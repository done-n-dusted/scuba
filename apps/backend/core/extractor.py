class Extractor:
    """Extract metadata from a file path.

    Example:
        extractor = Extractor()
        meta = extractor.extract("/path/to/file.txt")
    """

    def extract(self, file_path: str) -> dict:
        """Return a dictionary with basic file metadata.

        Parameters
        ----------
        file_path: str
            Path to the file.
        """
        import os
        import mimetypes
        try:
            stat = os.stat(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            _, ext = os.path.splitext(file_path)
            return {
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "created": stat.st_ctime,
                "path": file_path,
                "mime_type": mime_type,
                "extension": ext
            }
        except OSError as e:
            return {"path": file_path, "error": str(e)}
