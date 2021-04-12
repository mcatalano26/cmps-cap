import pickle
from compress_pickle import dump, load
import pandas as pd

print('Starting\n')
swearwords_df = pd.read_csv('files/edited-swear-words.csv')
swearwords = swearwords_df.swear.tolist()
features = ['length', 'adjWordScore', 'NER_count', 'NER_match', 'WordScore', 'WholeScore', 'contains_url', 'no_url_WordScore', 'no_url_WholeScore', 'WordScoreNoStop', 'WholeScoreNoStop', 'no_url_or_stops_WholeScore', 'no_url_or_stops_WordScore']
our_model = load("latest_model.pkl", compression="lzma", set_default_extension=False)
print('Finished!')