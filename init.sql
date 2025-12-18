CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    author TEXT,
    publication_date DATE,
    image_url TEXT,
    summary TEXT,
    tags TEXT[],
    reading_time TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
