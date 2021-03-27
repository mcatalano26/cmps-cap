import pickle
import pandas as pd
import random
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from compress_pickle import dump, load

comments_df = pd.read_csv('files/compiled_comments_3_14_2021.csv')

def set_up_train_test_split(df, feature_list, target_name, test_size):
    X = df[feature_list]
    X = X.to_numpy()
    y = df[target_name]
    y = y.to_numpy()
    rand_state = random.randint(0, 1000)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = test_size, random_state=rand_state)
    return X_train, X_test, y_train, y_test

def determine_accuracy(y_test, y_val):
    percent_arr = (y_test == y_val)
    count = np.count_nonzero(percent_arr)
    percentage = (count/(len(percent_arr)))*100
    return percentage

from sklearn.ensemble import RandomForestClassifier
#Random Forest Classifier
def random_forest_class_func(df, feature_list, target_name, test_size, estimators, model_name):
    #set up training and testing split
    X_train, X_test, y_train, y_test = set_up_train_test_split(df, feature_list, target_name, test_size)
    
    #fit ridge classifier to x and y training set
    clf = RandomForestClassifier(n_estimators = estimators).fit(X_train, y_train)
    
    #pickle the model
    fname1 = model_name
    #dump(clf, fname1)
    dump(clf, fname1, compression="lzma", set_default_extension=False)
    
    #Predict with ridge classifier on x and y testing set
    y_val = clf.predict(X_test)
    
    #report the correct percentage of predictions
    percentage = determine_accuracy(y_test, y_val)
    
    print('Percentage correct: ' + str(percentage) + '\n')


features = ['adjWordScore', 'NER_count', 'NER_match', 'WordScore', 'WholeScore', 'contains_url', 'no_url_WordScore', 'no_url_WholeScore', 'WordScoreNoStop', 'WholeScoreNoStop', 'no_url_or_stops_WholeScore', 'no_url_or_stops_WordScore']
random_forest_class_func(comments_df, features, 'action', 0.1, 1000, 'latest_model.pkl')