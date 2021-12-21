import os
import sys
sys.path.append(os.path.join(sys.path[0], "mKoBertSum", "src"))
sys.path.append(os.path.join(sys.path[0], "mKoBertSum", "src", "models"))
sys.path.append(os.path.join(sys.path[0], "mKoBertSum", "src", "prepro"))

import argparse
import datetime
import numpy as np
import torch
import data_builder
from train import test

PROBLEM = 'ext'
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

DATA_DIR = f'{PROJECT_DIR}/{PROBLEM}/data'
RAW_DATA_DIR = DATA_DIR + '/raw'
JSON_DATA_DIR = DATA_DIR + '/json_data'
BERT_DATA_DIR = DATA_DIR + '/bert_data' 
LOG_DIR = f'{PROJECT_DIR}/{PROBLEM}/logs'
LOG_PREPO_FILE = LOG_DIR + '/preprocessing.log' 

MODEL_DIR = f'{PROJECT_DIR}/{PROBLEM}/models' 
RESULT_DIR = f'{PROJECT_DIR}/{PROBLEM}/results' 

def preload():
    args = {"dataset": 'test', "with_title": False, "log_file": LOG_PREPO_FILE, 'lower': True, 'map_path': '../../data/', 'max_src_nsents': 120, 'max_src_ntokens_per_sent': 300, 'max_tgt_ntokens': 500, 'min_src_nsents': 1, 'min_src_ntokens_per_sent': 1, 'min_tgt_ntokens': 1, 'mode': 'format_to_bert', 'n_cpus': 2, 'pretrained_model': 'bert', 'raw_path': f'{JSON_DATA_DIR}/test', 'save_path': f'{BERT_DATA_DIR}/test', 'select_mode': 'greedy', 'shard_size': 2000, 'use_bert_basic_tokenizer': False}
    args = argparse.Namespace(**args)
    bertData = data_builder.BertData(args)
    trainer = test(True)
    return bertData, trainer

def preload_with_title():
    args = {"dataset": 'test', "with_title": True,"log_file": f'{LOG_DIR}/preprocessing.log', 'lower': True, 'map_path': '../../data/', 'max_src_nsents': 120, 'max_src_ntokens_per_sent': 300, 'max_tgt_ntokens': 500, 'min_src_nsents': 1, 'min_src_ntokens_per_sent': 1, 'min_tgt_ntokens': 1, 'mode': 'format_to_bert', 'n_cpus': 2, 'pretrained_model': 'bert', 'raw_path': f'{JSON_DATA_DIR}/test', 'save_path': f'{BERT_DATA_DIR}/test', 'select_mode': 'greedy', 'shard_size': 2000, 'use_bert_basic_tokenizer': False}
    args = argparse.Namespace(**args)
    bertData = data_builder.BertData(args)
    trainer = test(True, with_title=True)
    return bertData, trainer

def bertSum(models, sort_by_pred=True, n_sents=3, block_trigram=True):
    bertData, trainer = models
    bertData = data_builder.dataPrepro(bertData)
    index = test(False, bertData, trainer, block_trigram=block_trigram)
    with open(f"{RESULT_DIR}/result_0727_0000_step_0.candidate") as file:
        lines = file.readlines()
    for line in lines:
        sum_sents_text, sum_sents_idxes, sum_sents_xent = line.rsplit(r'[', maxsplit=2)
        sum_sents_text = sum_sents_text.replace('<q>', '\n')
        sum_sents_text = sum_sents_text.split('\n')
        sum_sents_idx_list = [ int(str.strip(i)) for i in sum_sents_idxes[:-1].split(', ')]
        sum_sents_xent_list = [ float(str.strip(i)) for i in sum_sents_xent[:-2].split(', ')]
        sum_sents_xent_list = list(np.array(sum_sents_xent_list)[sum_sents_idx_list])

        length = min(len(sum_sents_text), len(sum_sents_idx_list))
        sum_sents_text = sum_sents_text[:length]
        sum_sents_idx_list = sum_sents_idx_list[:length]
        sum_sents_xent_list = sum_sents_xent_list[:length]
        sum_sents_text = sum_sents_text[:n_sents]
        sum_sents_idx_list = sum_sents_idx_list[:n_sents]
        sum_sents_xent_list = sum_sents_xent_list[:n_sents]


        if not sort_by_pred:
            temp_list = []
            for i in range(min(n_sents, length)):
                temp = (sum_sents_idx_list[i], sum_sents_text[i], sum_sents_xent_list[i])
                temp_list.append(temp)
            temp_list.sort(key=lambda tup: tup[0])
            
            for i in range(n_sents):
                sum_sents_idx_list[i] = temp_list[i][0] 
                sum_sents_text[i] = temp_list[i][1]
                sum_sents_xent_list[i] = temp_list[i][2]
        
        return sum_sents_text[:n_sents], sum_sents_idx_list[:n_sents], sum_sents_xent_list[:n_sents]

def bertSum_with_title(models, sort_by_pred=True, n_sents=3, block_trigram=True):
    bertData, trainer = models
    bertData = data_builder.dataPrepro(bertData)
    index = test(False, bertData, trainer, block_trigram=block_trigram)

    with open(f"{RESULT_DIR}/result_0919_0000_step_0.candidate") as file:
        lines = file.readlines()
    for line in lines:
        sum_sents_text, sum_sents_idxes, sum_sents_xent = line.rsplit(r'[', maxsplit=2)
        sum_sents_text = sum_sents_text.replace('<q>', '\n')
        sum_sents_text = sum_sents_text.split('\n')
        sum_sents_idx_list = [ int(str.strip(i)) for i in sum_sents_idxes[:-1].split(', ')]
        sum_sents_xent_list = [ float(str.strip(i)) for i in sum_sents_xent[:-2].split(', ')]
        sum_sents_xent_list = list(np.array(sum_sents_xent_list)[sum_sents_idx_list])

        length = min(len(sum_sents_text), len(sum_sents_idx_list))
        sum_sents_text = sum_sents_text[:length]
        sum_sents_idx_list = sum_sents_idx_list[:length]
        sum_sents_xent_list = sum_sents_xent_list[:length]
        sum_sents_text = sum_sents_text[:n_sents]
        sum_sents_idx_list = sum_sents_idx_list[:n_sents]
        sum_sents_xent_list = sum_sents_xent_list[:n_sents]


        if not sort_by_pred:
            temp_list = []
            for i in range(min(n_sents, length)):
                temp = (sum_sents_idx_list[i], sum_sents_text[i], sum_sents_xent_list[i])
                temp_list.append(temp)
            temp_list.sort(key=lambda tup: tup[0])
            
            for i in range(n_sents):
                sum_sents_idx_list[i] = temp_list[i][0] 
                sum_sents_text[i] = temp_list[i][1]
                sum_sents_xent_list[i] = temp_list[i][2]
        
        return sum_sents_text[:n_sents], sum_sents_idx_list[:n_sents], sum_sents_xent_list[:n_sents]

if __name__ == "__main__":
    models = preload()
    bertSum(models, sort_by_pred=True, n_sents=6, block_trigram=False)
