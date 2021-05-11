from collections import namedtuple

import datefinder
from datefinder import DateFinder


ARGUMENT_ENTITY_TYPES = {
    'born' : [
        ['PERSON', 'ORG'],
        ['DATE'],
        ['GPE'],
    ],
    'acquire': [
        ['ORG'],
        ['ORG'],
        ['DATE'],
    ],
}


def post_process_triples(triple_type, doc):
    """Post-processes SVOTriples extracted for template types
    involving verbs similar to 'born' and 'acquire'.

    Template #1:
    BORN (PERSON/ORGANIZATION, DATE, LOCATION)

    Template #2:
    ACQUIRE (ORGANIZATION, ORGANIZATION, DATE)

    Arguments:
        triple_type (str):
            Relation.
        doc (chomskIE.utils.Document):
            Document containing list of SVOTriples for the verb.

    Returns:
        doc (chomskIE.utils.Document):
            Updated document containing relevant templates.
    """
    def extract_date_string(sentence):
        date_finder = DateFinder()
        matches = list(date_finder.extract_date_strings(sentence))
        date_string = matches[0][0]
        extra_tokens = matches[0][2]['extra_tokens']

        for et in extra_tokens:
            date_string = date_string.replace(et, '')

        date_string = date_string.strip()
        return date_string

    Args = namedtuple("Arguments", ["arg1", "arg2", "arg3"])

    ents = ARGUMENT_ENTITY_TYPES[triple_type]
    for index, sent in enumerate(doc.sents):
        templates = []
        svotriples = sent[f'{triple_type}_svotriples']
        for triple in svotriples:
            arg1 = triple.subject[0]

            if arg1.ent_type_ in ents[0]:
                for verb in triple.verb:
                    arg2, arg3 = None, None
                    for child in verb.children:
                        if child.ent_type_ in ents[1] and child != arg1:
                            arg2 = child
                            # Extracting date for third argument in relation
                            # using regex.
                            date_string = extract_date_string(sent['sent'])
                            if date_string:
                                arg3 = date_string

                    if not(arg2 is None and arg3 is None):
                        templates.append(Args(arg1, arg2, arg3))
        doc.sents[index][f'{triple_type}_templates'] = templates
        del doc.sents[index][f'{triple_type}_svotriples']
    return doc


def post_process_part_tuples(doc):
    """Post-processes tuples extracted from sentences which
    exhibit part-of relation.

    Template:
    PART-OF (ORGANIZATION/LOCATION, ORGANIZATION/LOCATION)

    Arguments:
        doc (chomskIE.utils.Document):
            Document containing tuples exhibiting PART-OF relation.

    Returns:
        doc (chomskIE.utils.Document):
            Updated document containing relevant templates.
    """
    Args = namedtuple("Arguments", ["arg1", "arg2"])

    for index, sent in enumerate(doc.sents):
        templates = []
        if sent['part_tuples']:
            for part_tuples in sent['part_tuples']:
                for _tuple in [part_tuples]:
                    templates.append(Args(getattr(_tuple, 'part'),
                                          getattr(_tuple, 'whole')))
        doc.sents[index][f'part_templates'] = templates
        del doc.sents[index][f'part_tuples']
    return doc
