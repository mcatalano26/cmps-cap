#!/usr/bin/env python
# coding: utf-8

import spacy
from spacy import displacy
import en_core_web_lg
nlp = en_core_web_lg.load()

import re

from spacy_wordnet.wordnet_annotator import WordnetAnnotator
nlp.add_pipe(WordnetAnnotator(nlp.lang), after='tagger')

#highlight Named Entities in Comments to visualize model for reader
def strong_ner(comment):
    #get NER from comment
    doc = nlp(comment)
    items = [x.text for x in doc.ents]
    #change comment so matches HTML
    for item in items:
        comment = comment.replace(" " + item + " ", " <b> " + item + " </b> ")
    return comment

#fix urls so they can be used again
def restore_url(comment):
    urlarr = []
    urlarr = re.findall('[(]?http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(comment))
    for url in urlarr:
        comment = comment.replace(" " + url + " ", "<a href={link}>{link}</a>".format(link = url))
    return comment

def visualize(comment):
    comment = strong_ner(comment)
    comment = restore_url(comment)
    return comment

def good_comment(comment, confidence):
    return ('[Good - ' + confidence + ']\n\n\n' + comment)

def bad_comment(comment, confidence):
    return ('[Bad - ' + confidence + ']\n\n\n' + comment)
