# Architecture - Medium Datligent

This document describes the architecture of the **Medium Datligent** project using a Mermaid diagram.

## Architecture Diagram

```mermaid
graph TD
    subgraph "External Services"
        Gmail["Gmail API (Medium Newsletters)"]
        LLM["Docker Model Runner (gemma3)"]
        MCP["Gateway (DuckDuckGo)"]
    end

    subgraph "Docker Stack (medium-network)"
        Frontend["Frontend (UI)"]
        Backend["Backend (FastAPI)"]
        DB[("PostgreSQL DB (medium_db)")]
        Ingestor["Ingestor (Scheduler)"]
        DBUpdater["DB Updater"]
    end

    Gmail -->|Fetch| Ingestor
    Ingestor -->|Agentic Processing| LLM
    Ingestor -->|Search| MCP
    Ingestor -->|Generate SQL| Updates["/updates (SQL Files)"]
    
    Updates -->|Read| DBUpdater
    DBUpdater -->|Execute SQL| DB
    
    Frontend -->|Requests| Backend
    Backend -->|Query| DB
```

## Application Logic Flow (Ingestion)

*Voir aussi : [ingest_standardized.mermaid](file:///Users/adminmac/medium-datligent/ingestion/ingest_standardized.mermaid)*

The following diagram illustrates the internal logic of the `ingestor` service for Medium newsletters.

```mermaid
sequenceDiagram
    participant S as ingest_standardized.py
    participant G as Gmail API
    participant Sc as Scraper
    participant L as LLM (gemma3)
    participant U as updates/ (SQL)

    S->>G: Search for Medium Daily Digest (ON target_date)
    G-->>S: Return matching emails
    S->>S: Extract Medium article links
    loop For each Medium link
        S->>Sc: Scrape article content
        Sc-->>S: Return text, author, image
        S->>L: Request French summary + tags
        L-->>S: Return JSON metadata
    end
    S->>U: Generate and save .sql file
```

## Component Roles

- **Frontend**: User interface for exploring Medium articles.
- **Backend**: API serving article content and metadata.
- **DB (PostgreSQL)**: Stores Medium articles, summaries, and tags.
- **Ingestor**: Scheduled task that fetches Medium newsletters, uses gemma3 for French summaries, and outputs SQL.
- **DB Updater**: Watches for new SQL updates and applies them to the database.
- **LLM**: Local instance of gemma3 powering the metadata extraction.
