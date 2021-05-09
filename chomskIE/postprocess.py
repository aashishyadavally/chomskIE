from collections import namedtuple


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
    'part': [
        ['ORG', 'GPE'],
        ['ORG', 'GPE'],
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
            Verb
        doc (chomskIE.utils.Document):
            Document containing list of SVOTriples for the verb.

    Returns:
        doc (chomskIE.utils.Document):
            Updated document containing relevant templates.
    """
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
                        elif child.ent_type_ in ents[2] and child != arg1:
                            arg3 = child
                    if not(arg2 is None and arg3 is None):
                        templates.append(Args(arg1, arg2, arg3))
        doc.sents[index][f'{triple_type}_templates'] = templates
        del doc.sents[index][f'{triple_type}_svotriples']
#            if arg1.ent_type_ in ents[0]:
#                for obj in triple.object:
#                    arg2, arg3 = None, None
#                    if obj.ent_type_ in ents[1]:
#                         arg2 = obj
#                    elif obj.ent_type_ in ents[2]:
#                        arg3 = obj
#                    if not(arg2 is None and arg3 is None):
#                        templates.append(Args(arg1, arg2, arg3))
#        doc.sents[index][f'{triple_type}_templates'] = templates
#        del doc.sents[index][f'{triple_type}_svotriples']


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
    pass