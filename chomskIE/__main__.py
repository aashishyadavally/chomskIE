import argparse
from pathlib import Path
from collections import namedtuple

from chomskIE.dataset import Loader, Writer
from chomskIE.utils import retrieve_spacy_language, filter_invalid_sents
from chomskIE.preprocess import *
from chomskIE.extract.svotriples import VerbTemplateExtractor
from chomskIE.utils import retrieve_wordnet

LANGUAGE = 'en_core_web_sm'

PIPELINE = [
    SentenceRecognizer,
    ModelTransformer,
    WordTokenizer,
    Lemmatizer,
    PartOfSpeechTagger,
    NamedEntityRecognizer,
    DependencyParser,
]


def post_process_document(doc):
    """
    """
    doc.processed = True
    delattr(doc, 'model_sents')
    doc = filter_invalid_sents(doc)
    return doc

def post_process_triples(triple_type, triples):
    """
    """
    templates = []

    if triple_type == 'born':
        Args = namedtuple("Arguments", ["arg1", "arg2", "arg3"])

        for sent, svotriples in triples:
            for triple in svotriples:
                if triple.subject[0].ent_type_ in ['PERSON', 'ORG']:
                    arg1 = triple.subject
                    for obj in triple.object:
                        if obj.ent_type_ == 'DATE':
                            arg2 = obj
                        elif obj.ent_type_ == 'GPE':
                            arg3 = obj
                    if 'arg2' not in locals():
                        arg2 = None

                    if 'arg3' not in locals():
                        arg3 = None

                    if arg2 is None and arg3 is None:
                        pass
                    else:
                        templates.append(Args(arg1, arg2, arg3))

    elif triple_type == 'acquire':
        Args = namedtuple("Arguments", ["arg1", "arg2", "arg3"])

        for sent, svotriples in triples:
            for triple in svotriples:
                if triple.subject[0].ent_type_ == 'ORG':
                    arg1 = triple.subject
                    for obj in triple.object:
                        if obj.ent_type_ == 'ORG':
                            arg2 = obj
                        elif obj.ent_type_ == 'DATE':
                            arg3 = obj
                    if 'arg2' not in locals():
                        arg2 = None

                    if 'arg3' not in locals():
                        arg3 = None

                    if arg2 is None and arg3 is None:
                        pass
                    else:
                        templates.append(Args(arg1, arg2, arg3))

    elif triple_type == 'part':
        Args = namedtuple("Arguments", ["arg1", "arg2"])

    return templates


def fit_transform_batch(input_path, output_path, english_model):
    """
    """
    data_loader, data_writer = Loader(), Writer()
    docs = data_loader.load_from_path(input_path)

    for Pipe in PIPELINE:
        docs = Pipe(english_model)(docs)

    for doc in docs:
        doc = post_process_document(doc)
        vte = VerbTemplateExtractor()

        born_triples = vte.extract(doc, 'born')
        acquire_triples = vte.extract(doc, 'acquire')

        templates = {
            'BORN': post_process_triples('born', born_triples),
            'ACQUIRE': post_process_triples('acquire', acquire_triples)
        }

        print(templates)

#        data_writer.write(output_path, doc.name, templates)


def fit_transform(input_path, output_path, english_model):
    """
    """
    data_loader, data_writer = Loader(), Writer()
    doc = data_loader.load(input_path)

    for Pipe in PIPELINE:
        doc = Pipe(english_model).transform(doc)
    doc = post_process_document(doc)

    born_triples = vte.extract(doc, 'born')
    acquire_triples = vte.extract(doc, 'acquire')

    templates = {
        'BORN': post_process_triples('born', born_triples),
        'ACQUIRE': post_process_triples('acquire', acquire_triples)
    }

#    data_writer.write(output_path, doc.name, templates)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CS6320 Final Project')
    parser.add_argument('--input_path', dest='input_path',
                        type=str, default='../assets/data/dev/',
                        help='Path to input data file/directory')
    parser.add_argument('--output_path', dest='output_path',
                        type=str, default='../assets/output.json',
                        help='Path to output file location')
    parser.add_argument('--transform', dest='transform', action='store_true',
                        help='If passed, transforms sentences in single \
                        dev/test .txt file.')

    args = parser.parse_args()

    input_path, output_path = Path(args.input_path), Path(args.output_path)
    english_model = retrieve_spacy_language(lang=LANGUAGE)
    data_loader = Loader()

    if not args.transform:
        fit_transform_batch(input_path, output_path, english_model)

    else:
        fit_transform_batch(input_path, output_path, english_model)
