import json
import pandas as pd
import time
import argparse

PROBLEM = 'ext'

## 사용할 path 정의
PROJECT_DIR = '..'

DATA_DIR = f'{PROJECT_DIR}/{PROBLEM}/data'
RAW_DATA_DIR = DATA_DIR + '/raw'
JSON_DATA_DIR = DATA_DIR + '/json_data'
BERT_DATA_DIR = DATA_DIR + '/bert_data' 
LOG_DIR = f'{PROJECT_DIR}/{PROBLEM}/logs'
LOG_PREPO_FILE = LOG_DIR + '/preprocessing.log' 

MODEL_DIR = f'{PROJECT_DIR}/{PROBLEM}/models' 
RESULT_DIR = f'{PROJECT_DIR}/{PROBLEM}/results' 

def write_six_sents(sent_id_list):

    test_pred_list = []
    _, sum_sents_idxes = sent_id_list.rsplit(r'[', maxsplit=1)
    sum_sents_idx_list = [ int(str.strip(i)) for i in sum_sents_idxes[:-2].split(', ')]
    test_pred_list.append({'sent_id': sum_sents_idx_list})

    result = []
    for i in range(len(test_pred_list)):
        result.append('{"sent_id": ['+', '.join(str(e) for e in test_pred_list[i]["sent_id"])+"]}\n")
    
    return json.loads(result[0])


# python make_submission.py result_1209_1236_step_7000.candidate
if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-matchsum_datapath", default=RAW_DATA_DIR + '/extractive_test_v2.jsonl', type=str)
    parser.add_argument("-candidate_path", default=None, required=True, type=str)
    parser.add_argument("-matchsum_resultpath", default=RESULT_DIR + '/extractive_six_sents.jsonl', type=str)
    args = parser.parse_args()

    # test set
    with open(args.matchsum_datapath, 'r') as json_file:
        json_list = list(json_file)

    tests = []
    for json_str in json_list:
        line = json.loads(json_str)
        tests.append(line)

    test_df = pd.DataFrame(tests)
    #print(test_df.head(4))
    # 추론결과
    with open(RESULT_DIR + '/' + args.candidate_path, 'r') as file:
        lines = file.readlines()
    # print(lines)
    test_pred_list = []
    for line in lines:
        sum_sents_text, sum_sents_idxes = line.rsplit(r'[', maxsplit=1)
        sum_sents_text = sum_sents_text.replace('<q>', '\n')
        sum_sents_idx_list = [ int(str.strip(i)) for i in sum_sents_idxes[:-2].split(', ')]
        
        test_pred_list.append({'sum_sents_tokenized': sum_sents_text, 
                            'sent_id': sum_sents_idx_list
                            })

    result_df = pd.merge(test_df, pd.DataFrame(test_pred_list), how="left", left_index=True, right_index=True)
    #result_df['summary'] = result_df.apply(lambda row: '\n'.join(list(np.array(row['article_original'])[row['sum_sents_idxes']])) , axis=1)
    #submit_df = pd.read_csv(RAW_DATA_DIR + '/extractive_sample_submission_v2.csv', encoding="cp949")
    #submit_df.drop(['summary'], axis=1, inplace=True)


    #print(result_df['id'].dtypes)
    #print(submit_df.dtypes)

    #result_df['id'] = result_df['id'].astype(int)
    #print(result_df['id'].dtypes)

    #submit_df  = pd.merge(submit_df, result_df.loc[:, ['id', 'sum_sents_idxes']], how="left", left_on="id", right_on="id")
    submit_df = result_df.loc[:, ['sent_id']]
    print(submit_df)
    print(submit_df.isnull().sum())

    ## 결과 통계치 보기
    # word
    #abstractive_word_counts = submit_df['summary'].apply(lambda x:len(re.split('\s', x)))
    #print(abstractive_word_counts.describe())

    # export
    now = time.strftime('%y%m%d_%H%M')
    #submit_df.to_csv(f'{RESULT_DIR}/submission_{now}.csv', index=False, encoding="utf-8-sig")
    with open(args.matchsum_resultpath, 'w') as file:
        for i in range(submit_df.shape[0]):
            file.write('{"sent_id": ['+', '.join(str(e) for e in submit_df.iloc[i]["sent_id"])+"]}\n")