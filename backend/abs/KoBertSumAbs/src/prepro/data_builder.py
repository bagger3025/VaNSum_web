from src.others.utils import get_tokenizer
import argparse
import gc
import glob
import json
import os
import re

import torch
from multiprocess import Pool

from others.logging import logger, init_logger

# for full_selection
from itertools import permutations 
import numpy as np
from others.rouge_metric import Rouge

# VaNSum_web/backend/abs/KoBertSumAbs
PROJECT_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..")

def _get_ngrams(n, text):
    """Calcualtes n-grams.

		Args:
		n: which n-grams to calculate
		text: An array of tokens

		Returns:
		A set of n-grams
    """
    ngram_set = set()
    text_length = len(text)
    max_index_ngram_start = text_length - n
    for i in range(max_index_ngram_start + 1):
        ngram_set.add(tuple(text[i:i + n]))
    return ngram_set

def _get_word_ngrams(n, sentences):
    """Calculates word n-grams for multiple sentences.
    """
    assert len(sentences) > 0
    assert n > 0

    words = sum(sentences, [])
    return _get_ngrams(n, words)

def cal_rouge(evaluated_ngrams, reference_ngrams):
    reference_count = len(reference_ngrams)
    evaluated_count = len(evaluated_ngrams)

    overlapping_ngrams = evaluated_ngrams.intersection(reference_ngrams)
    overlapping_count = len(overlapping_ngrams)

    if evaluated_count == 0:
        precision = 0.0
    else:
        precision = overlapping_count / evaluated_count

    if reference_count == 0:
        recall = 0.0
    else:
        recall = overlapping_count / reference_count

    f1_score = 2.0 * ((precision * recall) / (precision + recall + 1e-8))
    return {"f": f1_score, "p": precision, "r": recall}

# 1개만 선택했을 때 가장 높은거 고르고, 그 1개와 다른 1개 조합했을 때 가장 높은거 고르고... 차례대로
# 만약 1개만 선택한것보다 다른 1개 더 선택하는 조합의 루지 점수가 떨어지면 그냥 1개만 나올 수 도 있음
def greedy_selection(doc_sent_list, abstract_sent_list, summary_size):
    def _rouge_clean(s):
        return re.sub(r'[^a-zA-Z0-9가-힣 ]', '', s)

    max_rouge = 0.0
    abstract = sum(abstract_sent_list, [])
    abstract = _rouge_clean(' '.join(abstract)).split()
    sents = [_rouge_clean(' '.join(s)).split() for s in doc_sent_list]
    evaluated_1grams = [_get_word_ngrams(1, [sent]) for sent in sents]
    reference_1grams = _get_word_ngrams(1, [abstract])
    evaluated_2grams = [_get_word_ngrams(2, [sent]) for sent in sents]
    reference_2grams = _get_word_ngrams(2, [abstract])

    selected = []
    for _ in range(summary_size):
        cur_max_rouge = max_rouge
        cur_id = -1
        for i in range(len(sents)):
            if (i in selected):
                continue
            c = selected + [i]
            candidates_1 = [evaluated_1grams[idx] for idx in c]
            candidates_1 = set.union(*map(set, candidates_1))
            candidates_2 = [evaluated_2grams[idx] for idx in c]
            candidates_2 = set.union(*map(set, candidates_2))
            rouge_1 = cal_rouge(candidates_1, reference_1grams)['f']
            rouge_2 = cal_rouge(candidates_2, reference_2grams)['f']
            rouge_score = rouge_1 + rouge_2
            if rouge_score > cur_max_rouge:
                cur_max_rouge = rouge_score
                cur_id = i
        if (cur_id == -1):
            return selected
        selected.append(cur_id)
        max_rouge = cur_max_rouge

    return selected

