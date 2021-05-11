import argparse
from pathlib import Path

from chomskIE.dataset import (Loader,
                              Writer,
                              DummyLoader,
                              DummyWriter)
from chomskIE.utils import (retrieve_spacy_language,
                            filter_invalid_sents,
                            retrieve_wordnet)
from chomskIE.preprocess import *
from chomskIE.extract import *
from chomskIE.postprocess import (post_process_triples,
                                  post_process_part_tuples)


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


def process_document(doc):
    """Must be called following the completion of the preprocessing
    pipeline to check flag for each ``chomskIE.utils.Document`` object.
    Furthermore, invalid sentences are filtered out.

    Arguments:
        doc (chomskIE.utils.Document)
            Document.

    Returns:
        doc (chomskIE.utils.Document)
            Processed document.
    """
    doc.processed = True
    delattr(doc, 'model_sents')
    doc = filter_invalid_sents(doc)
    return doc


def extract_relations(doc):
    """Pipeline to extract relation templates.

    Arguments:
        doc (chomskIE.utils.Document)
            Document.

    Returns:
        doc (chomskIE.utils.Document)
            Document containing extracted relations.
    """
    pte = PartTupleExtractor()
    vte = VerbTemplateExtractor()

    doc = process_document(doc)

    doc = pte.extract(doc)
    doc = post_process_part_tuples(doc)

    doc = vte.extract(doc, 'born')
    doc = post_process_triples('born', doc)

    doc = vte.extract(doc, 'acquire')
    doc = post_process_triples('acquire', doc)

    return doc


def extract_born_relations(input_path, english_model, transform):
    """
    """
    data_loader = DummyLoader()

    if not transform:
        docs, spacy_docs = data_loader.load_from_path(english_model,
                                                      input_path)
    else:
        doc, spacy_doc = data_loader.load(english_model, input_path)
        docs, spacy_docs = [doc], [spacy_doc]

    bte = BornTupleExtractor()
    docs = [bte.extract(doc, spacy_docs[index]) \
            for index, doc in enumerate(docs)]
    return docs


def fit_transform_batch(input_path, english_model):
    """Extract relation templates from batch of documents.

    Arguments:
        input_path (str):
            Path to folder containing .txt files.
        english_model (spacy.lang)
            Trained SpaCy language pipeline.

    Returns:
        docs (List of chomskIE.utils.Document objects)
            Documents containing extracted relations.
    """
    data_loader = Loader()
    docs = data_loader.load_from_path(input_path)

    for Pipe in PIPELINE:
        docs = Pipe(english_model)(docs)

    docs = [extract_relations(doc) for doc in docs]
    return docs


def fit_transform(input_path, english_model):
    """Extract relation templates from single document.

    Arguments:
        input_path (str):
            Path to folder containing .txt files.
        english_model (spacy.lang)
            Trained SpaCy language pipeline.

    Returns:
        docs (List of chomskIE.utils.Document objects)
            Documents containing extracted relations.
    """
    data_loader  = Loader()
    doc = data_loader.load(input_path)

    for Pipe in PIPELINE:
        doc = Pipe(english_model).transform(doc)

    doc = extract_relations(doc)
    return doc


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CS6320 Final Project')
    parser.add_argument('--input_path', dest='input_path',
                        type=str, default='../assets/data/dev/',
                        help='Path to input data file/directory')
    parser.add_argument('--output_path', dest='output_path',
                        type=str, default='../assets/outputs/',
                        help='Path to output file location')
    parser.add_argument('--transform', dest='transform', action='store_true',
                        help='If passed, transforms sentences in single \
                        dev/test .txt file.')

    args = parser.parse_args()

    input_path, output_path = Path(args.input_path), Path(args.output_path)
    english_model = retrieve_spacy_language(lang=LANGUAGE)

    if not args.transform:
        # Extracting templates for 'BORN' relation
        docs = extract_born_relations(input_path, english_model, args.transform)

        data_writer = DummyWriter()
        data_writer.write(output_path, docs, ['born'])

        # Extracting templates for 'ACQUIRE' and 'PART-OF' relations
        docs = fit_transform_batch(input_path, english_model)

        data_writer = Writer()
        data_writer.write(output_path, docs, ['acquire', 'part'])
    else:
        # Extracting templates for 'BORN' relation
        docs = extract_born_relations(input_path, english_model, args.transform)

        data_writer = DummyWriter()
        data_writer.write(output_path, docs, ['born'])

        # Extracting templates for 'ACQUIRE' and 'PART-OF' relations
        doc = fit_transform(input_path, english_model)

        data_writer = Writer()
        data_writer.write(output_path, [doc], ['acquire', 'part'])
