from flask import Flask, render_template, request, redirect, flash, url_for, send_from_directory, jsonify
import os
import praw
from dotenv import load_dotenv
load_dotenv()
import app_backend as ab

#imports
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

import warnings
warnings.filterwarnings('ignore')

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


app = Flask(__name__)

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET=os.getenv('CLIENT_SECRET')
APP_NAME=os.getenv('APP_NAME')
REDDIT_USERNAME=os.getenv('REDDIT_USERNAME')
REDDIT_PASSWORD=os.getenv('REDDIT_PASSWORD')
reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=APP_NAME, username=REDDIT_USERNAME, password=REDDIT_PASSWORD)

swearwords_df = pd.read_csv('files/edited-swear-words.csv')
swearwords = swearwords_df.swear.tolist()
features = ['length', 'adjWordScore', 'NER_count', 'NER_match', 'WordScore', 'WholeScore', 'contains_url', 'no_url_WordScore', 'no_url_WholeScore', 'WordScoreNoStop', 'WholeScoreNoStop', 'no_url_or_stops_WholeScore', 'no_url_or_stops_WordScore']
our_model = load("latest_model.pkl", compression="lzma", set_default_extension=False)


def commentScore(comment):
    return comment.score

@app.route('/')
def index():
    return render_template('index.html')

# want this method to show this post and its comments
@app.route('/showPost', methods = ['POST'])
def showPosts():
    comments = []

    reddit_link = request.form.get('reddit_link')
    submission = reddit.submission(url = reddit_link)
    title = submission.title
    selftext = submission.selftext
    submission.comments.replace_more(limit=0)

    submission = reddit.submission(url = reddit_url)
    article_url = submission.url
    cleaned_article_text = ab.clean_article(article_url)
    no_url_article_text = ab.remove_urls(cleaned_article_text)
    no_stop_article_text = ab.remove_stopwords(cleaned_article_text)
    no_stop_or_url_article_text = ab.remove_urls(no_stop_article_text)

    # rank by upvotes
    for comment in submission.comments:
        ab.judgeComment(comment, reddit_link, swearwords, features, our_model, cleaned_article_text, no_url_article_text, no_stop_article_text, no_stop_or_url_article_text)[0]
        comments.append(comment)

    comments.sort(reverse=True, key=commentScore)

    return render_template('post.html', comments = comments, title = title, selftext = selftext, reddit_url = reddit_link)


@app.route('/scoreComment', methods = ['POST'])
def scoreComment():
    # text of comment
    comment = request.form.get("comment")
    reddit_url = request.form.get("reddit_url")
    
    score = ab.judgeComment(comment, reddit_url, swearwords, features, our_model, cleaned_article_text, no_url_article_text, no_stop_article_text, no_stop_or_url_article_text)[1]
    print("made it")
    return jsonify(score = score)


if __name__ == "__main__":
    app.run(debug=True)