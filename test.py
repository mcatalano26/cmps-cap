import pickle
from compress_pickle import dump, load
import pandas as pd

boo = False
stringy = 'This is a !!fucking. long string'
words_in_string = stringy.split()
punctuation_lst = [',', '.', '!', '?', '<', '>', '/', ':', ';', '\'', '\"', '[', '{', ']', '}', '|', '\\', '`', '~', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+']
swearwords_df = pd.read_csv('files/edited-swear-words.csv')
swearwords = swearwords_df.swear.tolist()
for word in words_in_string:
    for letter in word:
        if letter in punctuation_lst:
            word = word.replace(letter, "")
    if word in swearwords:
        boo = True

if boo:
    print('swear word is detected in stringy')
else:
    print('no swear word found')

stringy = 'THIS IS A caps STRING'

stringy = stringy.lower()
print(stringy)