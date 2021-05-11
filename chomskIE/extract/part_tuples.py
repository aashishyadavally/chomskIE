from itertools import chain
from collections import namedtuple, defaultdict

from chomskIE.utils import retrieve_wordnet


# Data structure to store subject-verb-object triples.
PartTuple = namedtuple("PartTuple", ["part", "whole"])


class PartTupleExtractor:
    """All relevant tuples corresponding to each sentence in a document
    that exhibit part-whole relationship are extracted. 

    Extracted tuples belong to (ORGANIZATION, ORGANIZATION) and
    (LOCATION, LOCATION) pairs.

    ``PartTupleExtractor.extract`` is the entry-point.
    """
    def _extract_synonyms(self, wordnet, tokens):
        """Extract set of synonyms using Wordnet.

        Arguments:
            (wordnet):
                Wordnet resource   
            tokens (list):
                List of tokens in sentence.

        Returns:
            (set):
                Set of synonyms.
        """
        synonyms = []
        for token in tokens:
            senses = wordnet.synsets(token)
            synonyms += list(chain.from_iterable([[name.replace('_', ' ') \
                          for name in sense.lemma_names()] for sense in senses]))
        return set(synonyms)

    def _extract_holonyms(self, wordnet, tokens):
        """Extract set of holonyms using Wordnet.

        Arguments:
            (wordnet):
                Wordnet resource   
            tokens (list):
                List of tokens in sentence, and their synonyms.

        Returns:
            (set):
                Set of holonyms.
        """
        holonyms = []
        for token in tokens:
            senses = wordnet.synsets(token)

            for sense in wordnet.synsets(token):
                sense_holonyms = sense.part_holonyms()

                for holonym in sense_holonyms:
                    holonyms += [name.replace('_', ' ') \
                                 for name in holonym.lemma_names()]
        return set(holonyms)

    def _extract_meronyms(self, wordnet, tokens):
        """Extract set of meronyms using Wordnet.

        Arguments:
            (wordnet):
                Wordnet resource   
            tokens (list):
                List of tokens in sentence, and their synonyms.

        Returns:
            (set):
                Set of meronyms.
        """
        meronyms = []
        for token in tokens:
            senses = wordnet.synsets(token)

            for sense in wordnet.synsets(token):
                sense_meronyms = sense.part_meronyms()

                for meronym in sense_meronyms:
                    meronyms += [name.replace('_', ' ') \
                                 for name in meronym.lemma_names()]
        return set(meronyms)

    def _map_part_to_whole(self, parts, wholes):
        """Maps corresponding meronym extracted from the sentence
        to its holonym.

        Arguments:
            parts (list):
                List of meronyms.
            wholes (list):
                List of holonyms.

        Returns:
            part_tuples (list of PartTuple objects)
                List of meronym-holonym pairs.
        """
        if len(parts) < len(wholes):
            wholes = list(wholes)[:len(parts)]
        elif len(parts) > len(wholes):
            parts = list(parts)[:len(wholes)]

        part_tuples = list(zip(parts, wholes))
        return part_tuples

    def _retrieve_part_tuples(self, sent):
        """Retrieve ``PartTuple`` objects for a given sentence.

        Extraction details:
        In every sentence containing more than one location or
        organization named entity (relevant sentences), first,
        synonyms are extracted for each of the tokens. Then,
        holonyms and meronyms are extracted for each of these
        synonyms. Finally, the (part, whole) pairs are extracted
        by taking the intersection of each of these sets with the
        list of tokens.

        Arguments:
            sent (chomskIE.utils.Document sentence)
                Sentence.

        Returns:
            part_tuples (PartTuple objects or None):
                Extracted tuples exhibiting part-whole relationship.
                If no such tuples exist, None is returned.
        """
        def retrieval_pipeline(wordnet, tokens):
            part_tuples = []
            token_synonyms = self._extract_synonyms(wordnet, tokens)
            holonyms = self._extract_holonyms(wordnet, token_synonyms)
            meronyms = self._extract_meronyms(wordnet, token_synonyms)
            parts = meronyms.intersection(tokens)
            wholes = holonyms.intersection(tokens)

            if bool(parts) and bool(wholes):
                part_whole_pairs = self._map_part_to_whole(parts, wholes)
                for part_whole_pair in part_whole_pairs:
                    part_tuples.append(PartTuple(part=part_whole_pair[0],
                                                 whole=part_whole_pair[1]))
            return part_tuples

        loc_tokens, org_tokens = [], []

        for word, ent in sent['named_entities']:
            if ent in ['GPE', 'FAC', 'LOC']:
                word = word.replace(' ', '_')
                loc_tokens.append(word)
            elif ent == 'ORG':
                word = word.replace(' ', '_')
                org_tokens.append(word)

        wordnet = retrieve_wordnet()

        if len(loc_tokens) >= 2:
            return retrieval_pipeline(wordnet, loc_tokens)
        elif len(org_tokens) >= 2:
            return retrieval_pipeline(wordnet, org_tokens)
        else:
            return None

    def extract(self, doc):
        """Extracts ``PartTuple`` objects containing (Organization, Organization)
        or (Location, Location) tuples which exhibit part-of relationship.
        Each such relevant tuple is appended to the corresponding sentence
        in the document.

        Arguments:
            doc (chomskIE.utils.Document):
                Document.

        Returns:
            doc (chomskIE.utils.Document):
                Updated document.
        """
        for index, sent in enumerate(doc.sents):
            part_tuples = self._retrieve_part_tuples(sent)
            doc.sents[index][f'part_tuples'] = part_tuples
        return doc
