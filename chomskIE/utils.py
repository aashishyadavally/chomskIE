import subprocess
from collections import Counter

import spacy


def retrieve_spacy_language(lang):
    """Retrieves trained language pipeline from within SpaCy.
    If not available, it is downloaded.

    Arguments:
        lang (str):
            Key to trained SpaCy language pipeline.

    Returns:
        model (spacy.lang)
            Trained SpaCy language pipeline.
    """
    try:
        model = spacy.load(lang)
    except:
        subprocess.call(f'python -m spacy download {lang}', shell=True)
        model = spacy.load(lang)
        
    return model


def validate_input(pipe, input, transform):
    """Utility for `chomskIE.preprocess`.

    Validates input format for all preprocessing techniques.

    Arguments:
        pipe (str):
            Name of preprocessing technique class.
        input (list or chomskie.utils.Document):
            Input for preprocessing technique.
        transform (bool):
            If False, input is validated for stream of documents.
            If True, input is validated for single document.
    """
    valid = True

    if not transform:
        if isinstance(input, list):
            for doc in input:
                if not isinstance(doc, Document):
                    valid = False
                    break
    else:
        if not isinstance(input, Document):
            valid = False

    if not valid:
        raise InputError(pipe)
    
    return valid
        


class InputError(Exception):
    """Raised if input for preprocessing step is invalid.
    """
    def __init__(self, pipe):
        """Initializes :class: `InputError`.

        Arguments:
            pipe (str):
                Name of preprocessing technique class.
        """
        print(f'Invalid input for preprocessing step `{pipe}`')


class PipelineError(Exception):
    """Raised if invalid sequence of preprocessing steps are instantiated.
    """
    pass


class Document:
    """Utility representing document contents of a .txt file.

    Based on the instantiated preprocessing steps, can be used to
    access sentences and their components such as tokens, named entities,
    parts of speech, dependency graphs, etc. within the document.

    Parameters:
        name (str):
            Name of .txt file.
        text (str):
            Contents of .txt file.
        processed (bool):
            True, if all the preprocessing steps in the pipeline have been
            instantiated. False otherwise.
        sents (None or list):
            Created following the instantiation of the preprocessing steps
            in the pipeline.
    """
    def __init__(self, name, text, paragraphs):
        """Initializes :class: `Document`.

        Arguments:
            name (str):
                Name of .txt file.
            text (str):
                Contents of .txt file.
            paragraphs (list):
            	Array of paragraphs in the .txt file.
        """
        self.name = name
        self.text = text
        self.paragraphs = paragraphs
        # Document is considered to not have been processed when
        # created. Following the instantiated pre-processing steps,
        # `sents` class variable is modified. The following code
        # snippet shows a sample `Document.sents` object:
        #
        # >> document.sents
        # [{'sent': 'The boy killed the cat.',
        #   'tokens': ['The', 'boy', 'killed', 'the', 'cat', '.'],
        #   'pos_tags': ['DET', 'NOUN', 'VERB', 'DET', 'NOUN', '.']}
        # ]
        self.processed = False
        self.sents = None

        
def filter_invalid_sents(doc):
    """Helps filter invalid sentences in document which are incomplete
    and do not express complete thought such as bullet points.

    Arguments:
        doc (chomskIE.utils.Document):
            Document.

    Returns:
        doc (chomskIE.utils.Document):
            Filtered document.

    Notes:
    A complete sentence contains at least one subject, one predicate,
    one object, and closes with punctuation. Subject and object are
    almost always nouns, and the predicate is always a verb. Thus you
    need to check if your sentence contains two nouns, one verb and
    closes with punctuation.

    References:
    [1] https://stackoverflow.com/questions/50454857/determine-if-a-text-extract-from-spacy-is-a-complete-sentence
    """
    def is_valid(sent):
        tag_counts = Counter([pos[0] for pos in sent['pos_tags']])
        num_subjects = tag_counts['NOUN'] + tag_counts['PROPN'] \
                       + tag_counts['PRON']
        num_predicates = tag_counts['VERB'] + tag_counts['AUX']
        complete = (num_subjects >= 1 and num_predicates >= 1)
        valid = complete and num_subjects > 1
        return valid

    doc_sents = [sent for sent in doc.sents if is_valid(sent)]
    doc.sents = doc_sents

    return doc
