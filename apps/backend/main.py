from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional
from apps.backend.core.traverser import Traverser
from apps.backend.core.extractor import Extractor
from apps.backend.core.indexer import Indexer
from apps.backend.core.storage import Storage

app = FastAPI(title="File Indexer")

storage = Storage("index.json")

class IndexRequest(BaseModel):
    directory: str = "test_data"
    ignore_list: Optional[list[str]] = [".git", "__pycache__"]

@app.post("/index")
def create_index(req: IndexRequest):
    traverser = Traverser(req.directory, ignore_list=req.ignore_list)
    extractor = Extractor()
    indexer = Indexer(traverser, extractor)
    index_data = indexer.build_index()
    storage.save(index_data)
    return {"message": "Index created successfully", "indexed_files_count": len(index_data)}

@app.get("/index")
def get_index():
    return storage.load()

@app.get("/search")
def search_index(q: str = Query(..., description="Search query")):
    index_data = storage.load()
    results = {}
    for path, meta in index_data.items():
        if q.lower() in path.lower():
            results[path] = meta
    return {"query": q, "results": results}
