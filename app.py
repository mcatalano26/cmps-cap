from flask import Flask, render_template, request, redirect, flash, url_for, send_from_directory, jsonify
import os
import praw
from dotenv import load_dotenv


app = Flask(__name__)

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET=os.getenv('CLIENT_SECRET')
APP_NAME=os.getenv('APP_NAME')
REDDIT_USERNAME=os.getenv('REDDIT_USERNAME')
REDDIT_PASSWORD=os.getenv('REDDIT_PASSWORD')
reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=APP_NAME, username=REDDIT_USERNAME, password=REDDIT_PASSWORD)


@app.route('/')
def index():
    return render_template('index.html')

# want this method to show this post and its comments
@app.route('/showPost', methods = ['POST'])
def showPosts():
    reddit_link = request.form.get('reddit_link')
    submission = reddit.submission(url = reddit_link)
    title = submission.title
    selftext = submission.selftext
    comments = []
    submission.comments.replace_more(limit=0)
    for comment in submission.comments:
        comments.append(comment.body)   
    return render_template('post.html', comments = comments, title = title, selftext = selftext)


if __name__ == "__main__":
    app.run(debug=True)