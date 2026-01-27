
import unittest

def extract_tags_logic(title, tags=None):
    if tags is None:
        tags = []
    
    # Fallback: Extract generic keywords from title if no tags found
    if not tags:
        common_words = {"the", "a", "an", "in", "on", "at", "for", "to", "of", "and", "or", "with", "by", "is", "are", "was", "were", "be", "been", "how", "what", "why", "when", "where", "who", "which", "vs", "versus", "compare", "comparison", "guide", "tutorial", "best", "top", "review", "introduction", "intro", "everything", "need", "know", "about", "using", "your", "more", "most", "some", "any"}
        # Replace common punctuation with space to split correctly
        clean_title = title.replace(":", " ").replace("-", " ").replace("(", " ").replace(")", " ").replace(",", " ").replace(".", " ").replace("?", " ").replace("!", " ")
        words = clean_title.split()
        
        # Generic technical terms to prioritize
        tech_keywords = {"python", "java", "javascript", "react", "vue", "angular", "node", "express", "fastapi", "django", "flask", "ai", "ml", "llm", "gpt", "deep", "learning", "data", "science", "docker", "kubernetes", "cloud", "aws", "azure", "gcp", "sql", "postgresql", "mongodb", "redis", "devops", "security", "web", "mobile", "ios", "android", "startup", "business", "tech"}
        
        extracted = []
        for w in words:
            w_lower = w.lower()
            if w_lower in tech_keywords:
                extracted.append(w if w_lower in ["ai", "ml", "llm", "gpt", "aws", "gcp", "ios", "sql"] else w.capitalize())
            elif w_lower not in common_words and len(w) > 4:
                extracted.append(w.capitalize())
        
        # Deduplicate while preserving order and limit to 3 tags
        tags = []
        for t in extracted:
            if t not in tags:
                tags.append(t)
        tags = tags[:3]
        
    if not tags:
        tags = ["Tech"]
    return tags

class TestTagExtraction(unittest.TestCase):
    def test_generic_extraction(self):
        title = "Everything you need to know about Python and AI"
        tags = extract_tags_logic(title)
        self.assertEqual(tags, ["Python", "AI"])

    def test_tech_priority(self):
        title = "Running Kubernetes on AWS: A guide to Cloud"
        tags = extract_tags_logic(title)
        self.assertEqual(tags, ["Kubernetes", "AWS", "Cloud"])

    def test_long_words_fallback(self):
        title = "Beautiful Architecture in modern applications"
        tags = extract_tags_logic(title)
        self.assertEqual(tags, ["Beautiful", "Architecture", "Modern"])

    def test_limited_tags(self):
        title = "Python Javascript React Node Docker Kubernetes"
        tags = extract_tags_logic(title)
        self.assertEqual(len(tags), 3)

if __name__ == "__main__":
    unittest.main()
