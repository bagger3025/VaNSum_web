import os
import sys
import time
sys.path.append("/home/vaiv2021/shbin/TestSite/mKoBertSum/src")
sys.path.append("/home/vaiv2021/shbin/TestSite/mKoBertSum/src/models")
sys.path.append("/home/vaiv2021/shbin/TestSite/mKoBertSum")
sys.path.append("/home/vaiv2021/shbin/TestSite/mKoBertSum/src/prepro")
sys.path.append("/home/skkuedu/TestSite/mKoBertSum/src/prepro")
import argparse
import json
import datetime
import pandas as pd
import numpy as np
import torch
import data_builder
from itertools import permutations
import re
from transformers import XLNetTokenizer, BertTokenizer
from train import test
from konlpy.tag import Kkma
PROBLEM = 'ext'


PROJECT_DIR = os.getcwd()

DATA_DIR = f'{PROJECT_DIR}/{PROBLEM}/data'
RAW_DATA_DIR = DATA_DIR + '/raw'
JSON_DATA_DIR = DATA_DIR + '/json_data'
BERT_DATA_DIR = DATA_DIR + '/bert_data' 
LOG_DIR = f'{PROJECT_DIR}/{PROBLEM}/logs'
LOG_PREPO_FILE = LOG_DIR + '/preprocessing.log' 

MODEL_DIR = f'{PROJECT_DIR}/{PROBLEM}/models' 
RESULT_DIR = f'{PROJECT_DIR}/{PROBLEM}/results' 


def showTime():
    now = datetime.datetime.now()
    print(now)


def preload():
    args = {"dataset": 'test', "log_file": '../ext/logs/preprocessing.log', 'lower': True, 'map_path': '../../data/', 'max_src_nsents': 120, 'max_src_ntokens_per_sent': 300, 'max_tgt_ntokens': 500, 'min_src_nsents': 1, 'min_src_ntokens_per_sent': 1, 'min_tgt_ntokens': 1, 'mode': 'format_to_bert', 'n_cpus': 2, 'pretrained_model': 'bert', 'raw_path': '../ext/data/json_data/test', 'save_path': '../ext/data/bert_data/test', 'select_mode': 'greedy', 'shard_size': 2000, 'use_bert_basic_tokenizer': False}
    args = argparse.Namespace(**args)
    bertData = data_builder.BertData(args)
    trainer = test(True)
    return bertData, trainer

def bertSum(models, sort_by_pred=True, n_sents=3, block_trigram=True):
    bertData, trainer = models
    # start = time.time()
    bertData = data_builder.dataPrepro(bertData)
    # print("kobertsum preprocess ends at ", time.time() - start)
    # start = time.time()
    index = test(False, bertData, trainer, block_trigram=block_trigram)
    # print("kobertsum test ends at ", time.time() - start)
    with open("/home/skkuedu/TestSite/mKoBertSum/ext/results/result_0727_0000_step_0.candidate") as file:
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
        
        print("sum_sents_text======")
        print(sum_sents_text)
        print("sum_sents_idx_list======")
        print(sum_sents_idx_list)
        print("sum_sents_xent_list======")
        print(sum_sents_xent_list)
        return sum_sents_text[:n_sents], sum_sents_idx_list[:n_sents], sum_sents_xent_list[:n_sents]


if __name__ == "__main__":
    models = preload()
    bertSum(models, sort_by_pred=True, n_sents=6, block_trigram=False)
