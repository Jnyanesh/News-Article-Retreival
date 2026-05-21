# NewsLens: Deterministic News Information Retrieval System

A high-performance news article retrieval and recommendation system utilizing classical Information Retrieval (IR) principles—without relying on machine learning, semantic search, or vector databases.

## 🚀 New Features

- **Premium Web UI**: Includes a beautiful, responsive, dark-mode focused frontend powered by vanilla HTML/CSS/JS with smooth glassmorphism aesthetics.
- **Real-Time Universal Fetching**: The search engine is no longer limited to a static database! Whenever you perform a search, the system dynamically intercepts the query, pulls the absolute latest articles from **Google News RSS**, ingests them into the database instantly, and serves them. Every query is guaranteed to return real-world breaking news.
- **Optimized Search Logic**: The search backend intelligently processes multi-word queries to allow partial matching (`OR`), preventing strict failures while still ranking perfect exact matches at the top.
- **One-Click Recommendations**: The recommendation system is now fully wired into the UI. Click "Find Similar Articles" on any result to immediately discover related news.

---

## 🛠️ Technology Stack
- **Framework**: FastAPI (Async)
- **Database**: PostgreSQL with SQLAlchemy 2.0 (`asyncpg`)
- **Background Tasks**: TaskIQ
- **Caching / Broker**: Redis
- **NLP**: spaCy, BeautifulSoup4
- **Frontend**: Vanilla HTML / CSS / JS

---

## 🏗️ Architecture

This system is built upon four dedicated service agents:

1. **Data Architect**: Implements PostgreSQL GIN indexing on `tsvector` columns for ultra-fast full-text keyword lookups.
2. **Ingestion Engineer**: Asynchronously fetches RSS feeds (both on a schedule via TaskIQ and dynamically on-the-fly during search), normalizes HTML, removes stop-words, and performs strict URL-hash deduplication.
3. **Retrieval Specialist**: Executes complex SQL queries returning BM25-style relevance scores combined with a recency decay function.
4. **Recommendation Engine**: Uses "Common Keyword Overlap" within article categories using PostgreSQL's `ts_stat` to recommend similar articles deterministically.

---

## 🧮 Deterministic Ranking Formula

The ranking system relies entirely on term frequency and recency.

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

## 🏁 Getting Started

1.  **Start Services** (Database & Redis):
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
3.  **Start the API & Web Server**:
    ```bash
    source .venv/bin/activate
    uvicorn app.main:app --reload
    ```
    *Open your browser and navigate to `http://127.0.0.1:8000/` to view the NewsLens UI!*

4. **(Optional) Run Background Workers for Automated Polling**:
   Open a second terminal to run the background ingestion worker:
   ```bash
   source .venv/bin/activate
   taskiq worker app.worker:broker
   ```
   Open a third terminal to run the 15-minute scheduler:
   ```bash
   source .venv/bin/activate
   taskiq scheduler app.worker:scheduler
   ```

### Running the Benchmark

We provide a script to seed the database with mock articles and benchmark the `/search` endpoint latency to ensure it meets strict performance requirements.

```bash
python scripts/seed_mock_data.py
python scripts/benchmark.py
```
