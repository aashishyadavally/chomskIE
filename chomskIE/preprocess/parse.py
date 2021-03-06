from chomskIE.utils import PipelineError
from chomskIE.preprocess.base import Preprocessor


class DependencyToken:
    def __init__(self, dep, head, head_pos, token):
        """
        """
        self.dep = dep
        self.head = head
        self.head_pos = head_pos
        self.token = token


class DependencyParser(Preprocessor):
    """Pipeline component for dependency parsing.

    Parameters:
        model (spacy.lang):
            Trained SpaCy language pipeline.

    Properties:
        name (str):
            Key to identify preprocessing step output in
            `chomskIE.utils.Document.sents`.  
    """
    def __init__(self, model):
        """Initializes :class: `DependencyParser`.

        Arguments:
            model (spacy.lang):
                Trained SpaCy language pipeline.
        """
        self._name = 'dep'
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

            model_sent = self._retrieve_model_sent(doc, index)

            dependencies = [DependencyToken(
                                token.dep_,
                                token.head.text,
                                token.head.pos_,
                                token) for token in model_sent]
            doc_sents[index][self.name] = dependencies

        doc.sents = doc_sents
        return doc
