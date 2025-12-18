import os
import imaplib
import email
import datetime
import requests
from bs4 import BeautifulSoup
import deepl
from email.header import decode_header
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("../.env")

# Configuration
IMAP_SERVER = "imap.gmail.com"
EMAIL_USER = os.environ.get("GMAIL_USER")
EMAIL_PASS = os.environ.get("GMAIL_PASS")
DEEPL_API_KEY = os.environ.get("DEEPL_API_KEY")
OUTPUT_DIR = "../updates"

def connect_gmail():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    return mail

def get_latest_newsletter(mail):
    mail.select("inbox")
    # Search for Medium Daily Digest
    # Adjust search criteria as needed
    status, messages = mail.search(None, '(FROM "noreply@medium.com" SUBJECT "Medium Daily Digest")')
    
    if status != "OK" or not messages[0]:
        print("No newsletter found.")
        return None

    latest_email_id = messages[0].split()[-1]
    status, msg_data = mail.fetch(latest_email_id, "(RFC822)")
    
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            return msg
    return None

from urllib.parse import urlparse

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
                    
                    # Medium newsletter links typically contain source=email and digest.reader
                    if "medium.com" in href and "digest.reader" in href:
                        # Parse URL to check structure
                        parsed = urlparse(href)
                        path_segments = [s for s in parsed.path.split('/') if s]
                        
                        # Articles usually have at least 2 segments: /@user/title-id or /publication/title-id
                        # Profiles/Publications usually have 1: /@user or /publication
                        # Filter out 'me/' (settings, profile), 'help.medium.com', and 'jobs-at-medium'
                        if len(path_segments) >= 2 and "me/" not in href and "help.medium.com" not in href and "jobs-at-medium" not in href:
                            links.append(href)
    return list(set(links)) # Deduplicate

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
        # Disable SSL verification if using a proxy that intercepts SSL (common with some scraping proxies)
        # or ensure certificates are correct. For now, we'll keep verify=True unless issues arise.
    
    try:
        response = requests.get(url, headers=headers, proxies=proxies, timeout=30) # Increased timeout for proxy
        if response.status_code != 200:
            print(f"Failed to fetch {url}: Status {response.status_code}")
            return None
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract Metadata
        og_title = soup.find("meta", property="og:title")
        title = og_title["content"] if og_title else (soup.title.string if soup.title else "No Title")
        
        og_desc = soup.find("meta", property="og:description")
        description = og_desc["content"] if og_desc else ""
        
        og_image = soup.find("meta", property="og:image")
        image_url = og_image["content"] if og_image else "https://placehold.co/600x400"
        
        author_meta = soup.find("meta", attrs={"name": "author"})
        author = author_meta["content"] if author_meta else "Unknown Author"
        
        # Try to find reading time (often in text like "5 min read")
        reading_time = "5 min read" # Default
        reading_time_element = soup.find(string=lambda text: text and "min read" in text)
        if reading_time_element:
            reading_time = reading_time_element.strip()
        
        # Tags - Try article:tag first, then keywords
        tags = []
        article_tags = soup.find_all("meta", property="article:tag")
        if article_tags:
            tags = [t["content"] for t in article_tags]
        
        if not tags:
            keywords_meta = soup.find("meta", attrs={"name": "keywords"})
            if keywords_meta:
                tags = keywords_meta["content"].split(",")
        
        tags = [t.strip() for t in tags if t.strip()]
        
        # Fallback: Extract keywords from title if no tags found
        if not tags:
            common_words = {"the", "a", "an", "in", "on", "at", "for", "to", "of", "and", "or", "with", "by", "is", "are", "was", "were", "be", "been", "how", "what", "why", "when", "where", "who", "which", "vs", "versus", "compare", "comparison", "guide", "tutorial", "best", "top", "review", "introduction", "intro"}
            words = title.replace(":", "").replace("-", "").split()
            tags = [w for w in words if w.lower() not in common_words and len(w) > 3]
            tags = tags[:5] # Limit to 5 tags
            
        if not tags:
            tags = ["Newsletter"]
        
        # Translate summary if we have one
        summary = description
        if DEEPL_API_KEY and summary:
            try:
                translator = deepl.Translator(DEEPL_API_KEY)
                result = translator.translate_text(summary, target_lang="FR")
                summary = result.text
            except Exception as e:
                print(f"DeepL Translation Error: {e}")
        
        return {
            "title": title,
            "author": author,
            "summary": summary,
            "tags": tags,
            "reading_time": reading_time,
            "image_url": image_url,
            "url": url # Add the URL to the returned dictionary
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def translate_summary(text):
    return text

def generate_sql(articles, target_date):
    filename = f"medium-{target_date.strftime('%Y-%m-%d')}.sql"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, "w") as f:
        # Add DELETE statement to clear existing data for this date
        # This ensures we remove any "phantom" articles from previous runs
        f.write(f"DELETE FROM articles WHERE publication_date = '{target_date.strftime('%Y-%m-%d')}';\n\n")
        
        for article in articles:
            # Escape single quotes for SQL
            title = article['title'].replace("'", "''")
            summary = article['summary'].replace("'", "''")
            author = article['author'].replace("'", "''")
            tags_str = "{" + ",".join([f'"{t}"' for t in article['tags']]) + "}"
            
            # Define variables for direct use in f-string, escaping if necessary
            url = article['url'].replace("'", "''")
            publication_date = article['publication_date'].replace("'", "''")
            image_url = article['image_url'].replace("'", "''")
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

import sys

def get_newsletter_by_date(mail, target_date):
    mail.select("inbox")
    # Format date for IMAP search (e.g., "10-Nov-2025")
    date_str = target_date.strftime("%d-%b-%Y")
    
    # Search for emails from Medium on the specific date
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

def main():
    if not EMAIL_USER or not EMAIL_PASS:
        print("Please set GMAIL_USER and GMAIL_PASS environment variables.")
        return

    # Parse date argument or use today
    if len(sys.argv) > 1:
        try:
            target_date = datetime.datetime.strptime(sys.argv[1], "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            return
    else:
        target_date = datetime.date.today()

    print(f"Connecting to Gmail to find newsletter for {target_date}...")
    try:
        mail = connect_gmail()
        msg = get_newsletter_by_date(mail, target_date)
        if msg:
            print(f"Newsletter found for {target_date}.")
            print(f"Subject: {msg['subject']}")
            links = extract_links(msg)
            print(f"Found {len(links)} links.")
            
            articles = []
            for link in links: # Process all links
                print(f"Scraping {link}...")
                article = scrape_article(link)
                if article:
                    # Check if image_url is valid (not None, empty, or placeholder)
                    # AND check if author is known.
                    # User request: "n'inclure ... que des articles ayant une image ou dont l'auteur est connu"
                    # This implies: Keep if (Image Valid) OR (Author Known).
                    # So we only exclude if (Image Invalid) AND (Author Unknown).
                    
                    is_author_unknown = article['author'] == "Unknown Author"
                    is_image_invalid = not article['image_url'] or "placehold.co" in article['image_url']

                    if is_author_unknown and is_image_invalid:
                        print(f"Skipping phantom article (Unknown Author AND No Image): {article['title']}")
                        continue

                    # Filter out specific titles
                    if article['title'] in ["Work at Medium", "Medium Help Center"]:
                        print(f"Skipping system article: {article['title']}")
                        continue

                    # article['summary'] is already translated in scrape_article
                    # Use the target date for the SQL file
                    article['publication_date'] = target_date.isoformat() 
                    articles.append(article)
            
            generate_sql(articles, target_date)
        else:
            print(f"No newsletter found for {target_date} from noreply@medium.com.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
