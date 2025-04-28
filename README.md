# Inventory Search Engine

A full-stack inventory search engine that combines semantic search using FAISS with geolocation filtering using PostgreSQL and PostGIS.

## Features

- Semantic search using FAISS and sentence-transformers
- Geolocation-based filtering using PostGIS
- FastAPI REST API
- Dockerized deployment
- Batch product ingestion
- Vector similarity search

## Prerequisites

- Docker and Docker Compose
- Python 3.11+
- PostgreSQL with PostGIS extension

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd inventory-search-engine
```

2. Create and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Build and start the services:
```bash
docker-compose up --build
```

4. Ingest sample data:
```bash
docker-compose exec app python scripts/ingest_products.py
```

## API Usage

### Search Endpoint

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "lightweight waterproof hoodie",
    "lat": 12.9716,
    "lon": 77.5946,
    "radius_km": 10,
    "max_results": 10
  }'
```

## Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI application
│   ├── routers/             # API routes
│   ├── db/                  # Database models and configuration
│   └── services/            # Business logic services
├── scripts/
│   ├── ingest_products.py   # Data ingestion script
│   └── build_faiss_index.py # FAISS index building script
├── sample_data/             # Sample product data
├── faiss_index/             # FAISS index storage
├── tests/                   # Unit tests
├── docker-compose.yml       # Docker configuration
├── Dockerfile               # Application Dockerfile
└── requirements.txt         # Python dependencies
```

## Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run tests:
```bash
pytest
```

## License

MIT License 