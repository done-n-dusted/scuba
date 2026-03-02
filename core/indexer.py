class Indexer:
    """Build an index of files using Traverser and Extractor.

    Example:
        from core.traverser import Traverser
        from core.extractor import Extractor
        from core.indexer import Indexer

        traverser = Traverser()
        extractor = Extractor()
        indexer = Indexer(traverser, extractor)
        index = indexer.build_index("/some/dir")
    """

    def __init__(self, traverser, extractor):
        self.traverser = traverser
        self.extractor = extractor
        self.index = {}

    def build_index(self, root_path: str):
        """Traverse ``root_path`` and extract metadata for each file.

        Returns a dictionary mapping file paths to metadata dictionaries.
        """
        for file_path in self.traverser.iterate(root_path):
            meta = self.extractor.extract(file_path)
            self.index[file_path] = meta
        return self.index
