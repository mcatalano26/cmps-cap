For Milestone 3:

To help you understand how our code is structured, I will describe it here. All of our currently working code is in Jupyter Notebook format. There are 5 Notebooks in this repository as of 11/13/2020. Here is a description of each file:

FullPipeline:
This is the best notebook to look at to get the most general picture of our project. The code here goes step by step through data collection, feature creation, and the running of our machine learning model.

Early Work:
This file can be almost completely ignored by anyone trying to learn about our project. This file was used in the very early stages of development and doesn't have much cohesion to it. It is mostly just us trying different things and seeing what does and doesn't work. All of the code that works has been put into more structured notebooks.

Article Scraping and Ner:
This file contains our initial attempts at scraping reddit and using NER and wordnet to create features for our machine learning model. Everything that is functioning here can be found in the FullPipeline notebook.

MachineLearning:
This is a small, standalone notebook that anyone who is curious about the results of our machine learning tests can run. Running this to test the machine learning functionality will be much quicker than running the FullPipeline as there is no scraping or feature creation necessary.

Upvote Predictor:
The upvote predictor is a machine learning model built using this tutorial: https://towardsdatascience.com/predicting-reddit-comment-karma-a8f570b544fc. We wanted to build something to compare our eventual results with and this also helped us learn what we needed to do when building our model.
