from flask import Flask, render_template, request, redirect, flash, url_for, send_from_directory, jsonify
import os
import praw
from dotenv import load_dotenv
import app_backend as ab


app = Flask(__name__)

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET=os.getenv('CLIENT_SECRET')
APP_NAME=os.getenv('APP_NAME')
REDDIT_USERNAME=os.getenv('REDDIT_USERNAME')
REDDIT_PASSWORD=os.getenv('REDDIT_PASSWORD')
reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=APP_NAME, username=REDDIT_USERNAME, password=REDDIT_PASSWORD)


def commentScore(comment):
    return comment.score

@app.route('/')
def index():
    return render_template('index.html')

# want this method to show this post and its comments
@app.route('/showPost', methods = ['POST'])
def showPosts():
    goodComments = []
    badComments = []

    reddit_link = request.form.get('reddit_link')
    submission = reddit.submission(url = reddit_link)
    title = submission.title
    selftext = submission.selftext
    #comments = []
    submission.comments.replace_more(limit=0)

    # split into good/bad

    # rank by upvotes
    for comment in submission.comments:
        if (ab.judgeComment(comment.body, reddit_link)[0]):
            goodComments.append(comment)
        else :
            badComments.append(comment) 

    goodComments.sort(reverse = True, key = commentScore)
    badComments.sort(reverse = True, key = commentScore)

    return render_template('post.html', goodComments = goodComments, badComments = badComments, title = title, selftext = selftext, reddit_url = reddit_link)


@app.route('/scoreComment', methods = ['POST'])
def scoreComment():
    # text of comment
    comment = request.form.get("comment")
    reddit_url = request.form.get("reddit_url")
    
    score = ab.judgeComment(comment, reddit_url)[1]
    print("made it")
    return jsonify(score = score)


if __name__ == "__main__":
    app.run(debug=True)