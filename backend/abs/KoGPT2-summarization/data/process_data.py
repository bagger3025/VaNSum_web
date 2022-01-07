import json
import pandas as pd
import numpy as np

DATA_JSONL = "aihub_article_train.jsonl"
DST_FILE = "train_aihub.tsv"
# DATA_JSONL = "aihub_article_valid.jsonl"
# DST_FILE = "test_aihub.tsv"


with open(DATA_JSONL, "r") as jsonl_file:
    json_str_list = list(jsonl_file)
json_list = []
for json_str in json_str_list:
    line = json.loads(json_str)
    json_list.append(line)
df = pd.DataFrame(json_list)
df = df.filter(["article_original", "abstractive"], axis=1)
df.rename(columns={"article_original":"news", "abstractive":"summary"}, inplace=True)
df["news"] = df.apply(lambda row: ' '.join(list(row["news"])), axis=1)

print(df.isna().sum())
print( df.loc[df.loc[:, "summary"].isna()] )

df.to_csv(DST_FILE, sep='\t', index=False)


df = pd.read_csv(DST_FILE, sep='\t')

print(df.isna().sum())
print( df.loc[df.loc[:, "summary"].isna()] )

df.dropna(inplace=True);
print(df.isna().sum())
print( df.loc[df.loc[:, "summary"].isna()] )
df.to_csv(DST_FILE, sep='\t', index=False)



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
