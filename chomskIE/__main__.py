from pathlib import Path

from chomskIE.dataset import Loader
from chomskIE.utils import retrieve_spacy_language, filter_invalid_sents
from chomskIE.preprocess import *
from chomskIE.extract.svotriples import VerbTemplateExtractor
from chomskIE.utils import retrieve_wordnet

LANGUAGE = 'en_core_web_sm'

DATA_PATH = Path('../chomskIE/assets/data/dev')

TRANSFORM = False

PIPELINE = [
    SentenceRecognizer,
    ModelTransformer,
    WordTokenizer,
    Lemmatizer,
    PartOfSpeechTagger,
    NamedEntityRecognizer,
    DependencyParser,
]


if __name__ == '__main__':
    english_model = retrieve_spacy_language(lang=LANGUAGE)
    english_model.add_pipe('sentencizer', before='parser')
    english_model.add_pipe('merge_entities')
    
    wordnet = retrieve_wordnet()

    data_loader = Loader()
    if not TRANSFORM:
        docs = data_loader.load_from_path(DATA_PATH)
        for Pipe in PIPELINE:
            docs = Pipe(english_model)(docs)

        for doc in docs:
            doc.processed = True
            delattr(doc, 'model_sents')
            doc = filter_invalid_sents(doc)
            vte = VerbTemplateExtractor(wordnet)
            verb_templates = vte.extract(doc)
            for verb, templates in verb_templates.items():
                print(f'Verb: {verb}')
                print(templates)
    else:
        doc = data_loader.load(DATA_PATH)
        for Pipe in self.args:
            doc = Pipe(english_model).transform(doc)

        doc.processed = True
        delattr(doc, 'model_sents')
        doc = filter_invalid_sents(doc)
