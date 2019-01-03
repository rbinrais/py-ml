from sklearn.svm import SVC
from gensim.sklearn_api import W2VTransformer
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
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

def transform_labels(labels):
    label_encoder = LabelEncoder()
    return label_encoder.fit_transform(labels)

def feature_post_processing(features):
    features.fillna(0, axis=1, inplace=True)
    return features.T

def generate_clf(csv):
    df = pd.read_csv(csv)
    features = do_word2vec(df["comments"])
    features = feature_post_processing(features)
    labels = transform_labels(df["labels"])
    clf = SVC(class_weight="balanced",
        tol=1e-5,
        gamma="scale",
        kernel="sigmoid",
        random_state=42,
        C=0.8)
    clf.fit(features, labels)
    joblib.dump(clf, 'clf.joblib')

if __name__ == '__main__':
    generate_clf("labeled_data.csv")

# automate feature post processing
# add padding array function
# create label decoder function
