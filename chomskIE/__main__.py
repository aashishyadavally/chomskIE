from pathlib import Path

from chomskIE.dataset import Loader
from chomskIE.utils import retrieve_spacy_language
from chomskIE.preprocess import *


LANGUAGE = 'en_core_web_sm'

DATA_PATH = Path('/home/aashish/Github/chomskIE/assets/data/raw')

TRANSFORM = False

PIPELINE = [
    SentenceRecognizer,
    WordTokenizer,
    PartOfSpeechTagger,
]


if __name__ == '__main__':
    english_model = retrieve_spacy_language(lang=LANGUAGE)
    data_loader = Loader()
    if not TRANSFORM:
        docs = data_loader.load_from_path(DATA_PATH)
        for Pipe in PIPELINE:
            pipe = Pipe(english_model)
            docs = pipe(docs)

        for doc in docs:
            doc.processed = True
            print(doc.sents)

    else:
        doc = data_loader.load(DATA_PATH)
        for Pipe in self.args:
            pipe = Pipe(english_model)
            doc = pipe.transform(doc)
        doc.processed = True