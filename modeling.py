from sklearn.svm import SVC
from gensim.sklearn_api import W2VTransformer, TfIdfTransformer, PhrasesTransformer
from sklearn.pipeline import Pipeline
import pandas as pd
from sklearn.manifold import TSNE
import numpy as np
from scipy.stats import norm
from keras import backend as K
from keras.layers import Input, Dense, Lambda, Layer, Add, Multiply
from keras.models import Model, Sequential
from sklearn.preprocessing import LabelEncoder
import code
import random
import time
import re
from nltk.corpus import stopwords
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import FeatureUnion
import joblib

def tokenize(data):
    sentences = []
    for sentence in data:
        sentences.append(sentence.split(" "))
    return sentences

def fit_transform(model, data):
    df = pd.DataFrame()
    fitted_model = model.fit(data)
    for datum in data:
        df = pd.concat([df, pd.DataFrame(fitted_model.transform(datum))], axis=1)
    return df

# improvement: add BERT support - https://github.com/Separius/BERT-keras
# improvement: add ELMo support
def do_word2vec(data):
    data = tokenize(data)
    features = pd.DataFrame()
    model = W2VTransformer(size=1, min_count=1, seed=42)
    return fit_transform(model, data)

class TextSelector(BaseEstimator, TransformerMixin):
    """
    Transformer to select a single column from the data frame to perform additional transformations on
    Use on text columns in the data
    """
    def __init__(self, key):
        self.key = key

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[self.key]
    
class NumberSelector(BaseEstimator, TransformerMixin):
    """
    Transformer to select a single column from the data frame to perform additional transformations on
    Use on numeric columns in the data
    """
    def __init__(self, key):
        self.key = key

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return X[[self.key]]

#creating a function to encapsulate preprocessing, to mkae it easy to replicate on  submission data
def processing(df):
    stopWords = set(stopwords.words('english'))
    #lowering and removing punctuation
    df['processed'] = df['text'].apply(lambda x: re.sub(r'[^\w\s]','', x.lower()))
    
    #numerical feature engineering
    #total length of sentence
    df['length'] = df['processed'].apply(lambda x: len(x))
    #get number of words
    df['words'] = df['processed'].apply(lambda x: len(x.split(' ')))
    df['words_not_stopword'] = df['processed'].apply(lambda x: len([t for t in x.split(' ') if t not in stopWords]))
    #get the average word length
    df['avg_word_length'] = df['processed'].apply(lambda x: np.mean([len(t) for t in x.split(' ') if t not in stopWords]) if len([len(t) for t in x.split(' ') if t not in stopWords]) > 0 else 0)
    #get the average word length
    df['commas'] = df['text'].apply(lambda x: x.count(','))
    return(df)

def feature_selection(features):
    features.dropna(axis=1, inplace=True)
    rows, cols = features.shape
    percentages = [0.5, 0.6, 0.7, 0.8, 0.9]
    percentage = random.choice(percentages)
    n_components = int(cols * percentage)
    return TSNE(n_components=n_components).fit_transform(features)

def transform_labels(labels):
    label_encoder = LabelEncoder()
    return label_encoder.fit_transform(labels)

def do_classification(features, labels):
    clf = SVC(
        class_weight="balanced",
        tol=1e-5,
        gamma="scale",
        kernel="sigmoid",
        random_state=42,
        C=0.8
    )
    clf.fit(features, labels)
    return clf
    
if __name__ == '__main__':
    df = pd.read_csv("labeled_data.csv")
    # df["text"] = df["comments"]
    # df.drop("comments", axis=1)
    # df = processing(df)
    # df.drop("text", axis=1)
    # df.drop("labels", axis=1)
    # df.drop("processed", axis=1)
    
    text = Pipeline([
        ('selector', TextSelector(key='processed')),
        ('tfidf', TfidfVectorizer( stop_words='english'))
    ])
    
    length =  Pipeline([
        ('selector', NumberSelector(key='length')),
        ('standard', StandardScaler())
    ])
    words =  Pipeline([
        ('selector', NumberSelector(key='words')),
        ('standard', StandardScaler())
    ])
    words_not_stopword =  Pipeline([
        ('selector', NumberSelector(key='words_not_stopword')),
        ('standard', StandardScaler())
    ])
    avg_word_length =  Pipeline([
        ('selector', NumberSelector(key='avg_word_length')),
        ('standard', StandardScaler())
    ])
    commas =  Pipeline([
        ('selector', NumberSelector(key='commas')),
        ('standard', StandardScaler()),
    ])

    feats = FeatureUnion([
        ('text', text), 
        ('length', length),
        ('words', words),
        ('words_not_stopword', words_not_stopword),
        ('avg_word_length', avg_word_length),
        ('commas', commas),
    ])

    pipeline = Pipeline([
        ('feats', feats),
        ('classifier', SVC(class_weight="balanced",
                           tol=1e-5,
                           gamma="scale",
                           kernel="sigmoid",
                           random_state=42,
                           C=0.8))
    ])

    #labels = transform_labels(df["labels"])
    #pipeline.fit(df, labels)
    #joblib.dump(pipeline, 'text_classification_pipeline.joblib')
    # feature_processing.fit_transform(X_train)

    # features = do_feature_engineering(df["comments"])
    # #features = feature_selection(features, method="tsne")
    # labels = transform_labels(df["labels"])
    # clf = do_classification(features, labels)

    features = do_word2vec(df["comments"])
    features.fillna(0, axis=1, inplace=True)
    features = features.T
    labels = transform_labels(df["labels"])
    clf = SVC(class_weight="balanced",
        tol=1e-5,
        gamma="scale",
        kernel="sigmoid",
        random_state=42,
        C=0.8)
    clf.fit(features, labels)
    joblib.dump(clf, 'clf.joblib')
