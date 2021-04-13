from chomskIE.utils import PipelineError
from chomskIE.preprocess.base import Preprocesser


class SentenceRecognizer(Preprocesser):
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


class WordTokenizer(Preprocesser):
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
