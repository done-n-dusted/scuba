import json
import os

class Storage:
    """JSON file storage for the file index."""

    def __init__(self, file_path: str = "index.json"):
        self.file_path = file_path
        self._store = {}
        self.load()

    def save(self, index: dict):
        """Save the provided index to disk."""
        self._store = index.copy()
        with open(self.file_path, "w") as f:
            json.dump(self._store, f, indent=2)

    def load(self) -> dict:
        """Return the stored index from disk."""
        if os.path.exists(self.file_path):
            with open(self.file_path, "r") as f:
                try:
                    self._store = json.load(f)
                except json.JSONDecodeError:
                    self._store = {}
        return self._store.copy()
