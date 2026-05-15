# Deterministic News Information Retrieval System

A high-performance news article retrieval and recommendation system utilizing classical Information Retrieval (IR) principles without relying on machine learning, semantic search, or vector databases.

## Technology Stack
- **Framework**: FastAPI (Async)
- **Database**: PostgreSQL with SQLAlchemy
- **Background Tasks**: TaskIQ
- **Caching / Broker**: Redis
- **NLP**: spaCy, BeautifulSoup4

## Architecture

This system is built upon four dedicated service agents:

1.  **Data Architect**: Implements PostgreSQL GIN indexing on `tsvector` columns for ultra-fast full-text keyword lookups.
2.  **Ingestion Engineer**: Uses TaskIQ and Redis to asynchronously fetch RSS feeds, normalize HTML, remove stop-words with `spaCy`, and perform strict URL-hash deduplication.
3.  **Retrieval Specialist**: Executes complex SQL queries returning BM25-style relevance scores combined with a recency decay function.
4.  **Recommendation Engine**: Uses "Common Keyword Overlap" within article categories using `ts_stat` to recommend similar articles deterministically.

---

## Deterministic Ranking Formula

The ranking system is explicitly designed to be deterministic, relying entirely on term frequency and recency.

### 1. Base Relevance Score
The core of the retrieval relies on PostgreSQL's `ts_rank_cd` (Cover Density ranking). This function computes a relevance score based on how frequently the queried terms appear in the document's `tsvector` and how closely they are positioned together. 

*   Title is weighted as `A` (highest priority).
*   Body is weighted as `B`.

### 2. Recency Decay Function
To prioritize fresh news, the base relevance score is multiplied by an **Exponential Decay Function**:

```text
Final_Score = ts_rank_cd * EXP( -decay_rate * (Days_Since_Publication) )
```

*   **`decay_rate`**: A tunable parameter (default `0.1`). A higher value penalizes older articles more aggressively.
*   **`Days_Since_Publication`**: Calculated via `extract(epoch from (now() - published_at))/86400`.

This ensures that a highly relevant but old article will eventually be outranked by a slightly less relevant but newly published article.

---

## Getting Started

1.  **Start Services**:
    ```bash
    docker-compose up -d
    ```
2.  **Install Dependencies**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    python -m spacy download en_core_web_sm
    ```
3.  **Run Migrations / Setup DB**:
    *The app auto-creates tables on startup.*
4.  **Start FastAPI**:
    ```bash
    uvicorn app.main:app --reload
    ```

### Running the Benchmark

We provide a script to seed the database with 10,000 mock articles and benchmark the `/search` endpoint latency to ensure it meets the <100ms requirement.

```bash
python scripts/seed_mock_data.py
python scripts/benchmark.py
```
