import requests
from bs4 import BeautifulSoup

url = "https://medium.com/@bbangjoa/chatgpt-codex-vs-claude-code-strengths-weaknesses-and-how-to-choose-4d4468c2050b"
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string if soup.title else "No title"
        print(f"Title: {title}")
        
        og_title = soup.find("meta", property="og:title")
        if og_title:
            print(f"OG Title: {og_title['content']}")
            
        og_desc = soup.find("meta", property="og:description")
        if og_desc:
            print(f"OG Description: {og_desc['content']}")
            
        author = soup.find("meta", attrs={"name": "author"})
        if author:
            print(f"Author: {author['content']}")
            
        og_image = soup.find("meta", property="og:image")
        if og_image:
            print(f"OG Image: {og_image['content']}")

        article_tags = soup.find_all("meta", property="article:tag")
        if article_tags:
            print(f"Article Tags: {[t['content'] for t in article_tags]}")
        else:
            print("No article:tag found")
            
        # Reading Time
        # Look for text containing "min read"
        reading_time_element = soup.find(string=lambda text: text and "min read" in text)
        if reading_time_element:
            print(f"Reading Time Found: {reading_time_element.strip()}")
        else:
            print("Reading Time Not Found")

        # Tags from links
        # Medium tags often have href starting with /tag/
        tag_links = soup.find_all("a", href=lambda href: href and "/tag/" in href)
        extracted_tags = []
        for link in tag_links:
            tag_text = link.get_text(strip=True)
            if tag_text and tag_text not in extracted_tags:
                extracted_tags.append(tag_text)
        
        print(f"Tags from links: {extracted_tags[:5]}")

    else:
        print("Failed to fetch page")

except Exception as e:
    print(f"Error: {e}")
