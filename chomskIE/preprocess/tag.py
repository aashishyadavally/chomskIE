from chomskIE.utils import PipelineError
from chomskIE.preprocess.base import Preprocessor


class PartOfSpeechTagger(Preprocessor):
    """Pipeline component for part of speech tagger.

    Parameters:
        model (spacy.lang):
            Trained SpaCy language pipeline.

    Properties:
        name (str):
            Key to identify preprocessing step output in
            `chomskIE.utils.Document.sents`.  
    """
    def __init__(self, model):
        """Initializes :class: `PartOfSpeechTagger`.

        Arguments:
            model (spacy.lang):
                Trained SpaCy language pipeline.
        """
        self._name = 'pos_tags'
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

            if hasattr(doc, 'model_sents'):
                model_sent = doc.model_sents[index]
            else:
                model_sent = self.model(sent)

            tags = [(token.pos_, token.tag_) for token in model_sent]
            doc_sents[index][self.name] = tags

        doc.sents = doc_sents
        return doc
    