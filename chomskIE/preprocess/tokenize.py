from abc import ABC, abstractmethod

from chomskIE.utils import validate_input, PipelineError
from chomskIE.preprocess.base import Preprocesser


class Tokenizer(Preprocesser, ABC):
    """An abstract base class for tokenization techniques such as
    sentence recognition and word tokenization.
    """
    @property
    @abstractmethod
    def name(self):
        """Key for preprocessing technique. It helps identify preprocessing
        step output in `chomskIE.utils.Document.sents`.
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
    def transform(self):
        """Apply the preprocessing technique of subclass to single document.
        """
        pass


class SentenceRecognizer(Tokenizer):
    """Pipeline component for sentence segmentation.

    Parameters:
        model (spacy.lang):
            Trained SpaCy language pipeline.

    Properties:
        name (str):
            Key to identify preprocessing step output in
            `chomskIE.utils.Document.sents`.  
    """
    def __init__(self, model):
        """Initializes :class: `SentenceRecognizer`.

        Arguments:
            model (spacy.lang):
                Trained SpaCy language pipeline.
        """
        self._name = 'sent'
        self.model = model
        self.model.add_pipe(self.model.create_pipe('sentencizer'))

    @property
    def name(self):
        return self._name

    def transform(self, doc):
        """Apply the preprocessing technique of subclass to single document.

        Arguments:
            doc (chomskIE.utils.Document):
                Document to apply preprocessing.

        Returns:
            doc (chomskIE.utils.Document):
                Processed document.
        """
        self._validate_input(doc, True)
        sents = list(self.model(doc.text).sents)

        if not doc.processed:
            doc_sents = [{} for _ in range(len(sents))]

        for index, sent in enumerate(sents):
            doc_sents[index][self.name] = str(sent)

        doc.sents = doc_sents
        return doc


class WordTokenizer(Tokenizer):
    """Pipeline component for word tokenization.

    Parameters:
        model (spacy.lang):
            Trained SpaCy language pipeline.

    Properties:
        name (str):
            Key to identify preprocessing step output in
            `chomskIE.utils.Document.sents`.  
    """
    def __init__(self, model):
        """Initializes :class: `WordTokenizer`.

        Arguments:
            model (spacy.lang):
                Trained SpaCy language pipeline.
        """
        self._name = 'tokens'
        self.model = model

    @property
    def name(self):
        return self._name

    def transform(self, doc):
        """Apply the preprocessing technique of subclass to single document.

        Arguments:
            doc (chomskIE.utils.Document):
                Document to apply preprocessing.

        Returns:
            doc (chomskIE.utils.Document):
                Processed document.
        """
        self._validate_input(doc, True)
        doc_sents = doc.sents

        for index, doc_sent in enumerate(doc_sents):
            if 'sent' in doc_sent:
                sent = doc_sent['sent']
            else:
                error_msg = 'Sequence of pre-processing steps is incorrect.'
                raise PipelineError(error_msg)
            tokens = [token.text for token in self.model(sent)]
            doc_sents[index][self.name] = tokens

        doc.sents = doc_sents
        return doc
