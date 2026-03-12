class Indexer:
    """Build an index of files using Traverser and Extractor.

    Example:
        from apps.backend.core.traverser import Traverser
        from apps.backend.core.extractor import Extractor
        from apps.backend.core.indexer import Indexer

        traverser = Traverser("/some/dir")
        extractor = Extractor()
        indexer = Indexer(traverser, extractor)
        index = indexer.build_index()
    """

    def __init__(self, traverser, extractor):
        self.traverser = traverser
        self.extractor = extractor
        self.index = {}

    def build_index(self):
        """Build the index using the configured traverser and extractor.

        Returns a dictionary mapping file paths to metadata dictionaries.
        """
        for file_path in self.traverser.iterate():
            meta = self.extractor.extract(file_path)
            self.index[file_path] = meta
        return self.index
