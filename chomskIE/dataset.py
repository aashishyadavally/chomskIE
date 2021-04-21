from pathlib import Path
import ftfy
from itertools import chain

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

        return cond

    def load_from_path(self, path):
        """Loads all .txt files from `path`.

        Arguments:
            path (pathlib.Path)

        Returns:
            docs (list of chomskIE.utils.Document objects)
                List of documents corresponding to .txt files in `path`.
        """
        if not self._validate_data_path(path, is_directory=True):
            raise PathError(f'{path} is not a valid data directory path.')

        text_files = list(path.glob('*.txt'))
        docs = [self.load(text_file) for text_file in text_files]
        return docs
            

    def load(self, path_to_file):
        """Loads .txt file from `path_to_file`.

        Arguments:
            path_to_file (pathlib.Path):
                Path to .txt file

        Returns:
            doc (chomskIE.utils.Document)
                Document object corresponding to .txt file in `path_to_file`.
        """
        if not self._validate_data_path(path_to_file, is_directory=False):
            raise PathError(f'{path_to_file} is not a valid file path.')
            
        try:
            text_obj = open(path_to_file, 'r')
            text = text_obj.read()
        except UnicodeDecodeError:
            text_obj = open(path_to_file, 'rb')
            text, _ = ftfy.guess_bytes(text_obj.read())
        
        text = ftfy.ftfy(text)
        name = str(path_to_file).split('/')[-1]
        paragraphs = [p.strip() for p in text.splitlines() if p]

        doc = Document(name=name, text=text, paragraphs=paragraphs)
        return doc
