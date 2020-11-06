import os
os.system('pip install -U python-dotenv')

#Need to fix this part
#from dotenv import load_dotenv
#load_dotenv()

##CLIENT_ID = os.getenv('CLIENT_ID')
##CLIENT_SECRET=os.getenv('CLIENT_SECRET')
##APP_NAME=os.getenv('APP_NAME')
##REDDIT_USERNAME=os.getenv('REDDIT_USERNAME')
##REDDIT_PASSWORD=os.getenv('REDDIT_PASSWORD')

CLIENT_ID='19bvmJjVRPulcA'
CLIENT_SECRET='-CPjNx_uM2kfohYCzej_iYAbkko'
APP_NAME='cmpsCap'
REDDIT_USERNAME='mattcat26'
REDDIT_PASSWORD='2Mkj2644'


os.system('pip install praw')
import praw
import pandas as pd
import datetime as dt
import numpy as np

reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=APP_NAME, username=REDDIT_USERNAME, password=REDDIT_PASSWORD)

subreddit = reddit.subreddit('neutralnews')
top_subreddit = subreddit.top()
topics_dict = {'title':[], 'score':[], 'id':[], 'url':[], 'comms_num': [], 'created':[], 'body':[]}
for submission in top_subreddit:
    topics_dict['title'].append(submission.title)
    topics_dict['score'].append(submission.score)
    topics_dict['id'].append(submission.id)
    topics_dict['url'].append(submission.url)
    topics_dict['comms_num'].append(submission.num_comments)
    topics_dict['created'].append(submission.created)
    topics_dict['body'].append(submission.selftext)
topics_data = pd.DataFrame(topics_dict)

comments_dict = {"action": [], "content": [], "author": [], "details": [], "submissionId": [], "commentId": []}
for submission in subreddit.top(limit=20):
    #print(submission.title, submission.id)
    submission.comments.replace_more(limit=100)
    for comment in submission.comments:
        #print(top_level_comment.body)
        
        #What is the action and details column for?
        comments_dict["action"].append(np.nan)
        comments_dict["content"].append(comment.body)
        comments_dict["author"].append(comment.author)
        comments_dict["details"].append(np.nan)
        comments_dict["submissionId"].append(submission.id)
        comments_dict["commentId"].append(comment.id)

comment_data = pd.DataFrame(comments_dict)

from newspaper import Article
from newspaper import Config

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
config = Config()
config.browser_user_agent = user_agent

import spacy
from spacy import displacy
from collections import Counter
os.system('python -m spacy download en_core_web_lg')
os.system('pip install spacy-wordnet')

import en_core_web_lg
nlp = en_core_web_lg.load()

from spacy_wordnet.wordnet_annotator import WordnetAnnotator
nlp.add_pipe(WordnetAnnotator(nlp.lang), after='tagger')


STOP_WORDS = spacy.lang.en.stop_words.STOP_WORDS

def clean_articles(topics_data, comment_data, text_list):
    for url in topics_data['url']:
        try:
            article = Article(submission.url, language='en', fetch_images=False, config = config)
            article.download()
            article.parse()
            art_text = article.text
            art_doc = nlp(art_text.lower())
            text_list.append(art_doc)
        #if there is an exception, remove comments that go with this article
        except:
            text_list.append("error")
            comment_data = comment_data[comment_data['submissionId'] != url]
            continue
    
    topics_data['text'] = text_list
    
clean_articles(topics_data, comment_data, [])

topics_data.to_csv('topics_data.csv')
comment_data.to_csv('comment_data.csv')


