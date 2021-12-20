import json
import os
import pandas as pd
import time
import sys
import argparse
import numpy as np
import re

PROJECT_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')

DATA_DIR = f'{PROJECT_DIR}/ext/data'
RAW_DATA_DIR = DATA_DIR + '/raw'

RESULT_DIR = f'{PROJECT_DIR}/ext/results' 

def process_candiate_file(test_from_candidate):
    print(test_from_candidate)
    with open(test_from_candidate, 'r') as file:
        lines = file.readlines()
    test_pred_list = []
    
    # for line in lines:
    #     sum_sents_text, sum_sents_idxes = line.rsplit(r'[', maxsplit=1)
    #     sum_sents_text = sum_sents_text.replace('<q>', '\n')
    #     sum_sents_idx_list = [ int(str.strip(i)) for i in sum_sents_idxes[:-2].split(', ')]
    #     test_pred_list.append({'sum_sents_tokenized': sum_sents_text, 
    #                         'sum_sents_idxes': sum_sents_idx_list
    #                         })

    for line in lines:
        sum_sents_text, sum_sents_idxes, sum_sents_xent = line.rsplit(r'[', maxsplit=2)
        sum_sents_text = sum_sents_text.replace('<q>', '\n')
        sum_sents_text = sum_sents_text.split('\n')
        sum_sents_idx_list = [ int(str.strip(i)) for i in sum_sents_idxes[:-1].split(', ')]
        sum_sents_xent_list = [ float(str.strip(i)) for i in sum_sents_xent[:-2].split(', ')]
        # sum_sents_xent_list = list(np.array(sum_sents_xent_list)[sum_sents_idx_list])
        temp = [sum_sents_idx_list[i] - 1 for i in range(len(sum_sents_idx_list))]
        sum_sents_xent_list = list(np.array(sum_sents_xent_list)[temp])
        # sum_sents_xent_list2 = [0 for i in range(len(sum_sents_idx_list))]
        # for i in range(len(sum_sents_idx_list)):
        #     sum_sents_xent_list2[sum_sents_idx_list[i]] = sum_sents_xent_list[i]
        test_pred_list.append({'sum_sents_tokenized': sum_sents_text, 
                            'sum_sents_idxes': sum_sents_idx_list,
                            'sum_sents_xent': sum_sents_xent_list
                            })
    print("done")
    return test_pred_list

def read_jsonl_file(path):
    with open(path, 'r', encoding='utf-8') as json_file:
        json_list = list(json_file)
    tests = []
    for json_str in json_list:
        line = json.loads(json_str)
        tests.append(line)
    test_df = pd.DataFrame(tests)
    return test_df

# python make_submission.py result_1209_1236_step_7000.candidate
if __name__ == '__main__':
    now = time.strftime('%y%m%d_%H%M')
    parser = argparse.ArgumentParser()
    parser.add_argument("-test_from_candidate", default='2', type=str)
    parser.add_argument("-test_from_jsonl", default='0', type=str)
    parser.add_argument("-test_for", type=str, choices=["dacon", "matchsum", "rouge_test"], default="dacon")
    parser.add_argument("-save_to", type=str, default=f'{RESULT_DIR}/submission_{now}.csv')
    args = parser.parse_args()

    # test set
    test_df = read_jsonl_file(args.test_from_jsonl)

    # 추론결과
    test_pred_list = process_candiate_file(args.test_from_candidate)

    print(test_pred_list)
    
    if args.test_for == "dacon":
        result_df = pd.merge(test_df, pd.DataFrame(test_pred_list), how="left", left_index=True, right_index=True)
        result_df['summary'] = result_df.apply(lambda row: '\n'.join(list(np.array(row['article_original'])[row['sum_sents_idxes']])) , axis=1)
        
        submit_df = pd.read_csv(RAW_DATA_DIR + '/extractive_sample_submission_v2.csv', encoding='cp949')
        submit_df.drop(['summary'], axis=1, inplace=True)

        print(result_df['id'].dtypes)
        print(submit_df.dtypes)

        result_df['id'] = result_df['id'].astype(int)
        print(result_df['id'].dtypes)

        submit_df  = pd.merge(submit_df, result_df.loc[:, ['id', 'summary']], how="left", left_on="id", right_on="id")
        print(submit_df.isnull().sum())

        ## 결과 통계치 보기
        # word
        abstractive_word_counts = submit_df['summary'].apply(lambda x:len(re.split('\s', x)))
        print(abstractive_word_counts.describe())

        # export
        now = time.strftime('%y%m%d_%H%M')
        submit_df.to_csv(args.save_to, index=False, encoding="utf-8-sig")


    elif args.test_for == "rouge_test":
        result_df = pd.merge(test_df, pd.DataFrame(test_pred_list), how="left", left_index=True, right_index=True)
        result_df['summary'] = result_df.apply(lambda row: list(np.array(row['article_original'])[row['sum_sents_idxes']]), axis=1)
        result_df = result_df.filter(["id", "summary"], axis=1)
        result_df.to_json(args.save_to.rsplit(".", 1)[0] + ".jsonl", orient="records", lines=True, force_ascii=False)

    elif args.test_for == "matchsum":
        new_index_list = []
        for ele in test_pred_list:
            new_index_list.append(json.dumps({"sent_id": ele["sum_sents_idxes"]}))
        with open(args.save_to, "w") as f:
            for ele in new_index_list:
                f.write(ele + "\n")