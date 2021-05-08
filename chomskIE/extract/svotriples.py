from itertools import chain
from operator import attrgetter
from collections import namedtuple, defaultdict

from spacy.symbols import *

from textacy.extract.triples import expand_noun, expand_verb

from chomskIE.utils import retrieve_wordnet


# Categories of SpaCy dependency tags
_NOMINAL_SUBJ_DEPS = {nsubj, nsubjpass}
_CLAUSAL_SUBJ_DEPS = {csubj, csubjpass}
_ACTIVE_SUBJ_DEPS = {csubj, nsubj}
_VERB_MODIFIER_DEPS = {aux, auxpass, neg}

# Data structure to store subject-verb-object triples.
SVOTriple = namedtuple("SVOTriple", ["subject", "verb", "object"])


class VerbTemplateExtractor:
    """Extracts relevant information from a document which fit the
    following information templates from subject-verb-object triples.

    Template #1: BORN (PERSON/ORGANIZATION, DATE, LOCATION)

    Template #2: ACQUIRE (ORGANIZATION, ORGANIZATION, DATE)
    """
    def _filter_on_ne(self, triples):
        """
        TO-DO: Implement according to templates.
        """
        return triples

    def _filter_on_verbs(self, verbs, triples):
        """Extract relevant subject-verb-object triples which
        contain the verb in ``verbs``.

        Arguments:
            verbs (set):
                Set of relevant verbs for a particular template.

            triples (list of ``SVOTriple`` objects):
                (subject, verb, object) triples in document.

        Returns:
            relevant (list of ``SVOTriple`` objects):
                List of relevant subject-verb-object triples that
                fit Template #1 and Template #2.
        """
        relevant = []

        for triple in triples:
            verbs_extra = ({token.text for token in triple.verb}).\
                            union({token.lemma_ for token in triple.verb})
            if any(verb in verbs_extra for verb in verbs):
                relevant.append(triple)

        return relevant

    def _extract_verbs(self, verb):
        """Extract verbs similar to ``verb`` using Wordnet.

        Arguments:
            verb (str):
                Verb

        Returns:
            (set):
                Set of verbs similar to ``verb``.
        """
        if verb == 'born':
            verbs_extra, verbs = [verb], ['founded', 'created']
        else:
            verbs_extra, verbs = [], [verb]

        wordnet = retrieve_wordnet()

        for verb in verbs:
            senses = wordnet.synsets(verb, pos=wordnet.VERB)
            verbs_extra += list(chain.from_iterable([[name.replace('_', ' ') \
                          for name in sense.lemma_names()] for sense in senses]))
        return set(verbs_extra)

    def _retrieve_svo_triples(self, sent):
        """Retrieves subject-verb-object triples from a sentence.

        ``textacy.extract.triples.subject_verb_object_triples``
        extended to retrieve subject-verb-object-triples from
        ``chomskIE.utils.Document``.

        Arguments:
            sent (chomskIE.utils.Document):
                Sentence in document.

        Returns:
            triples (list of SVOTriple objects):
                List of SVO triple as (subject, verb, object) in order
                of appearence, where each is a ``spacy.tokens.Token``
                object.
        """
        # Connect subjects/objects to direct verb heads and expand
        # them to include conjuncts, compound nouns, etc.
        dependency_tokens, triples = sent['dep'], []
        verb_sos = defaultdict(lambda: defaultdict(set))

        for dependency_token in dependency_tokens:
            token = dependency_token.token
            head = token.head

            # Ensure entry for all verbs, even if empty, to catch conjugate
            # verbs without direct subject/object deps
            if token.pos == VERB:
                _ = verb_sos[token]

            # Nominal subject of active or passive verb
            if token.dep in _NOMINAL_SUBJ_DEPS:
                if head.pos == VERB:
                    verb_sos[head]["subjects"].update(expand_noun(token))

            # Clausal subject of active or passive verb
            elif token.dep in _CLAUSAL_SUBJ_DEPS:
                if head.pos == VERB:
                    verb_sos[head]["subjects"].update(token.subtree)

            # Nominal direct object of transitive verb
            elif token.dep == dobj:
                if head.pos == VERB:
                    verb_sos[head]["objects"].update(expand_noun(token))

            # Prepositional object acting as agent of passive verb
            elif token.dep == pobj:
                if head.dep == agent and head.head.pos == VERB:
                    verb_sos[head.head]["objects"].update(expand_noun(token))

            # Open clausal complement, but not as a secondary predicate
            elif token.dep == xcomp:
                if (
                    head.pos == VERB
                    and not any(child.dep == dobj for child in head.children)
                ):
                    verb_sos[head]["objects"].update(token.subtree)

        # Fill in any indirect relationships connected via verb conjuncts
        for verb, so_dict in verb_sos.items():
            conjuncts = verb.conjuncts
            if so_dict.get("subjects"):
                for conj in conjuncts:
                    conj_so_dict = verb_sos.get(conj)
                    if conj_so_dict and not conj_so_dict.get("subjects"):
                        conj_so_dict["subjects"].update(so_dict["subjects"])
            if not so_dict.get("objects"):
                so_dict["objects"].update(
                    obj
                    for conj in conjuncts
                    for obj in verb_sos.get(conj, {}).get("objects", [])
                )

        # Expand verbs and restructure into ``SVOTriple`` objects.
        for verb, so_dict in verb_sos.items():
            if so_dict["subjects"] and so_dict["objects"]:
                triples.append(
                    SVOTriple(
                        subject=sorted(so_dict["subjects"],
                                       key=attrgetter("i")),
                        verb=sorted(expand_verb(verb),
                                    key=attrgetter("i")),
                        object=sorted(so_dict["objects"],
                                      key=attrgetter("i")),
                    )
                )
        return triples

    def extract(self, doc, verb):
        """
        """
        templates = []

        for sent in doc.sents:
            svo_triples = self._retrieve_svo_triples(sent)
            verbs = self._extract_verbs(verb)
            svo_triples = self._filter_on_verbs(verbs, svo_triples)
            svo_triples = self._filter_on_ne(svo_triples)

            if svo_triples:
                templates.append((sent['sent'], svo_triples))

        return templates
