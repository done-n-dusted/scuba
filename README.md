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
│   │   ├── main.py
│   │   └── pyproject.toml
│   └── frontend/
│       ├── tests/
│       └── index.html
├── test_data/
│   ├── folder1/
│   │   └── file2.json
│   ├── file1.txt
│   └── script.py
├── Makefile
└── README.md
```

## Setup & Execution

We use a `Makefile` at the root directory to orchestrate setting up and running the project.

**To see all available commands:**
```bash
make help
```

**To install dependencies for both apps:**
```bash
make setup
```

**To start the application servers:**
```bash
make start
```
*(You can also use `make start-backend` and `make start-frontend` individually).*

## API Endpoints

Once the backend server is running, you can access the following endpoints:

- `POST /index`: Triggers the indexer to traverse the directory (default `test_data`) and save the index to `index.json`.
- `GET /index`: Retrieves the complete built index.
- `GET /search?q={query}`: Searches the index for files matching the given query string.

## Core Component Usage

You can still use the core components independently of the FastAPI server by importing them:

```python
from core.traverser import Traverser
from core.extractor import Extractor
from core.indexer import Indexer
from core.storage import Storage

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
