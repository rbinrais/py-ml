import modeling
import pandas as pd
import joblib
import azure_helper 
import os
import numpy as np

def load_data_from_blob(file_name,retain_file=True):
    azure_helper.download_from_blob(file_name,file_name)
    data = pd.read_csv(file_name)
    if retain_file == False:
        os.remove(file_name)
    return data

def feature_size_pad(features):
    labeled_data = load_data_from_blob("labeled_data.csv") #pd.read_csv("labeled_data.csv")
    labeled_features = generate_features(labeled_data)
    if features.shape[1] < labeled_features.shape[1]:
        difference_in_columns = labeled_features.shape[1] - features.shape[1]
        empty_df = pd.DataFrame(np.zeros((features.shape[0], difference_in_columns)))
        features.index = list(range(len(features)))
        empty_df.index = list(range(len(empty_df)))
        return pd.concat([features, empty_df], axis=1)
    # TODO think about how to handle this properly so we don't lose any features
    elif features.shape[1] > labeled_features.shape[1]:
        columns_to_keep = list(range(labeled_features.shape[1]))
        return features[columns_to_keep]
    else:
        return features

def generate_features(df):
    features = modeling.do_word2vec(df["comments"])
    return modeling.feature_post_processing(features)

def generate_predictions():
    data = load_data_from_blob("comments.csv") #pd.read_csv("wikipedia/comments.csv")
    features = generate_features(data)
    features = feature_size_pad(features)
    model_file = "clf.joblib" 
    azure_helper.download_from_blob(model_file,model_file)
    label_encoder_file = "label_encoder.joblib"
    azure_helper.download_from_blob(label_encoder_file,label_encoder_file)
    clf = joblib.load(model_file)
    labels = clf.predict(features)
    label_encoder = joblib.load(label_encoder_file)
    text_labels = label_encoder.inverse_transform(labels)
    data["labels"] = text_labels
    data.to_csv("predicted_labels.csv", index=False)

if __name__ == '__main__':
    generate_predictions()
