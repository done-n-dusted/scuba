import os

class Traverser:
    """Traverse directories and yield file paths.

    Example:
        traverser = Traverser("/some/dir", ignore_list=[".git", "__pycache__"])
        for path in traverser.iterate():
            print(path)
    """

    def __init__(self, root_path: str, ignore_list: list[str] = None, follow_symlinks: bool = False):
        self.root_path = root_path
        self.ignore_list = ignore_list
        self.follow_symlinks = follow_symlinks

    def _should_ignore(self, path: str) -> bool:
        """Check if a path should be ignored."""
        if self.ignore_list is None:
            return False
        for ignore_pattern in self.ignore_list:
            if ignore_pattern in path:
                return True
        return False

    def iterate(self):
        """Yield file paths under ``root_path``."""
        for root, dirs, files in os.walk(self.root_path, topdown=True, followlinks=self.follow_symlinks):
            if self.ignore_list:
                dirs[:] = [d for d in dirs if d not in self.ignore_list]
                files = [f for f in files if f not in self.ignore_list]
                
            for filename in files:
                yield os.path.join(root, filename)