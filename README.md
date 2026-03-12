# File Indexer

A Python file indexer project with core components for traversing directories, extracting file metadata, indexing, and storage. It now includes a FastAPI server (backend) and a placeholder for the frontend component.

## Project Structure

```text
file-indexer/
├── apps/
│   ├── backend/
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── traverser.py
│   │   │   ├── extractor.py
│   │   │   ├── indexer.py
│   │   │   └── storage.py
│   │   ├── tests/
│   │   └── main.py
│   └── frontend/
│       ├── tests/
│       └── index.html
├── test_data/
│   ├── folder1/
│   │   └── file2.json
│   ├── file1.txt
│   └── script.py
├── pyproject.toml
└── README.md
```

## Setup

Install the project dependencies and the FastAPI packages via Poetry:

```bash
poetry install
```

*(Note: Ensure you have `fastapi` and `uvicorn` included in your environment.)*

## Running the Server

Start the FastAPI backend server using Uvicorn:

```bash
poetry run uvicorn apps.backend.main:app --reload
```

## API Endpoints

Once the server is running, you can access the following endpoints:

- `POST /index`: Triggers the indexer to traverse the directory (default `test_data`) and save the index to `index.json`.
- `GET /index`: Retrieves the complete built index.
- `GET /search?q={query}`: Searches the index for files matching the given query string.

## Core Component Usage

You can still use the core components independently of the FastAPI server by importing from `apps.backend.core`:

```python
from apps.backend.core.traverser import Traverser
from apps.backend.core.extractor import Extractor
from apps.backend.core.indexer import Indexer
from apps.backend.core.storage import Storage

# Initialize components
traverser = Traverser("test_data")
extractor = Extractor()
indexer = Indexer(traverser, extractor)

# Build index
index_data = indexer.build_index()

# Save index to a JSON file
storage = Storage("index.json")
storage.save(index_data)
```
