from abc import ABC, abstractmethod

from chomskIE.utils import validate_input


class Preprocessor(ABC):
    """An abstract base class for all preprocessing techniques.
    """
    @property
    @abstractmethod
    def name(self):
        """Key for preprocessing technique. Helps identify preprocessing
        technique output in `chomskIE.utils.Document.sents`.
        """
        pass

    def __call__(self, docs):
        """Apply the preprocessing technique of subclass to a stream
        of documents.

        Arguments:
            docs (list of chomskIE.utils.Document)
                Stream of documents

        Returns:
            processed_docs (list of chomskIE.utils.Document)
                Stream of processed documents.
        """
        self._validate_input(docs, False)
        processed_docs = [self.transform(doc) for doc in docs]
        return processed_docs

    def _validate_input(self, input, transform):
        """Check whether the format of input matches that expected
        by the subclass' `__call__` and `transform` methods.

        Arguments:
            input (list or chomskie.utils.Document):
                Input for preprocessing technique.
            transform (bool):
                If False, input is validated for stream of documents.
                If True, input is validated for single document.

        Returns:
            is_valid (bool):
                True, if preprocessing input is valid. False, otherwise.
        """
        is_valid = validate_input(pipe=self.__class__.__name__,
                                  input=input,
                                  transform=transform)
        return is_valid

    @abstractmethod
    def transform(self, doc):
        """Apply the preprocessing technique of subclass to single document.
        """
        pass
