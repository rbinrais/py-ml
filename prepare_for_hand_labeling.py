import pandas as pd
from glob import glob
import random

csvs = glob("comments/*.csv")
for index, csv in enumerate(csvs):
    if index < 2:
        df = pd.read_csv(csv)
        df = df[["comment"]]
        df["labels"] = [random.choice(["L", "C"])
                        for _ in range(len(df))]
        df.to_csv(csv, index=False)
    else:
        df = pd.read_csv(csv)
        df = df[["comment"]]
        df["labels"] = -1
        df.to_csv(csv, index=False)