# 전체 경우의 수 탐색
def full_selection(doc_sent_list, abstract_sent_list, summary_size=3):
    def _rouge_clean(s):
        return re.sub(r'[^A-Za-z0-9가-힣 ]', '', s)

    rouge_evaluator = Rouge(
            metrics=["rouge-n", "rouge-l"],
            max_n=2,
            limit_length=True,
            length_limit=1000,
            length_limit_type="words",
            use_tokenizer=True,
            apply_avg=True,
            apply_best=False,
            alpha=0.5,  # Default F1_score
            weight_factor=1.2,
        )

    # cleaning and merge [[w,w,w], [w,w,w]] -> [w,w,w, w,w,w] 
    abstract = sum(abstract_sent_list, [])
    abstract = _rouge_clean(' '.join(abstract))
    doc_sent_list_merged = [_rouge_clean(' '.join(sent)) for sent in doc_sent_list]
    src_len = len(doc_sent_list_merged)

    # 일단 greedy로 구한 다음 3개가 안되는 경우만 나머지를 full로 채움!
    selected_idx3_list = greedy_selection(doc_sent_list, abstract_sent_list, summary_size)

    total_max_rouge_score = 0.0
    if src_len > 10 or len(selected_idx3_list) < 2: # greedy
        for _ in range(summary_size - len(selected_idx3_list)):
            cur_max_total_rouge_score = 0.0
            cur_sent_idx = -1
            for sent_idx in range(len(doc_sent_list_merged)):
                if sent_idx in selected_idx3_list:
                    continue
                temp_idx3_list = selected_idx3_list + [sent_idx]
                sents_array = np.array(doc_sent_list_merged)[temp_idx3_list]
                sents_merged = '\n'.join(sents_array)
                # ROUGE1,2,l 합score 계산
                rouge_scores = rouge_evaluator.get_scores(sents_merged, abstract)
                total_rouge_score = 0
                for v in rouge_scores.values():
                    total_rouge_score += v['f']
                if total_rouge_score > cur_max_total_rouge_score:
                    cur_max_total_rouge_score = total_rouge_score
                    cur_sent_idx = sent_idx
            selected_idx3_list.append(cur_sent_idx)
            total_max_rouge_score = cur_max_total_rouge_score
            
    # full
    sents_idx_perm_list = list(permutations(range(src_len), summary_size)) 
    sents_idx_list = []
    for sents_idx_perm in sents_idx_perm_list:
        if set(sents_idx_perm) & set(selected_idx3_list) == set(selected_idx3_list):
            sents_idx_list.append(sents_idx_perm)

    for sents_idx in sents_idx_list:
        sents_array = np.array(doc_sent_list_merged)[list(sents_idx)]
        sents_merged = ' '.join(sents_array)

        # ROUGE1,2,l 합score 계산
        rouge_scores = rouge_evaluator.get_scores(sents_merged, abstract)
        total_rouge_score = 0
        for v in rouge_scores.values():
            total_rouge_score += v['f']

        if total_rouge_score > total_max_rouge_score:
            total_max_rouge_score = total_rouge_score
            selected_idx3_list = list(sents_idx)
    return selected_idx3_list

class BertData():
    def __init__(self, args):
        self.args = args
        tokenizer_set = get_tokenizer(args.model, f"{PROJECT_DIR}/temp")
        self.tokenizer, self.special_tokens = tokenizer_set["tokenizer"], tokenizer_set["special_tokens"]
        self.sep_token = self.special_tokens["sep"]
        self.cls_token = self.special_tokens["cls"]
        self.pad_token = self.special_tokens["pad"]
        self.tgt_bos = self.special_tokens["bos"]
        self.tgt_eos = self.special_tokens["eos"]
        self.tgt_sent_split = self.special_tokens["sent_split"]
        
        self.sep_vid = self.special_tokens["sep_id"]
        self.cls_vid = self.special_tokens["cls_id"]
        self.pad_vid = self.special_tokens["pad_id"]

    def preprocess(self, src, tgt, sent_labels, is_test=False):
        if ((not is_test) and len(src) == 0):
            return None

        original_src_txt = [' '.join(s) for s in src]
        idxs = [i for i, s in enumerate(src) if (len(s) > self.args.min_src_ntokens_per_sent)]

        _sent_labels = [0] * len(src)
        for l in sent_labels:
            _sent_labels[l] = 1

        src = [src[i][:self.args.max_src_ntokens_per_sent] for i in idxs]
        sent_labels = [_sent_labels[i] for i in idxs]
        src = src[:self.args.max_src_nsents]
        print(src)
        sent_labels = sent_labels[:self.args.max_src_nsents]

        if ((not is_test) and len(src) < self.args.min_src_nsents):
            return None

        src_subtoken_idxs = self.encoding_process(src, f"{self.sep_token} {self.cls_token}", self.cls_token, self.sep_token)
        
        _segs = [-1] + [i for i, t in enumerate(src_subtoken_idxs) if t == self.sep_vid]
        segs = [_segs[i] - _segs[i - 1] for i in range(1, len(_segs))]
        segments_ids = []
        for i, s in enumerate(segs):
            segments_ids += s * [i % 2]
        cls_ids = [i for i, t in enumerate(src_subtoken_idxs) if t == self.cls_vid]

        # examine min_tgt_ntokens only when it is not test, otherwise ignore it
        min_tgt_ntokens = args.min_tgt_ntokens if not is_test else -1
        tgt_subtoken_idxs = self.encoding_process(tgt, self.tgt_sent_split, self.tgt_bos, self.tgt_eos, 
                                                    self.args.max_tgt_ntokens, min_tgt_ntokens)
        if tgt_subtoken_idxs is None:
            return None

        tgt_txt = '<q>'.join([' '.join(tt) for tt in tgt])
        src_txt = [original_src_txt[i] for i in idxs]
        return src_subtoken_idxs, sent_labels, tgt_subtoken_idxs, segments_ids, cls_ids, src_txt, tgt_txt

    def encoding_process(self, src, sent_split_token, cls_token, sep_token, max_ntokens = -1, min_ntokens = -1):
        
        # each element is sentence
        src_txt = [" ".join(sent) for sent in src]
        print(src_txt)

        # each element is tokens of sentence
        src_txt = [" ".join(self.tokenizer.tokenize(sent)) for sent in src_txt]
        print(src_txt)

        # add special tokens 
        src_subtokens = f" {sent_split_token} ".join(src_txt)
        src_subtokens = f"{cls_token} {src_subtokens} {sep_token}".split()
        print(src_subtokens)

        # examine max_ntokens, min_ntokens
        if max_ntokens != -1:
            src_subtokens = src_subtokens[:max_ntokens]
        
        if min_ntokens != -1 and len(src_subtokens) < min_ntokens:
            return None

        # map tokens into ids
        src_subtoken_idxs = self.tokenizer.convert_tokens_to_ids(src_subtokens)
        return src_subtoken_idxs

