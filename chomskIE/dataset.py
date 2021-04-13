from pathlib import Path

from chomskIE.utils import Document


class PathError(Exception):
    """Exception raised for invalid file/folder paths.
    """
    pass


class Loader:
    """Utility class to load .txt files and create corresponding :class:
    `chomskIE.utils.Document` objects.
    """
    def _validate_data_path(self, path, is_directory):
        """Checks if path to directory/file containing data is valid.

        Arguments:
            path (pathlib.Path):
                Path to file or directory.

            is_directory (bool):
                True, if path corresponds to that of a directory.
                False, otherwise.

        Returns:
            (bool):
                True, if `path` is a valid file or directory.
                False, otherwise.
        """
        cond = path.exists() if is_directory else path.is_file()

        if cond:
            return True
        return False

    def load_from_path(self, path):
        """Loads all .txt files from `path`.

        Arguments:
            path (pathlib.Path)

        Returns:
            docs (list of chomskIE.utils.Document objects)
                List of documents corresponding to .txt files in `path`.
        """
        if self._validate_data_path(path, is_directory=True):
            text_files = list(path.glob('*.txt'))
            docs = [self.load(text_file) for text_file in text_files]
            return docs
        else:
            raise PathError(f'{path} is not a valid data directory path.')

    def load(self, path_to_file):
        """Loads .txt file from `path_to_file`.

        Arguments:
            path_to_file (pathlib.Path):
                Path to .txt file

        Returns:
            doc (chomskIE.utils.Document)
                Document object corresponding to .txt file in `path_to_file`.
        """
        if self._validate_data_path(path_to_file, is_directory=False):
            with open(path_to_file, 'r', encoding='iso-8859-15') as text_obj:
                name = str(path_to_file).split('/')[-1]
                text = text_obj.read()
                doc = Document(name=name, text=text)
                return doc
        else:
            raise PathError(f'{path_to_file} is not a valid file path.')
