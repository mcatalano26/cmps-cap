import pickle
from compress_pickle import dump, load
import pandas as pd
import numpy as np

import lime
from lime import lime_tabular

features = ['length', 'adjWordScore', 'NER_count', 'NER_match', 'WordScore', 'WholeScore', 'contains_url', 'no_url_WordScore', 'no_url_WholeScore', 'WordScoreNoStop', 'WholeScoreNoStop', 'no_url_or_stops_WholeScore', 'no_url_or_stops_WordScore']

our_model = load("latest_model.pkl", compression="lzma", set_default_extension=False)
new_X_train = np.loadtxt('files/X_train.csv', delimiter = ',')
new_X_train

explainer = lime_tabular.LimeTabularExplainer(
    training_data=np.array(new_X_train),
    feature_names=features,
    class_names=[False, True],
    mode='classification'
)

exp = explainer.explain_instance(
    data_row=new_X_train[1], 
    predict_fn=our_model.predict_proba
)

variab = exp.as_html()
print(variab)

print('\n\n\n\n\n')
print('Made it')