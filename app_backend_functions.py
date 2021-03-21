import random

from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelBinarizer

from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings('ignore')

import praw

import os
from dotenv import load_dotenv
load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET=os.getenv('CLIENT_SECRET')
APP_NAME=os.getenv('APP_NAME')
REDDIT_USERNAME=os.getenv('REDDIT_USERNAME')
REDDIT_PASSWORD=os.getenv('REDDIT_PASSWORD')

reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=APP_NAME, username=REDDIT_USERNAME, password=REDDIT_PASSWORD)

def set_up_train_test_split(df, feature_list, target_name, test_size):
    X = df[feature_list]
    X = X.to_numpy()
    y = df[target_name]
    y = y.to_numpy()
    rand_state = random.randint(0, 1000)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = test_size, random_state=rand_state)
    return X_train, X_test, y_train, y_test

#Random Forest Classifier
def random_forest_class_func(df, feature_list, target_name, test_size, estimators):
    #set up training and testing split
    X_train, X_test, y_train, y_test = set_up_train_test_split(df, feature_list, target_name, test_size)
    
    #fit ridge classifier to x and y training set
    clf = RandomForestClassifier(n_estimators = estimators).fit(X_train, y_train)
    
    return clf

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