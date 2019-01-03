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
        dicter = df.loc[index].to_dict()
        for key in dicter:
            print(key, ":", dicter[key])
        label = input("what label should this have?")
        if label == '-1':
            break
        df.loc[index, ["labels"]] = label
    return df, index

def auto_label(df, index):
    """
    Auto labels remaining comments as -1 for label propagation
    """
    for i in range(index, max(df.index)):
        df.loc[i]["labels"] = -1
    return df

def write_csv(df, folder, filename):
    path = folder+"/"+filename
    df.to_csv(path, index=False)

def ask_for_labels(folder, filename):
    df = get_csv(folder, filename)
    df, index = hand_label(df)
    df = auto_label(df, index)
    name, ext = filename.split(".")
    name += "with_labels"
    filename = name + ext
    write_csv(df, folder, filename)

if __name__ == '__main__':
    ask_for_labels("wikipedia", "comments.csv")
