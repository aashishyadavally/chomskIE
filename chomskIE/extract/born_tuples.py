import spacy
from spacy.symbols import ORTH, LEMMA, POS


class BornTupleExtractor:
    """All tuples in each sentence in the document that fit the template
    BORN (ORGANIZATION/PERSON, DATE, LOCATION) are extracted.
    """
    def _founded_active(self, sent):
        """Extract relations from sentences with 'founded' as the root word,
        used in active voice.

        Arguments:
            sent (spacy.tokens.Document.sent):
                Sentence in document.

        Returns:
            (tuple):
                Organization, Date, Place 
        """
        if 'founded' not in sent.root.text:
            return None
        
        subject = [child for child in sent.root.children if child.dep_ == 'nsubj']
        object = [child for child in sent.root.children if child.dep_ == 'dobj']

        dates = [ent for ent in sent.ents if ent.label_ == 'DATE' and \
                 ent.root.head.tag_ =='IN']
        places = [ent for ent in sent.ents if ent.label_ == 'GPE' and \
                  ent.root.head.tag_ =='IN'] 

        org = object[0] if object else ''
        date = dates[0] if dates else ''
        place = places[0] if places else ''

        if org:
            return org, date, place

    def _founded_passive(self, sent):
        """Extract relations from sentences with 'founded' as the root word,
        used in passive voice.

        Arguments:
            sent (spacy.tokens.Document.sent):
                Sentence in document.

        Returns:
            (tuple):
                Organization, Date, Place 
        """
        if ('founded' not in sent.text.lower()) and \
            ('established' not in sent.text.lower()):
            return None

        object = [ent for ent in sent.ents if ent.label_ == 'ORG']
        dates = [ent for ent in sent.ents if ent.label_ == 'DATE' and\
                 ent.root.head.tag_ =='IN']
        places = [ent for ent in sent.ents if ent.label_ == 'GPE' and\
                  ent.root.head.tag_ =='IN'] 

        org = object[0] if object else ''
        date = dates[0] if dates else ''
        place = places[0] if places else ''

        if org and date:
            return org, date, place


    def _retrieve_born_template(self, sent):
        """Retrieve information templates that indicate a person/organization
        being 'born'.

        Arguments:
            sent (spacy.tokens.Document.sent):
                Sentence in document.

        Returns:
            (tuple):
                Organization, Date, Place 
        """
        if 'born' not in sent.root.text :
            return None

        subject = [child for child in sent.root.children if child.dep_ == 'nsubjpass']
        places = [ent for ent in sent.ents if ent.label_ == 'GPE' and \
                  ent.root.head.tag_ =='IN'] 
        dates = [ent for ent in sent.ents if ent.label_ == 'DATE' and \
                 ent.root.head.tag_ =='IN']

        person = subject[0].text if subject else ''
        date = dates[0].text if dates else ''
        place = places[0].text if places else ''

        if person:
            return person, date, place


    def _retrieve_founded_template(self, sent):
        """Retrieve information templates that indicate an organization
        being founded.

        Arguments:
            sent (spacy.tokens.Document.sent):
                Sentence in document.

        Returns:
            (tuple):
                Organization, Date, Place 
        """
        _templates = self._founded_active(sent)
        if not _templates:
            _templates = self._founded_passive(sent)

        return _templates


    def extract(self, doc, spacy_doc):
        """Extracts organization-date-location templates which exhibit
        'born' relationship. Each such relevant tuple is appended to
        the corresponding sentence in the document.

        Arguments:
            doc (chomskIE.utils.Document):
                Document
            spacy_doc (spacy.tokens.Document):
                Document processed by spacy English language model.

        Returns:
            doc (chomskIE.utils.Document)
                Updated document with extracted BORN relations.
        """
        doc_sents = []

        for sent in spacy_doc.sents:
            templates = []
            dummy_sent = {'sent': sent}

            _born_template = self._retrieve_born_template(sent)
            _founded_template = self._retrieve_founded_template(sent)

            if _born_template: 
                templates.append(_born_template)

            if _founded_template:
                templates.append(_founded_template)

            dummy_sent['born_templates'] = templates
            doc_sents.append(dummy_sent)

        doc.sents = doc_sents
        return doc
