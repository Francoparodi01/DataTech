# DataTech

DataTech is a price-intelligence pipeline for hardware products. It collects product snapshots, stores price history, computes historical price context, exposes a small web/API surface, and can trigger webhook alerts for unusually attractive prices.

## Architecture

```text
Collectors (Mercado Libre API / Amazon HTML fallback)
        ↓
ProductSnapshot normalization
        ↓
MongoDB historical storage
        ↓
Pricing analytics + Deal Score
        ↓
Dashboard / JSON API / webhook alerts
```

The repository is intentionally organized around one domain model so collectors, storage, analytics and the web app cannot silently drift into incompatible schemas.

## Security

No credentials belong in Git. Configure MongoDB and optional webhooks through environment variables. Copy `.env.example` to `.env` for local development.

> Important: an older revision of this repository contained a MongoDB credential in source code. That credential must be rotated/revoked in MongoDB Atlas even though the current tree no longer contains it. Git history should also be rewritten before treating the repository as fully remediated.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
pytest
```

With Docker:

```bash
docker compose up --build
```

The dashboard is served on `http://localhost:8000`.

## CLI

Collect Mercado Libre Argentina results:

```bash
datatech collect-meli --query "rtx 5070" --pages 2
```

Preview without MongoDB writes:

```bash
datatech collect-meli --query "rtx 5070" --dry-run
```

Collect Amazon US results using the HTML fallback collector:

```bash
datatech collect-amazon --query "rtx 5070" --pages 2
```

Run the development web server:

```bash
datatech serve
```

## Data model

Each observation is immutable and contains, at minimum:

- source
- source product ID
- title / normalized title
- price and currency
- product URL
- image URL when available
- seller ID when available
- capture timestamp

Repeated observations create a time series rather than overwriting the current price.

## Deal Score

The current Deal Score is a transparent heuristic, not a machine-learning model. It combines price discount versus 30/90-day medians and the current price percentile. Confidence increases with the number of historical observations. The score is designed to be inspectable and replaceable as the dataset matures.

## HTTP endpoints

- `GET /` dashboard
- `GET /health` service and database health
- `GET /api/products?source=mercadolibre&limit=100`
- `GET /api/deal/<source>/<product_id>` historical price context and Deal Score

## Development quality gates

GitHub Actions runs Ruff and pytest with coverage for every push and pull request.

## Production notes

For production, use a managed MongoDB instance, rotate all legacy credentials, keep `.env` out of Git, run the Flask application behind Gunicorn, and schedule collectors externally (cron, GitHub Actions, Cloud Run jobs, ECS tasks, etc.). Amazon's official Creators API should replace the HTML fallback when valid Associates/Creators credentials are available.
