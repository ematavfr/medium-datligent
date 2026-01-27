import os
import imaplib
import email
import datetime
import requests
import sys
import json
import asyncio
from bs4 import BeautifulSoup
from email.header import decode_header
from dotenv import load_dotenv
from urllib.parse import urlparse
from langchain_openai import ChatOpenAI

# Load environment variables
if os.path.exists(".env"):
    load_dotenv(".env")
elif os.path.exists("../.env"):
    load_dotenv("../.env")
else:
    load_dotenv()

# Configuration
IMAP_SERVER = "imap.gmail.com"
EMAIL_USER = os.environ.get("GMAIL_USER", "").strip('"')
EMAIL_PASS = os.environ.get("GMAIL_PASS", "").strip('"')
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "updates"))

# Standardized LLM / MCP Config
MODEL_NAME = os.environ.get("MODEL_NAME", "ai/gemma3").strip('"')
BASE_URL = os.environ.get("BASE_URL", "http://model-runner.docker.internal/engines/llama.cpp/v1").strip('"')

# Initialize LLM (Docker Model Runner)
llm = ChatOpenAI(
    model=MODEL_NAME,
    api_key="nope", # Required by LangChain but not by model-runner
    base_url=BASE_URL,
)

def connect_gmail():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    return mail

def get_newsletter_by_date(mail, target_date):
    mail.select("inbox")
    date_str = target_date.strftime("%d-%b-%Y")
    search_criteria = f'(FROM "noreply@medium.com" ON "{date_str}")'
    print(f"Searching with criteria: {search_criteria}")
    
    status, messages = mail.search(None, search_criteria)
    if status != "OK" or not messages[0]:
        return None

    latest_email_id = messages[0].split()[-1]
    status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
    
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            return msg
    return None

def extract_links(msg):
    links = []
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                try:
                    html_content = part.get_payload(decode=True).decode()
                except Exception as e:
                    print(f"Error decoding HTML: {e}")
                    continue
                
                soup = BeautifulSoup(html_content, "html.parser")
                for a in soup.find_all('a', href=True):
                    href = a['href']
                    if "medium.com" in href and "digest.reader" in href:
                        parsed = urlparse(href)
                        path_segments = [s for s in parsed.path.split('/') if s]
                        if len(path_segments) >= 2 and "me/" not in href and "help.medium.com" not in href and "jobs-at-medium" not in href:
                            links.append(href)
    return list(set(links))

