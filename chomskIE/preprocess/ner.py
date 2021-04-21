from chomskIE.utils import PipelineError
from chomskIE.preprocess.base import Preprocessor


class NamedEntityRecognizer(Preprocessor):
    """Pipeline component for named entity recognizer.

    Parameters:
        model (spacy.lang):
            Trained SpaCy language pipeline.

    Properties:
        name (str):
            Key to identify preprocessing step output in
            `chomskIE.utils.Document.sents`.  
    """
    def __init__(self, model):
        """Initializes :class: `NamedEntityRecognizer`.

        Arguments:
            model (spacy.lang):
                Trained SpaCy language pipeline.
        """
        self._name = 'named_entities'
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

            entities = [(entity.text, entity.label_) for entity in model_sent.ents]
            doc_sents[index][self.name] = entities

        doc.sents = doc_sents
        return doc
    