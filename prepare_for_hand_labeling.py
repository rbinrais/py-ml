import pandas as pd
from glob import glob
import random

def _get_csvs():
    return glob("comments/*.csv")

def _add_label_data(csv):
    df = pd.read_csv(csv)
    df = df[["comment"]]
    df["labels"] = [random.choice(["L", "C"])
                    for _ in range(len(df))]
    df.to_csv(csv, index=False)

def _add_unlabeled_data(csv):
    df = pd.read_csv(csv)
    df = df[["comment"]]
    df["labels"] = -1
    df.to_csv(csv, index=False)

def prepare_for_labeling():
    csvs = _get_csvs()
    for index, csv in enumerate(csvs):
        if index < 2:
            _add_label_data(csv)
        else:
            _add_unlabeled_data(csv)

if __name__ == '__main__':
    prepare_for_labeling()
