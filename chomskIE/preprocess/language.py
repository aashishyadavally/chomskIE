from chomskIE.utils import PipelineError
from chomskIE.preprocess.base import Preprocessor


class ModelTransformer(Preprocessor):
    """Pipeline component for transforming a sentence based
    on trained SpaCy language model.

    It should be defined in the pipeline after
    ``chomskIE.preprocess.SentenceRecognizer``.

    Parameters:
        model (spacy.lang):
            Trained SpaCy language pipeline.

    Properties:
        name (str):
            Key to identify preprocessing step output in
            `chomskIE.utils.Document.sents`.  
    """
    def __init__(self, model):
        """Initializes :class: `ModelTransformer`.

        Arguments:
            model (spacy.lang):
                Trained SpaCy language pipeline.
        """
        self._name = 'model_sents'
        self.model = model

    @property
    def name(self):
        return self._name

    def transform(self, doc):
        """Apply the model transformation to single document.

        Arguments:
            doc (chomskIE.utils.Document):
                Document to transform.

        Returns:
            doc (chomskIE.utils.Document):
                Processed document.
        """
        self._validate_input(doc, True)
        doc_sents = doc.sents
        model_sents = []

        for index, doc_sent in enumerate(doc_sents):
            if 'sent' in doc_sent:
                sent = doc_sent['sent']
            else:
                error_msg = 'Sequence of pre-processing steps is incorrect.'
                raise PipelineError(error_msg)
            model_sents.append(self.model(sent))

        setattr(doc, self.name, model_sents)
        return doc
    