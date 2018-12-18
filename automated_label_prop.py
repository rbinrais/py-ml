import numpy as np
from sklearn import datasets
from sklearn.semi_supervised import LabelPropagation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import linear_model
import pandas as pd
import code
from glob import glob

def combine_data(dfs):
    df = pd.DataFrame()
    for tmp in dfs:
        df = df.append(tmp)
    df.index = list(range(len(df)))
    return df

def get_data():
    csvs = glob("comments/*.csv")
    dfs = [pd.read_csv(csv, index_col=False) for csv in csvs]
    return combine_data(dfs)

def clean_data(df):
    return df[pd.notnull(df["comment"])]

def generate_features(df):
    vectorizer = TfidfVectorizer()
    return vectorizer.fit_transform(df["comment"])

def encode_labels(x):
    if x["labels"] == "L":
        return 0
    if x["labels"] == "C":
        return 1
    if x["labels"] == -1:
        return -1

def decode_labels(x):
    if x == 0:
        return "L"
    if x == 1:
        return "C"

def generate_labels(df):    
    return df.apply(encode_labels, axis=1)

def label_propagation(df):
    X = generate_features(df)
    labels = generate_labels(df)
    label_prop_model = LabelPropagation()
    label_prop_model.fit(X.toarray(), labels)
    return label_prop_model.predict(X.toarray())

def get_new_labels(labels, df):
    new_labels = [decode_labels(elem) for elem in labels]
    df["labels"] = new_labels
    return df

def propagate_labels():
    df = get_data()
    df = clean_data(df)
    labels = label_propagation(df)
    return get_new_labels(labels, df)

def save_data(df, path):
    df.to_csv(path, index=False)

if __name__ == '__main__':
    df = propagate_labels()
    save_data(df, "labeled_data.csv")

# How to do this in general:
# we don't want to label everything at once (in the real world)
# how we should handle things:
# 1. predict some small amount of new labels, that are randomly chosen
# 1a. if this is intractable to analyze then take a sample
# 2. from your new labels check how well they match up with your ground truth dataset
#    So, if the proportion of labels is very different than your ground truth dataset
#    there may be something off (this may also be good, but it is likely not)
#    If they are very similar in proportion to your ground truth, pick some small set of
#    examples and compare semantically what it means to get this case.
# 3. do this again and again until you have reasonable confidence in your dataset
# 4. label the remaining data with your label propagation routinue

