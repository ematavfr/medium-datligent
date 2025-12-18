from pydantic import BaseModel
from typing import List, Optional
from datetime import date

class Article(BaseModel):
    id: int
    title: str
    url: str
    author: Optional[str] = None
    publication_date: Optional[date] = None
    image_url: Optional[str] = None
    summary: Optional[str] = None
    tags: List[str] = []
    reading_time: Optional[str] = None
