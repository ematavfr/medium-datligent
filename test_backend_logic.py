
import unittest
from typing import List, Optional

def mock_get_db_connection():
    class MockCursor:
        def execute(self, query, params):
            self.query = query
            self.params = params
        def fetchall(self):
            return []
        def close(self):
            pass
    class MockConn:
        def cursor(self):
            return MockCursor()
        def close(self):
            pass
    return MockConn()

def get_articles_logic(tag: Optional[str] = None):
    query = "SELECT * FROM articles WHERE 1=1"
    params = []
    
    if tag:
        tags_list = [t.strip() for t in tag.split(',') if t.strip()]
        if tags_list:
            query += " AND tags && %s"
            params.append(tags_list)
    return query, params

class TestBackendSearch(unittest.TestCase):
    def test_single_tag(self):
        query, params = get_articles_logic("AI")
        self.assertIn("tags && %s", query)
        self.assertEqual(params, [["AI"]])

    def test_multiple_tags(self):
        query, params = get_articles_logic("AI, Python")
        self.assertIn("tags && %s", query)
        self.assertEqual(params, [["AI", "Python"]])

    def test_empty_tag(self):
        query, params = get_articles_logic("")
        self.assertNotIn("tags &&", query)
        self.assertEqual(params, [])

if __name__ == "__main__":
    unittest.main()
