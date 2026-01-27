from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from database import get_db_connection
from models import Article

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:6050",
        "http://127.0.0.1:6050",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Medium Article Explorer API"}

@app.get("/articles", response_model=List[Article])
def get_articles(
    date: Optional[str] = None,
    tag: Optional[str] = None,
    author: Optional[str] = None
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM articles WHERE 1=1"
    params = []
    
    if date:
        query += " AND publication_date = %s"
        params.append(date)
        
    if author:
        query += " AND author = %s"
        params.append(author)
        
    if tag:
        # Split tags by comma and clean them
        tags_list = [t.strip() for t in tag.split(',') if t.strip()]
        if tags_list:
            # Use && operator for 'OR' search between arrays (has elements in common)
            query += " AND tags && %s"
            params.append(tags_list)
        
    query += " ORDER BY publication_date DESC, id DESC"
    
    try:
        cursor.execute(query, params)
        articles = cursor.fetchall()
        return articles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@app.get("/filters")
def get_filters():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get unique dates
        cursor.execute("SELECT DISTINCT publication_date FROM articles ORDER BY publication_date DESC")
        dates = [row['publication_date'] for row in cursor.fetchall() if row['publication_date']]
        
        # Get all tags and count them (optional, but good for UI)
        # For simplicity, just get unique tags
        cursor.execute("SELECT DISTINCT unnest(tags) as tag FROM articles ORDER BY tag")
        tags = [row['tag'] for row in cursor.fetchall() if row['tag']]
        
        return {"dates": dates, "tags": tags}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
