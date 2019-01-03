from sklearn.svm import SVC
from gensim.sklearn_api import W2VTransformer
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import joblib
import azure_helper

def load_data_from_blob(file_name,retain_file=True):
    azure_helper.download_from_blob(file_name,file_name)
    data = pd.read_csv(file_name)
    if retain_file == False:
        os.remove(file_name)
    return data

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
    encoded_labels = label_encoder.fit_transform(labels) 
    return encoded_labels, label_encoder

def feature_post_processing(features):
    features.fillna(0, axis=1, inplace=True)
    return features.T

def generate_clf(csv):
    df = load_data_from_blob(csv)
    features = do_word2vec(df["comments"])
    features = feature_post_processing(features)
    labels, encoder = transform_labels(df["labels"])
    clf = SVC(class_weight="balanced",
        tol=1e-5,
        gamma="scale",
        kernel="sigmoid",
        random_state=42,
        C=0.8)
    clf.fit(features, labels)
    
    model_file_name = 'clf.joblib'
    joblib.dump(clf, model_file_name)
    encoder_file_name = 'label_encoder.joblib'
    joblib.dump(encoder, encoder_file_name)
    
    azure_helper.upload_to_blob(model_file_name,model_file_name)
    azure_helper.upload_to_blob(encoder_file_name,encoder_file_name)
    

if __name__ == '__main__':
    generate_clf("labeled_data.csv")

# automate feature post processing
# add padding array function
# create label decoder function