def format_to_bert(args):
    if (args.dataset != ''):
        datasets = [args.dataset]
    else:
        datasets = ['train', 'valid', 'test']
    for corpus_type in datasets:
        a_lst = []
        for json_f in glob.glob(os.path.join(args.raw_path, '*' + corpus_type + '.*.json')):
            real_name = json_f.split('/')[-1]
            a_lst.append((corpus_type, json_f, args, os.path.join(args.save_path, real_name.replace('json', 'bert.pt'))))
        pool = Pool(args.n_cpus)
        for _ in pool.imap(_format_to_bert, a_lst):
            pass

        pool.close()
        pool.join()

def _format_to_bert(params):
    corpus_type, json_file, args, save_file = params
    is_test = corpus_type == 'test'
    if (os.path.exists(save_file)):
        logger.info('Ignore %s' % save_file)
        return

    bert = BertData(args)
    logger.info('Processing %s' % json_file)
    jobs = json.load(open(json_file))
    datasets = []
    for d in jobs:
        source, tgt = d['src'], d['tgt']
        ###############
        removeIdx=[]
        source=['<p>'.join(s) for s in source]
        for i in range(len(source)):
            if ("@" in source[i] and "기자" in source[i]) or ("구독하기" in source[i]):
                removeIdx.append(i)
        
        for i in removeIdx[::-1]:
            del source[i]

        source = [s.split('<p>') for s in source]
        ###############
        sent_labels = full_selection(source[:args.max_src_nsents], tgt, 3)
        if (args.lower):
            source = [' '.join(s).lower().split() for s in source]
            tgt = [' '.join(s).lower().split() for s in tgt]
        b_data = bert.preprocess(source, tgt, sent_labels, is_test=is_test)

        if (b_data is None):
            continue
        src_subtoken_idxs, sent_labels, tgt_subtoken_idxs, segments_ids, cls_ids, src_txt, tgt_txt = b_data
        datasets.append({"src": src_subtoken_idxs, "tgt": tgt_subtoken_idxs,
                        "src_sent_labels": sent_labels, "segs": segments_ids, 'clss': cls_ids,
                        'src_txt': src_txt, "tgt_txt": tgt_txt})
    logger.info('Processed instances %d' % len(datasets))
    logger.info('Saving to %s' % save_file)
    torch.save(datasets, save_file)
    datasets = []
    gc.collect()

if __name__ == '__main__':

    def str2bool(v):
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')

    parser = argparse.ArgumentParser()
    parser.add_argument("-model", default='klue', type=str, choices=['kykim-bert', "klue"])

    parser.add_argument("-mode", default='', type=str)
    parser.add_argument("-select_mode", default='greedy', type=str)
    parser.add_argument("-map_path", default='../../data/')
    parser.add_argument("-raw_path", default='../../line_data')
    parser.add_argument("-save_path", default='../../data/')
    parser.add_argument('-log_file', default='../../logs/cnndm.log')

    parser.add_argument("-shard_size", default=2000, type=int)
    parser.add_argument('-min_src_nsents', default=1, type=int)    # 3
    parser.add_argument('-max_src_nsents', default=120, type=int)    # 100
    parser.add_argument('-min_src_ntokens_per_sent', default=1, type=int)    # 5
    parser.add_argument('-max_src_ntokens_per_sent', default=300, type=int)    # 200
    parser.add_argument('-min_tgt_ntokens', default=1, type=int)    # 5
    parser.add_argument('-max_tgt_ntokens', default=500, type=int)    # 500

    parser.add_argument("-lower", type=str2bool, nargs='?',const=True,default=True)
    parser.add_argument('-dataset', default='')
    parser.add_argument('-n_cpus', default=2, type=int)

    args = parser.parse_args()
    init_logger(args.log_file)
    format_to_bert(args)