def scrape_article(url):
    print(f"Scraping {url}...")
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Referer": "https://medium.com/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Upgrade-Insecure-Requests": "1"
    }
    
    # Proxy Configuration
    BRIGHT_DATA_PROXY_URL = os.environ.get("BRIGHT_DATA_PROXY_URL")
    proxies = {}
    if BRIGHT_DATA_PROXY_URL:
        proxies = {
            "http": BRIGHT_DATA_PROXY_URL,
            "https": BRIGHT_DATA_PROXY_URL
        }
    
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=30)
        if response.status_code != 200:
            print(f"Failed to fetch {url}: Status {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract Metadata
        og_title = soup.find("meta", property="og:title")
        title = og_title["content"] if og_title else (soup.title.string if soup.title else "No Title")
        
        # Extract Body Text for LLM
        content_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'li'])
        body_text = " ".join([elem.get_text() for elem in content_elements])
        
        og_image = soup.find("meta", property="og:image")
        image_url = og_image["content"] if og_image else None
        
        author_meta = soup.find("meta", attrs={"name": "author"})
        author = author_meta["content"] if author_meta else "Unknown Author"
        
        reading_time = "5 min read"
        reading_time_element = soup.find(string=lambda text: text and "min read" in text)
        if reading_time_element:
            reading_time = reading_time_element.strip()
            
        return {
            "title": title,
            "author": author,
            "body_text": body_text,
            "image_url": image_url,
            "url": url,
            "reading_time": reading_time
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

async def pre_warm_model():
    """Wait for the model to be loaded and ready."""
    print(f"Waiting for model {MODEL_NAME} to be ready...")
    max_prewarm_attempts = 30 # Up to 5 minutes
    for i in range(max_prewarm_attempts):
        try:
            # Simple prompt to check readiness
            llm.invoke("Hi")
            print("Model is ready.")
            return True
        except Exception as e:
            print(f"Model not ready yet (attempt {i+1}/{max_prewarm_attempts}): {e}")
            await asyncio.sleep(10)
    return False

async def agentic_metadata_extraction(title, raw_content):
    """Uses LLM to generate summary and tags in a standardized way."""
    prompt = f"""
    Basé sur le titre "{title}" et le contenu suivant de l'article, génère :
    1. Un résumé en français de maximum 3 lignes.
    2. Une liste de 3 à 5 tags pertinents (en anglais technique uniquement).

    Contenu : {raw_content[:4000]}
    
    Réponds uniquement au format JSON : {{"summary": "...", "tags": ["tag1", "tag2"]}}
    """
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = llm.invoke(prompt)
            raw_response = response.content.strip()
            # Clean potential markdown backticks
            if raw_response.startswith("```json"):
                raw_response = raw_response[7:-3].strip()
            elif raw_response.startswith("```"):
                raw_response = raw_response[3:-3].strip()
                
            data = json.loads(raw_response)
            return data.get("summary"), data.get("tags")
        except Exception as e:
            print(f"LLM Extraction error (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(5 * (attempt + 1)) # Wait longer each time
            else:
                return "Résumé non disponible", ["Tech"]

def generate_sql(articles, target_date):
    filename = f"medium-{target_date.strftime('%Y-%m-%d')}.sql"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    with open(filepath, "w") as f:
        f.write(f"DELETE FROM articles WHERE publication_date = '{target_date.strftime('%Y-%m-%d')}';\n\n")
        
        for article in articles:
            title = article['title'].replace("'", "''")
            summary = article['summary'].replace("'", "''")
            author = article['author'].replace("'", "''")
            tags = article.get('tags', ["Tech"])
            tags_str = "{" + ",".join(['"' + t.replace("'", "''") + '"' for t in tags]) + "}"
            url = article['url'].replace("'", "''")
            publication_date = article['publication_date'].replace("'", "''")
            image_url = (article['image_url'] or "").replace("'", "''")
            reading_time = article['reading_time'].replace("'", "''")

            sql = f"""
            INSERT INTO articles (title, url, author, publication_date, image_url, summary, tags, reading_time)
            VALUES ('{title}', '{url}', '{author}', '{publication_date}', '{image_url}', '{summary}', '{tags_str}', '{reading_time}')
            ON CONFLICT (url) DO UPDATE SET
                title = EXCLUDED.title,
                author = EXCLUDED.author,
                publication_date = EXCLUDED.publication_date,
                image_url = EXCLUDED.image_url,
                summary = EXCLUDED.summary,
                tags = EXCLUDED.tags,
                reading_time = EXCLUDED.reading_time;
            """
            f.write(sql + "\n")
            
    print(f"Generated {filepath}")

async def run_standardized_ingestion(target_date=None):
    if not EMAIL_USER or not EMAIL_PASS:
        print("Please set GMAIL_USER and GMAIL_PASS environment variables.")
        return

    if not target_date:
        target_date = datetime.date.today()

    print(f"Connecting to Gmail for {target_date}...")
    try:
        mail = connect_gmail()
        msg = get_newsletter_by_date(mail, target_date)
        if msg:
            print(f"Newsletter found. Subject: {msg['subject']}")
            links = extract_links(msg)
            print(f"Found {len(links)} links.")
            
            # Pre-warm the model before starting
            if not await pre_warm_model():
                print("Model failed to warm up. Exiting.")
                return

            articles = []
            for link in links:
                article = scrape_article(link)
                if article:
                    # Filter phantom articles (no image AND unknown author)
                    if article['author'] == "Unknown Author" and not article['image_url']:
                        print(f"Skipping phantom: {article['title']}")
                        continue
                        
                    # Filter system articles
                    if article['title'] in ["Work at Medium", "Medium Help Center"]:
                        continue

                    # Agentic extraction
                    print(f"Extracting agentic metadata for: {article['title']}...")
                    summary, tags = await agentic_metadata_extraction(article['title'], article['body_text'])
                    article['summary'] = summary
                    article['tags'] = tags
                    article['publication_date'] = target_date.isoformat() 
                    articles.append(article)
                    
                    # Small throttle
                    await asyncio.sleep(2)
            
            generate_sql(articles, target_date)
        else:
            print(f"No newsletter found for {target_date}.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    target = None
    if len(sys.argv) > 1:
        try:
            target = datetime.datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            sys.exit(1)
            
    asyncio.run(run_standardized_ingestion(target))
