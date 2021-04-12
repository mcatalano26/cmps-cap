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
        return 'ERROR'
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
    adjustments = {"PERSON":0.4, "NORP":0.25, "FAC": 0.35, "ORG": 0.075, "GPE": 0.2, "LOC": 0.15, "PRODUCT": 0, "EVENT": 0.2, "WORK_OF_ART": 0, "LAW": 0, "LANGUAGE": 0.2, "DATE": 0.4, "TIME": 0.6, "PERCENT": 0.8, "MONEY": 0.5, "QUANTITY": 0.5, "ORDINAL": 0.25, "CARDINAL": 0.2}
    art_doc = nlp(str(art_doc))
    art_items = [x.text for x in art_doc.ents]
    art_labels = [x.label_ for x in art_doc.ents]

    art_tokens = []
    for (item, count) in Counter(art_items).most_common(5):
        token = nlp(item)[0]
        art_tokens += [token]
    comment_text = str(comment_text)
    doc = nlp(str(comment_text).lower())

    items = [x.text for x in doc.ents]
    labels = [x.label_ for x in doc.ents]

    score = 0

    for (item, count) in Counter(items).most_common(5):
        com_label = labels[items.index(item)]
        token = nlp(item)

        wordScores = []

        for art_word in art_tokens:
            art_label = art_labels[art_tokens.index(art_word)]

            if art_label == com_label:
                amt = adjustments[art_label]
                wordScores += [art_word.similarity(token) - amt]
            else:
                wordScores += [art_word.similarity(token)]
        
        if len(wordScores) != 0:
            score += sum(wordScores)/len(wordScores)
        else:
            score = 0

    return score

def ner_feature(comment_text, art_doc):
    art_doc = nlp(str(art_doc))
    art_items = [x.text for x in art_doc.ents]
    art_tokens = []
    for item in Counter(art_items):
        token = nlp(item)[0]
        art_tokens += [token]
    comment_text = str(comment_text)
    doc = nlp(str(comment_text).lower())
    items = [x.text for x in doc.ents]

    score = 0

    for item in Counter(items):
        token = nlp(item)
        if str(token) in str(art_tokens):
            score += 1
    return len(items), score

def tf(term, document):
    document = str(document)
    term = str(term)

    #instead of splitting up every time, split it initially
    #once and then pass in the term array and term dict to the function
    term_arr = str.split(document)
    term_dict = Counter(term_arr)
    return term_dict[term] / len(term_arr)

def tfidf(term, document, idf_df):
    idf_val = idf_df[idf_df['term'] == str(term)]
    new_idf_val = idf_df.at[idf_val.index[0], 'idf']
    return tf(term, document) * new_idf_val

def tfidf_feature(comment, article):
    idf_df = pd.read_csv('files/tfidf_ss.csv')
    #NaN was a duplicate here, so I just wanna get rid of this every time
    idf_df = idf_df.drop_duplicates()
    idf_df = idf_df.reset_index(drop=True)
    
    tfidf_current = 0
    tfidf_sum = 0
    comment = str(comment)
    term_arr = str.split(comment)
    #could remove duplicate terms to speed up the following loop
    for element in term_arr:
        tfidf_current = tfidf(element, article, idf_df)
        tfidf_sum += tfidf_current
    return tfidf_sum

def length_feature(comment):
    comment = str(comment)
    length = len(comment)
    return length

#Send in comment text, reddit url, and feature list
def big_func(comment_text, reddit_url, features, model, cleaned_article_text, no_url_article_text, no_stop_article_text, no_stop_or_url_article_text):
    feature_values = {'length': 0, 'WordScore': 0, 'WholeScore': 0, 'contains_url': False, 'adjWordScore': 0, 'no_url_WordScore': 0, 'no_url_WholeScore': 0, 'WordScoreNoStop': 0, 'WholeScoreNoStop': 0, 'no_url_or_stops_WholeScore': 0, 'no_url_or_stops_WordScore': 0, 'NER_count': 0, 'NER_match': 0}
    if cleaned_article_text == 'ERROR':
        return ['ERROR']
    
    feature_values['contains_url'] = contains_url_feature(comment_text)
    
    #Need to figure out how to do tfidf
    # feature_values['tfidf'] = tfidf_feature(comment_text, cleaned_article_text)

    feature_values['length'] = length_feature(comment_text)
    
    feature_values['WordScore'] = wordscore_feature(comment_text, cleaned_article_text)
    feature_values['WholeScore'] = wholescore_feature(comment_text, cleaned_article_text)
    
    feature_values['adjWordScore'] = adjwordscore_feature(comment_text, cleaned_article_text)
    
    no_url_comment_text = remove_urls(comment_text)
    
    feature_values['no_url_WordScore'] = wordscore_feature(no_url_comment_text, no_url_article_text)
    feature_values['no_url_WholeScore'] = wholescore_feature(no_url_comment_text, no_url_article_text)
    
    comment_text = remove_stopwords(comment_text)
    
    feature_values['WordScoreNoStop'] = wordscore_feature(comment_text, no_stop_article_text)
    feature_values['WholeScoreNoStop'] = wholescore_feature(comment_text, no_stop_article_text)

    comment_text = remove_urls(comment_text)
    
    feature_values['no_url_or_stops_WholeScore'] = wholescore_feature(comment_text, no_stop_or_url_article_text)
    feature_values['no_url_or_stops_WordScore'] = wordscore_feature(comment_text, no_stop_or_url_article_text)
    
    feature_values['NER_count'], feature_values['NER_match'] = ner_feature(comment_text, no_stop_or_url_article_text)
    
    prelim_features = []
    for feature in features:
        prelim_features.append(feature_values[feature])
    
    prelim_features = [prelim_features]
    prelim_features = np.array(prelim_features)
    
    prediction = model.predict(prelim_features)
    
    return prediction


#Use this function to judge user comments in the app
#judgeComment will return an array. The first element in the array will be True/False. True is a good comment, False is a bad comment
#Second element in the array will be a string to print out
def judgeComment(comment, reddit_url, swearwords, features, our_model, cleaned_article_text, no_url_article_text, no_stop_article_text, no_stop_or_url_article_text, punctuation_lst):
    goodString = 'Good comment! Our model believes that you have read the article and are an informed commenter\n'
    badString = 'Bad comment. Our model believes that you have not read the article and do not know what you are talking about\n'
    errorString = 'We\'re sorry, but there was an error reading in the article associated with this reddit link'
    #Threshold functions first

    #Threshold of comments that are too short or too long to be productive
    if ((isinstance(comment, str)) == False):
        comment = comment.body
    wordCount = len(comment.split())
    if wordCount < 4:
        return [False, 'Bad comment. The model believes that the comment is too short to be helpful']
    if wordCount > 1000:
        return [False, 'Bad comment. The model believes that the comment is too long to be helpful']

    #Threshold removing anything with profanity
    words_in_comment = comment.split()
    for word in words_in_comment:
        for letter in word:
            if letter in punctuation_lst:
                word = word.replace(letter, "")
        word = word.lower()
        if word in swearwords:
            return [False, 'Bad comment. The model believes that there is profanity in this comment']


    #Model work starts here
    answer = 'ERROR'
    answer = big_func(comment, reddit_url, features, our_model, cleaned_article_text, no_url_article_text, no_stop_article_text, no_stop_or_url_article_text)[0]

    if answer == 'ERROR':
        return [False, errorString]

    if answer:
        return [True, goodString]
    else:
        return [False, badString]