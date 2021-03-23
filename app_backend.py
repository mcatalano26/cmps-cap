#imports
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

import warnings
warnings.filterwarnings('ignore')

import os
from dotenv import load_dotenv
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET=os.getenv('CLIENT_SECRET')
APP_NAME=os.getenv('APP_NAME')
REDDIT_USERNAME=os.getenv('REDDIT_USERNAME')
REDDIT_PASSWORD=os.getenv('REDDIT_PASSWORD')

import praw
import datetime as dt
import random
import re
import string

import pickle
from compress_pickle import dump, load

import spacy
from spacy import displacy
from collections import Counter

import en_core_web_lg
nlp = en_core_web_lg.load()

from spacy_wordnet.wordnet_annotator import WordnetAnnotator
nlp.add_pipe(WordnetAnnotator(nlp.lang), after='tagger')

import nltk
nltk.download('wordnet')

STOP_WORDS = spacy.lang.en.stop_words.STOP_WORDS

from newspaper import Article
from newspaper import Config

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
config = Config()
config.browser_user_agent = user_agent

reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=APP_NAME, username=REDDIT_USERNAME, password=REDDIT_PASSWORD)

def clean_article(article_url):
    try:
        article = Article(article_url, language='en', fetch_images=False, config = config)
        article.download()
        article.parse()
        art_text = article.text
        art_doc = nlp(art_text.lower())
    except:
        print('The article could not be cleaned')
    return art_doc


def contains_url_feature(comment):
    urlarr = []
    urlarr = re.findall('[(]?http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(comment))
    if not urlarr:
        return False
    else:
        return True

#comment_text is the the comment and art_doc is the cleaned text of the article
def wordscore_feature(comment_text, art_doc):
    art_doc = nlp(str(art_doc))
    art_items = [x.text for x in art_doc.ents]
    #get tokens
    art_tokens = []
    for (item, count) in Counter(art_items).most_common(5):
        token = nlp(item)[0]
        art_tokens += [token]
        
    doc = nlp(str(comment_text).lower())
    items = [x.text for x in doc.ents]
    
    score = 0
    
    for (item, count) in Counter(items).most_common(5):
        
        token = nlp(item)
        
        wordScores = []
        
        for art_word in art_tokens:
            
            wordScores += [art_word.similarity(token)]
            
            if len(wordScores) != 0:
                score += sum(wordScores)/len(wordScores)
            else:
                score = 0
    return score

#comment_text is the the comment and art_doc is the cleaned text of the article
def wholescore_feature(comment_text, art_doc):
    art_doc = nlp(str(art_doc))
    comment_text = str(comment_text).lower()
    doc = nlp(comment_text)
    score = art_doc.similarity(doc)
    return score

def remove_urls(text):
    urlarr = re.findall('[(]?http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(text))
    for url in urlarr:
        text = text.replace(url, '')
    return text

def remove_stopwords(text):
    text = nlp(str(text))
    token_list = []
    for token in text:
        token_list.append(token.text)
        
    filtered_text = ''
    
    for word in token_list:
        lexeme = nlp.vocab[word]
        if lexeme.is_stop == False:
            if word in string.punctuation:
                filtered_text += word
            else:
                filtered_text += (' ' + word)
    return filtered_text

def adjwordscore_feature(comment_text, art_doc):
    return

def ner_feature(comment_text, art_doc):
    return

def tfidf_feature(comment, article):
    return

#Send in comment text, reddit url, and feature list
def big_func(comment_text, reddit_url, features, model):
    feature_values = {'tfidf': 0, 'WordScore': 0, 'WholeScore': 0, 'contains_url': False, 'adjWordScore': 0, 'no_url_WordScore': 0, 'no_url_WholeScore': 0, 'WordScoreNoStop': 0, 'WholeScoreNoStop': 0, 'no_url_or_stops_WholeScore': 0, 'no_url_or_stops_WordScore': 0, 'NER_count': 0, 'NER_match': 0}
    submission = reddit.submission(url = reddit_url)
    article_url = submission.url
    cleaned_article_text = clean_article(article_url)
    
    feature_values['contains_url'] = contains_url_feature(comment_text)
    
    #Need to figure out how to do tfidf
    #feature_values['tfidf'] = tfidf_feature(comment_text, cleaned_article_text)
    
    feature_values['WordScore'] = wordscore_feature(comment_text, cleaned_article_text)
    feature_values['WholeScore'] = wholescore_feature(comment_text, cleaned_article_text)
    
    #Need to include Gabe's adjusted word score feature here
    #feature_values['adjWordScore'] = adjwordscore_feature(comment_text, cleaned_article_text)
    
    no_url_comment_text = remove_urls(comment_text)
    no_url_article_text = remove_urls(cleaned_article_text)
    
    feature_values['no_url_WordScore'] = wordscore_feature(no_url_comment_text, no_url_article_text)
    feature_values['no_url_WholeScore'] = wholescore_feature(no_url_comment_text, no_url_article_text)
    
    comment_text = remove_stopwords(comment_text)
    cleaned_article_text = remove_stopwords(cleaned_article_text)
    
    feature_values['WordScoreNoStop'] = wordscore_feature(comment_text, cleaned_article_text)
    feature_values['WholeScoreNoStop'] = wholescore_feature(comment_text, cleaned_article_text)

    comment_text = remove_urls(comment_text)
    cleaned_article_text = remove_urls(cleaned_article_text)
    
    feature_values['no_url_or_stops_WholeScore'] = wholescore_feature(comment_text, cleaned_article_text)
    feature_values['no_url_or_stops_WordScore'] = wordscore_feature(comment_text, cleaned_article_text)
    
    #Need to include Sam's 2 new features, NER_count and NER_match
    #feature_values['NER_count'], feature_values['NER_match'] = ner_feature(comment_text, cleaned_article_text)
    
    prelim_features = []
    for feature in features:
        prelim_features.append(feature_values[feature])
    
    prelim_features = [prelim_features]
    prelim_features = np.array(prelim_features)
    
    prediction = model.predict(prelim_features)
    
    return prediction


#Start of actual code

def judgeComment(comment, reddit_url):
    features = ['WordScore', 'WholeScore', 'contains_url', 'no_url_WordScore', 'no_url_WholeScore', 'WordScoreNoStop', 'WholeScoreNoStop', 'no_url_or_stops_WholeScore', 'no_url_or_stops_WordScore']
    # features = ['WordScore', 'WholeScore', 'contains_url', 'no_url_WordScore', 'no_url_WholeScore', 'WordScoreNoStop', 'WholeScoreNoStop', 'no_url_or_stops_WholeScore', 'no_url_or_stops_WordScore', 'NER_count', 'NER_match', 'tfidf', 'adjWordScore']
    our_model = load("compressed_model.pkl", compression="lzma", set_default_extension=False)

    answer = big_func(comment, reddit_url, features, our_model)[0]

    if answer:
        return 'Good comment! Our model believes that you have read the article and are an informed commenter\n'
    else:
        return 'Bad comment. Our model believes that you have not read the article and do not know what you are talking about\n'
