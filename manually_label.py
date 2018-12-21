import pandas as pd

def get_csv(folder, filename):
    path = folder+"/"+filename
    return pd.read_csv(path)

def hand_label(df):
    """
    Asks an end user to hand label each comment as
    * syntax
    OR
    * semantics
    """
    df["labels"] = -1
    for index in df.index:
        print(df.loc[index])
        label = input("what label should this have?")
        if label == '-1':
            break
        df.loc[index, ["labels"]] = label
    return df

def auto_label(df):
    """
    Auto labels remaining comments as -1 for label propagation
    """
    for i in range(index, max(df.index)):
        df.loc[i]["labels"] = -1
    return df

def write_csv(folder, filename):
    path = folder+"/"+filename
    df.to_csv(path, index=False)

def ask_for_labels(folder, filename):
    df = get_csv(folder, filename)
    df = hand_label(df)
    df = auto_label(df)
    write_csv(df)

if __name__ == '__main__':
    ask_for_labels("wikipedia", "comments.csv")
