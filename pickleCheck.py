import pickle
import pandas as pd
import random
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from compress_pickle import dump, load

prior_df = pd.read_csv('files/compiled_comments_3_14_2021.csv')
prior_df['Label'] = prior_df['action']
prior_df = prior_df.drop(['action'], axis = 1)
prior_df = prior_df.replace({'Label': {False: 0, True: 1}})

valid_df = pd.read_csv('validation/Validation Comments - Sheet1.csv')

def set_up_train_test_split(prior_df, valid_df, feature_list, target_name, test_size):
    valid_X = valid_df[feature_list]

    prior_X = prior_df[feature_list]

    valid_y = valid_df[target_name]

    prior_y = prior_df[target_name]

    rand_state = random.randint(0, 1000)
    valid_X_train, valid_X_test, valid_y_train, valid_y_test = train_test_split(valid_X, valid_y, test_size = test_size, random_state=rand_state)
    X_train, X_test, y_train, y_test = train_test_split(prior_X, prior_y, test_size = test_size, random_state=rand_state)
    
    for i in range(1,5):
        X_train = X_train.append(valid_X_train, ignore_index = True)
        y_train = y_train.append(valid_y_train, ignore_index = True)

        X_test = X_test.append(valid_X_test, ignore_index = True)
        y_test = y_test.append(valid_y_test, ignore_index = True)
        
    return X_train, X_test, y_train, y_test


def determine_accuracy(y_test, y_val):
    percent_arr = (y_test == y_val)
    count = np.count_nonzero(percent_arr)
    percentage = (count/(len(percent_arr)))*100
    return percentage

from sklearn.ensemble import RandomForestClassifier
#Random Forest Classifier
def random_forest_class_func(prior_df, valid_df, feature_list, target_name, test_size, estimators, model_name):
    #set up training and testing split
    X_train, X_test, y_train, y_test = set_up_train_test_split(prior_df, valid_df, feature_list, target_name, test_size)

    #Send X_train to file for visualization later
    np.savetxt('files/X_train.csv', X_train, delimiter = ',')
    
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


features = ['profanity', 'length', 'adjWordScore', 'NER_count', 'NER_match', 'WordScore', 'WholeScore', 'contains_url', 'no_url_WordScore', 'no_url_WholeScore', 'WordScoreNoStop', 'WholeScoreNoStop', 'no_url_or_stops_WholeScore', 'no_url_or_stops_WordScore']
random_forest_class_func(prior_df, valid_df, features, 'Label', 0.1, 1000, 'updated_model.pkl')