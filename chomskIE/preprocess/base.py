from abc import ABC, abstractmethod


class Preprocesser(ABC):
    """An abstract base class for all preprocessing techniques.
    """
    @property
    @abstractmethod
    def name(self):
        """Key for preprocessing technique. Helps identify preprocessing
        technique output in `chomskIE.utils.Document.sents`.
        """
        pass

    @abstractmethod
    def __call__(self):
        """Apply the preprocessing technique of subclass to a stream
        of documents.
        """
        pass

    @abstractmethod
    def _validate_input(self):
        """Check whether the format of input matches that expected
        by the subclass' `__call__` and `transform` methods.
        """
        pass

    @abstractmethod
    def transform(self):
        """Apply the preprocessing technique of subclass to single document.
        """
        pass
