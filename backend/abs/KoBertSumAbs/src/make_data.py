import os
import re
import kss
import json
import pandas as pd
from tqdm import tqdm
import argparse

# VaNSum_web/backend/abs/KoBertSumAbs
PROJECT_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')

DATA_DIR = f'{PROJECT_DIR}/ext/data'
RAW_DATA_DIR = f'{DATA_DIR}/raw'
JSON_DATA_DIR = f'{DATA_DIR}/json_data'
BERT_DATA_DIR = f'{DATA_DIR}/bert_data' 
LOG_DIR = f'{PROJECT_DIR}/ext/logs'
LOG_PREPO_FILE = f'{LOG_DIR}/preprocessing.log' 

def noise_remove(text):
    text = text.lower()

    # remove_redundant_white_spaces
    text = re.sub(' +', ' ', text)

    text = re.sub("“", '"', text)
    text = re.sub("”", '"', text)
    text = re.sub("‘", "'", text)
    text = re.sub("’", "'", text)

    return text

def preprocessing(text, tokenizer=None):
    text = noise_remove(text)
    if tokenizer is not None:
        text = tokenizer(text)
        text = ' '.join(text)

    return text

def korean_sent_spliter(doc):
    sents_splited = kss.split_sentences(doc)
    if len(sents_splited) == 1:
        return sents_splited
    else:  # kss로 분리가 된 경우(3문장 이상일 때도 고려)
        idx = 0
        while idx < len(sents_splited) - 1:
            # 두 문장 사이에 .이나 ?가 없는 경우: 그냥 붙여주기
            if not sents_splited[idx].endswith('다.') and not sents_splited[idx].endswith('?'):
                first_start = doc.find(sents_splited[idx])
                second_start = doc.find(sents_splited[idx + 1])
                if first_start != -1 and second_start != -1:
                    second_end = second_start + len(sents_splited[idx + 1])
                    sents_splited[idx] = doc[first_start:second_end]
                    del sents_splited[idx + 1]
                    idx -= 1
            idx += 1
        return sents_splited

def create_json_files(data_type, df, path=''):
    NUM_DOCS_IN_ONE_FILE = 1000

    assert data_type in ["train", "valid", "test"]

    for start_idx in tqdm(range(0, len(df), NUM_DOCS_IN_ONE_FILE)):
        end_idx = min(start_idx + NUM_DOCS_IN_ONE_FILE, len(df))
        json_list = []
        for _, row in df.iloc[start_idx:end_idx].iterrows():
            original_sents_list = [preprocessing(original_sent).split() for original_sent in row['article_original']]

            summary_sents_list = []
            if data_type != "test":
                summary_sents = korean_sent_spliter(noise_remove(row['abstractive']))   
                summary_sents_list = [preprocessing(original_sent).split() for original_sent in summary_sents]

            json_list.append({'src': original_sents_list, 'tgt': summary_sents_list})

        #정렬을 위해 앞에 0 채워주기
        length = len(str(len(df)))
        start_idx_str = (length - len(str(start_idx)))*'0' + str(start_idx)
        end_idx_str = (length - len(str(end_idx-1)))*'0' + str(end_idx-1)

        with open(f'{path}/{data_type}.{start_idx_str}_{end_idx_str}.json', 'w') as json_file:
            json_file.write(json.dumps(json_list, indent=4, ensure_ascii=False))

def load_data_from_jsonl(path):
    data = []
    with open(path, "r") as json_file:
        data_list = list(json_file)
    for json_str in data_list:
        line = json.loads(json_str)
        data.append(line)
    return data

def make_directory(path):
    if os.path.exists(path):
        os.system(f"rm {path}/*")
    else:
        os.mkdir(path)

def make_json_and_bert_file(data_type, df):
    # 동일한 파일명 존재하면 덮어쓰는게 아니라 폴더 내 삭제 후 만들어주기
    json_data_dir = f"{JSON_DATA_DIR}/{data_type}"
    make_directory(json_data_dir)

    # Convert json to bert.pt files
    bert_data_dir = f"{BERT_DATA_DIR}/{data_type}"
    make_directory(bert_data_dir)

    create_json_files(data_type, df, path=json_data_dir)

    os.system(f"python prepro/data_builder.py"
        + f" -mode format_to_bert -dataset {data_type} -model {args.model}"
        + f" -raw_path {json_data_dir}"
        + f" -save_path {bert_data_dir}"
        + f" -log_file {LOG_PREPO_FILE}"
        + f" -lower -n_cpus {args.n_cpus}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-n_cpus", default='2', type=str)
    parser.add_argument("-make_for", default='train', type=str, choices=['train', 'test'])
    parser.add_argument("-model", default='klue', type=str, choices=["kykim-bert", "klue"])
    args = parser.parse_args()

    # Convert raw data to df
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    # Make bert input file for train and valid from df file
    os.makedirs(JSON_DATA_DIR, exist_ok=True)
    os.makedirs(BERT_DATA_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    
    if args.make_for == "train":
        # import data
        trains = load_data_from_jsonl(f'{RAW_DATA_DIR}/train.jsonl')

        # Convert raw data to df
        df = pd.DataFrame(trains)
        train_df = df.sample(frac=0.95,random_state=42) # random split, random state is a seed value
        valid_df = df.drop(train_df.index)
        train_df.reset_index(inplace=True, drop=True)
        valid_df.reset_index(inplace=True, drop=True)

        print(f'train_df({len(train_df)}) is exported')
        print(f'valid_df({len(valid_df)}) is exported')

        for data_type, data_df in [('train', train_df), ('valid', valid_df)]:
            make_json_and_bert_file(data_type, data_df)

    elif args.make_for == 'test':
        tests = load_data_from_jsonl(f'{RAW_DATA_DIR}/extractive_test_v2.jsonl')
        test_df = pd.DataFrame(tests)
        print(f'test_df({len(test_df)}) is exported')
        make_json_and_bert_file("test", test_df)
