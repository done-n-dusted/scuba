class Traverser:
    """Traverse directories and yield file paths.

    Example:
        traverser = Traverser()
        for path in traverser.iterate("/some/dir"):
            print(path)
    """

    def __init__(self, follow_symlinks: bool = False):
        self.follow_symlinks = follow_symlinks

    def iterate(self, root_path: str):
        """Yield file paths under ``root_path``.

        Parameters
        ----------
        root_path: str
            The directory to start traversal from.
        """
        import os
        for dirpath, _, filenames in os.walk(root_path, followlinks=self.follow_symlinks):
            for filename in filenames:
                yield os.path.join(dirpath, filename)
