This is the github repository for 'Did You Even Read The Article?'. DYERTA was created by Matt Catalano, Sam Minix, Leo Simanonok, and Gabe Harris for their senior computer science capstone project. The goal of this project is to create a machine learning algorithm that could recognize if a user commenting on an online article has actually read the article or if they are just reacting to the headline, spreading misinformation, derailing civil discussion, or creating hostile environments. The four members of the group had noticed that since the rise of public forums like Reddit and Facebook, users who are misinformed or not interested in constructive conversation are frequently displayed center stage. Oftentimes, social media platforms are inundated with comments by users which are not at all related to the argument or article being discussed. This overwhelming wave of text makes it difficult for users to determine what is true and who to engage in constructive conversation. Identifying and filtering bad comments will help to curb the spread of lies and toxic discussion.<br/>

**Methods:**

We used different metrics for similarity between comments and articles, comment length, presence of url's in comment, and profanity as features in a Random Forest Machine Learning Model to predict if a comment is good or not.

Training data was taken from the heavily moderated subreddit, r/neutralnews. We were able to get a data dump of moderator-deemed 'bad' comments. These are comments that moderators had removed from posts. For our 'good' comments, we scraped the same articles that the 'bad' comments came from and used the comments that were remaining as 'good' values. The total number of comments trained on was roughly 10,000 with a nearly even split of 'good' and 'bad' comments.<br/>


**Results:**

The comment dataset was split to train on 90% and test on the remaining 10%. During this testing, we were receiving ~82% accuracy with our model. This, initially, felt very promising. However, we believe that this was slightly misleading. To test the model against what we truly wanted to predict, our team handlabeled 400 comments as 'good' or 'bad' and ran the model on this new validation set. When run on this new validation set, we only received 60% accuracy, which is not nearly as good. We decided to retrain the model using our handlabeled comments as a fraction of the training data. Doing this, we were able to bump our accuracy up to 74%. This is the version of the model that is used in our program currently.<br/>

![alt text](https://github.com/mcatalano26/cmps-cap/blob/master/files/ReadImages/ConfusionMatrices.JPG)

**Prototype and how to run it:**

We have created a webpage that can take in a reddit link, mark all comments as good or bad with the confidence of our model, and take in a new user comment and rate it for you. This webpage, currently, can only be run locally.

![alt text](https://github.com/mcatalano26/cmps-cap/blob/master/files/ReadImages/HomePage.JPG)

![alt text](https://github.com/mcatalano26/cmps-cap/blob/master/files/ReadImages/LinkPage.JPG)

When a new comment is entered, in addition to rating the comment good or bad, the webpage will display a pdf explaining the reasons behind the prediction. The top 10 features that contributed to the model will be displayed in order of their importance. If their importance value is negative, it indicates that that feature contributed to a prediction indicating that the comment is 'bad'. If the importance value is positive, it indicates that the value of the feature helped to imply that the comment is 'good'.<br/>

![alt text](https://github.com/mcatalano26/cmps-cap/blob/master/files/ReadImages/GoodFeatureImportance.JPG)

![alt text](https://github.com/mcatalano26/cmps-cap/blob/master/files/ReadImages/BadFeatureImportance.JPG)

**Feature explanation:**

profanity - Boolean. Is there profanity in the comment?<br/>
length - Int. # of characters in a comment<br/>
WordScore - Double. Similarity between the named entities in the comment and the article<br/>
no_url_WordScore - Double. WordScore analyzed after url's have been removed.<br/>
WordScoreNoStop - Double. WordScore analyzed after stop words have been removed.<br/>
no_url_or_stops_WordScore - Double. WordScore analyzed after stop words and urls have been removed.<br/>
WholeScore - Double. Similarity between entire text of comment and article<br/>
no_url_WholeScore - Double. WholeScore analyzed after urls have been removed.<br/>
WholeScoreNoStop - Double. WholeScore analyzed after stop words have been removed.<br/>
no_url_or_stops_WholeScore - Double. WholeScore analyzed after urls and stop words have been removed.<br/>
adjWordScore - WordScore normalized across named entity categories.<br/>
NER_count - Int. The amount of named entities in the comment.<br/>
NEW_match - Int. The amount of named entities that are the same between the comment and the article.<br/>
contains_url - Boolean. Are there any urls in the comment?<br/>

*Named entities are real-world objects, such as persons, locations, organizations, products, etc., that can be denoted with a proper name. Stop words are words like 'the', 'or', 'and', 'this', and 'that'.*

**Running this code locally:**

If you want to run this program yourself, simply clone this repository in a folder, and run the following two commands in a terminal located at the newly cloned git repo:<br/>
*pip install -r requirements.txt*<br/>
*python -m spacy download en_core_web_lg*<br/>

After this, you can run:<br/>
*python app.py*<br/>
in your terminal and the web page will begin running on your local host. Paste in a reddit link to check out what our model thinks of the comments! If the reddit link does not have a news article (url) posted at the top of the thread, the app will not work. Some good subreddits that almost always have articles linked to threads are r/neutralnews and r/neutralpolitics.<br/>

If you are interested in the code that the app is running on, you can see the frontend of the flask app in app.py, templates/base.html, templates/index.html, and templates/post.html. The backend of the flask app can be found in app_backend.py. We train the model in the file pickleCheck.py.

**Future Steps:**

Going forward, we believe that we need to explore more models beyond the random forest, especially experimenting with semi-supervised learning and deep learning. Ideally, we would also like to improve the user interface of the website and host it somewhere on the internet. We believe that our labeled data could be increased through user input and feedback. If we were to get all users to rate comments good or bad as they used the product, we would be able to build a much more sophisticated training set for our model to work with. At the moment, there is clearly more work that is needed before this is something that could be given to the public. Exploring more models, more features that could indicate relevance, and increasing our training set are all steps towards making this available for public release.<br/>

**References:**

1. https://www.facebook.com/journalismproject/programs/third-party-fact-checking, Facebook’s Third-Party Fact-Checking Program
2. https://www.rand.org/research/projects/truth-decay/fighting-disinformation/search.html, Tools that Fight Disinformation Online
3. https://eprints.cs.univie.ac.at/3724/1/fp070-momeni.pdf, Identification of Useful User Comments in Social Media: A Case Study on Flickr Commons
4. https://eprints.cs.univie.ac.at/3724/1/fp070-momeni.pdf, Facts or Friends? Distinguishing Informational and Conversational Questions in 5. Social Q&A Sites
6. https://towardsdatascience.com/named-entity-recognition-with-nltk-and-spacy-8c4a7d88e7da, Named Entity Recognition with NLTK and SpaCy
7. https://wordnet.princeton.edu/, WordNet, a Lexical Database for English
8. http://www.nltk.org/howto/wordnet.html WordNet explanation
9. https://spacy.io/usage/vectors-similarity Similarity score explanation


