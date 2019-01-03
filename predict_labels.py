import modeling
import pandas as pd
import joblib

def feature_size_pad(features):
    labeled_data = pd.read_csv("labeled_data.csv")
    labeled_features = generate_features(labeled_data)
    if features.shape[1] < labeled_features.shape[1]:
        difference_in_columns = labeled_features.shape[1] - features.shape[1]
        empty_df = np.zeros((features.shape[0], difference_in_columns))
        features.index = list(range(len(features)))
        empty_df.index = list(range(len(empty_df)))
        return pd.concat([features, empty_df], axis=1)
    elif features.shape[1] > labeled_features.shape[1]:
        columns_to_keep = list(range(labeled_features.shape[1]))
        return features[columns_to_keep]
    else:
        return features

def generate_features(df):
    features = modeling.do_word2vec(df["comments"])
    return modeling.feature_post_processing(features)

def generate_predictions():
    data = pd.read_csv("wikipedia/comments.csv")
    features = generate_features(data)
    features = feature_size_pad(features)
    clf = joblib.load("clf.joblib")
    labels = clf.predict(features)
    label_encoder = joblib.load("label_encoder.joblib")
    text_labels = label_encoder.inverse_transform(labels)
    data["labels"] = text_labels
    data.to_csv("predicted_labels.csv", index=False)

if __name__ == '__main__':
    generate_predictions()
