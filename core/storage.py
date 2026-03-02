class Storage:
    """Simple in‑memory storage for the file index.

    This is a placeholder implementation that stores the index in a Python
    dictionary. In a real project you could replace this with a database or a
    more sophisticated persistence layer.
    """

    def __init__(self):
        self._store = {}

    def save(self, index: dict):
        """Save the provided index.

        Parameters
        ----------
        index: dict
            Mapping of file paths to metadata dictionaries.
        """
        self._store = index.copy()

    def load(self) -> dict:
        """Return the stored index (or an empty dict if nothing is saved)."""
        return self._store.copy()
