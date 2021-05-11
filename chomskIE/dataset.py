import json
import ftfy
from pathlib import Path
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


class Writer:
    """Utility class to write extracted relations to JSON file.
    """
    def _validate_data_path(self, path):
        """Checks if path to directory/file containing data is valid.

        Arguments:
            path (pathlib.Path):
                Path to file or directory.

        Returns:
            (bool):
                True, if `path` is a valid file or directory.
                False, otherwise.
        """
        if path.exists() or path.is_file():
            return True
        else:
            return False

    def _populate_arguments(self, template):
        """Populate templates with relevant arguments from relation.

        Arguments:
            template (namedtuple):
                Relation (for example, SVOTriple, PartTuple, etc.)

        Returns:
            args (list):
                Dictionary of relation arguments.
        """
        args = {}
        for _id, arg_id in enumerate(template._fields):
            if template[_id] is not None:
                args[f'{arg_id}'] = str(template[_id])
            else:
                args[f'{arg_id}'] = '_'
        return args

    def _populate_templates(self, doc, template_ids):
        """Extract relevant information to populate relation templates.

        Arguments:
            doc (chomskIE.utils.Document):
                Document.
            template_ids (list):
                Attribute identifier in ``chomskIE.util.Document``
                object to select corresponding relation templates.
        """
        populated = []

        for _id in template_ids:
            for sent in doc.sents:
                templates = sent[f'{_id}_templates']

                for template in templates:
                    _ext = {
                        'template': _id.upper(),
                        "sentences": sent['sent'],
                        "arguments": self._populate_arguments(template),
                    }
                    populated.append(_ext)
        return populated

    def write(self, path, docs, template_ids):
        """Writes extracted relations for corresponding templates
        to JSON files.

        Arguments:
            path (pathlib.Path):
                Output path.
            docs (list of chomskIE.utils.Document objects):
                List of documents for which extracted relations need
                to be written.
            template_ids (list):
                Attribute identifier in ``chomskIE.util.Document``
                object to select corresponding relation templates.
        """
        if not self._validate_data_path(path):
            path.mkdir()

        for doc in docs:
            output = {
                'document': doc.name,
                'extraction': self._populate_templates(doc, template_ids),
            }
            doc_name = doc.name.replace('.txt', '')
            output_file_path = Path(path) / f'{doc_name}.json'

            if output_file_path.exists():
                with open(output_file_path, 'r') as file:
                    file_data = json.load(file)
                    old = file_data['extraction']
                    old.extend(output['extraction'])
                    file_data['extraction'] = old

                with open(output_file_path, 'w+') as file:
                    json.dump(file_data, file, indent=4)
            else:
                with open(output_file_path, 'w+') as file:
                    json.dump(output, file, indent=4)


class DummyLoader(Loader):
    """Utility class to load .txt files as needed to extract BORN relations.
    """
    def load_from_path(self, english_model, path):
        """Loads all .txt files from `path`.

        Arguments:
            path (pathlib.Path)

        Returns:
            docs, spacy_docs (tuple)
                ``docs`` is list of ``chomskIE.utils.Document`` objects
                corresponding to .txt files in `path`.

                ``spacy_docs`` is list of ``spacy.tokens.Document`` objects
                corresponding to .txt files in `path` processed by
                ``english_model``.
        """
        if not self._validate_data_path(path, is_directory=True):
            raise PathError(f'{path} is not a valid data directory path.')

        text_files = list(path.glob('*.txt'))

        docs, spacy_docs = [], []

        for text_file in text_files:
            doc, spacy_doc = self.load(english_model, text_file)
            docs.append(doc)
            spacy_docs.append(spacy_doc)
        return docs, spacy_docs

    def load(self, english_model, path_to_file):
        """Loads .txt file from `path_to_file`.

        Arguments:
            english_model (spacy.lang)
                Trained SpaCy language pipeline.)
            path_to_file (pathlib.Path):
                Path to .txt file

        Returns:
            doc, spacy_doc (tuple)
                ``doc`` is a ``chomskIE.utils.Document`` object corresponding
                to .txt file in `path`.

                ``spacy_doc`` is a ``spacy.tokens.Document`` object corresponding
                to .txt files in `path` processed by ``english_model``.
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

        spacy_doc = english_model(text)
        doc = Document(name=name, text=None, paragraphs=None)

        return doc, spacy_doc


class DummyWriter(Writer):
    """Utility class to write extracted BORN relations to JSON file.
    """
    def _populate_templates(self, doc, template_ids):
        """Extract relevant information to populate relation templates.

        Arguments:
            doc (chomskIE.utils.Document):
                Document.
            template_ids (list):
                Attribute identifier in ``chomskIE.util.Document``
                object to select corresponding relation templates.
        """
        populated = []

        if 'born' in template_ids:
            _id = 'BORN'

        for sent in doc.sents:
            templates = sent[f'born_templates']
            for template in templates:
                _ext = {
                    'template': _id,
                    "sentences": str(sent['sent'].text),
                    "arguments": {
                        "arg1": str(template[0]),
                        "arg2": str(template[1]),
                        "arg3": str(template[2]),
                    },
                }
                populated.append(_ext)
        return populated
