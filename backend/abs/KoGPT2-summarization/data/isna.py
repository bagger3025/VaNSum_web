import json
import pandas as pd
import numpy as np

# DATA_JSONL = "aihub_article_train.jsonl"
# DST_FILE = "train_aihub.tsv"
DATA_JSONL = "aihub_article_valid.jsonl"
DST_FILE = "test_aihub.tsv"



df = pd.read_csv(DST_FILE, sep='\t')

print(df.isna().sum())
print( df.loc[df.loc[:, "summary"].isna()] )


# with open("aihub_article_valid.jsonl", "r") as file, open("test_aihub.tsv", "w") as write_file:
#     write_file.write("news\tsummary\n")
#     i = 0
#     for f in file:
#         i += 1
#         k = json.loads(f)
#         file_string = " ".join(k["article_original"]).replace("\n", " ") + "\t" + k["abstractive"].replace("\n", " ") + "\n"
#         if len(file_string.split("\t")) != 2:
#             print("FOUND!")
#             print(k)
#             continue
#         write_file.write(file_string)
