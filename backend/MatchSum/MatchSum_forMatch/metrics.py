from os.path import join
import torch
from datetime import timedelta
from time import time
from MatchSum.MatchSum_forMatch.utils import get_rouge_scores
import numpy as np
import pandas as pd
import os

from fastNLP.core.losses import LossBase
from fastNLP.core.metrics import MetricBase

class MarginRankingLoss(LossBase):      
    
    def __init__(self, margin, score=None, summary_score=None):
        super(MarginRankingLoss, self).__init__()
        self._init_param_map(score=score, summary_score=summary_score)
        self.margin = margin
        self.loss_func = torch.nn.MarginRankingLoss(margin)

    def get_loss(self, score, summary_score):
        
        # equivalent to initializing TotalLoss to 0
        # here is to avoid that some special samples will not go into the following for loop
        ones = torch.ones(score.size()).cuda(score.device)
        loss_func = torch.nn.MarginRankingLoss(0.0)
        TotalLoss = loss_func(score, score, ones)

        # candidate loss
        n = score.size(1)
        total_length = 0
        for i in range(1, n):
            pos_score = score[:, :-i]
            neg_score = score[:, i:]
            pos_score = pos_score.contiguous().view(-1)
            neg_score = neg_score.contiguous().view(-1)
            ones = torch.ones(pos_score.size()).cuda(score.device)
            loss_func = torch.nn.MarginRankingLoss(self.margin * i, reduction="sum")
            TotalLoss += loss_func(pos_score, neg_score, ones)
            total_length += len(pos_score)
        TotalLoss /= total_length

        # gold summary loss
        pos_score = summary_score.unsqueeze(-1).expand_as(score)
        neg_score = score
        pos_score = pos_score.contiguous().view(-1)
        neg_score = neg_score.contiguous().view(-1)
        ones = torch.ones(pos_score.size()).cuda(score.device)
        loss_func = torch.nn.MarginRankingLoss(0.0, reduction="sum")
        TotalLoss += loss_func(pos_score, neg_score, ones) / len(pos_score)
        
        return TotalLoss

class ValidMetric(MetricBase):
    def __init__(self, save_path, data, score=None):
        super(ValidMetric, self).__init__()
        self._init_param_map(score=score)

        self.save_path = save_path
        self.data = data

        self.top1_correct = 0
        self.top6_correct = 0
        self.top10_correct = 0
        
        self.ROUGE = 0.0
        self.ROUGE_ALL = [0.0, 0.0, 0.0]
        self.Error = 0

        self.cur_idx = 0
    
    def evaluate(self, score):
        batch_size = score.size(0)
        self.top1_correct += int(torch.sum(torch.max(score, dim=1).indices == 0))
        self.top6_correct += int(torch.sum(torch.max(score, dim=1).indices <= 5))
        self.top10_correct += int(torch.sum(torch.max(score, dim=1).indices <= 9))

        for i in range(batch_size):
            max_idx = int(torch.max(score[i], dim=0).indices)
            if max_idx >= len(self.data[self.cur_idx]['indices']):
                self.Error += 1 # Check if the candidate summary generated by padding is selected
                self.cur_idx += 1
                continue
            ext_idx = self.data[self.cur_idx]['indices'][max_idx]
            ext_idx.sort()

            dec = [self.data[self.cur_idx]['text'][j] for j in ext_idx]
            dec = '\n'.join(dec)
            ref = '\n'.join(self.data[self.cur_idx]['summary'])
            
            score = get_rouge_scores(dec, ref)
            self.ROUGE += (score[0] + score[1] + score[2]) / 3
            self.ROUGE_ALL = [t + k for t, k in zip(self.ROUGE_ALL, score)]
            self.cur_idx += 1

    def get_metric(self, reset=True):
        top1_accuracy = self.top1_correct / self.cur_idx
        top6_accuracy = self.top6_correct / self.cur_idx
        top10_accuracy = self.top10_correct / self.cur_idx
        ROUGE = self.ROUGE / self.cur_idx
        ROUGE_ALL = [t / self.cur_idx for t in self.ROUGE_ALL]
        eval_result = {'top1_accuracy': top1_accuracy, 'top6_accuracy': top6_accuracy, 
                    'top10_accuracy': top10_accuracy, 'Error': self.Error, 'ROUGE': ROUGE, 'ROUGE_ALL': ROUGE_ALL}
        with open(join(self.save_path, 'train_info.txt'), 'a') as f:
            print('top1_accuracy = {}, top6_accuracy = {}, top10_accuracy = {}, Error = {}, ROUGE = {}, ROUGE-ALL = {}'.format(
                top1_accuracy, top6_accuracy, top10_accuracy, self.Error, ROUGE, ROUGE_ALL), file=f)
        if reset:
            self.top1_correct = 0
            self.top6_correct = 0
            self.top10_correct = 0
            self.ROUGE = 0.0
            self.ROUGE_ALL = [0.0, 0.0, 0.0]
            self.Error = 0
            self.cur_idx = 0
        return eval_result
        
class MatchRougeMetric(MetricBase):
    def __init__(self, data, score=None):
        super(MatchRougeMetric, self).__init__()
        self._init_param_map(score=score)
        self.data = data
        self.n_total = len(data)
        self.cur_idx = 0
        self.ext = []
        self.start = time()
    
    def evaluate(self, score):
        ext = int(torch.max(score, dim=1).indices) # batch_size = 1
        self.ext.append(ext)
        self.cur_idx += 1
        print('{}/{} ({:.2f}%) decoded in {} seconds\r'.format(
            self.cur_idx, self.n_total, self.cur_idx/self.n_total*100, timedelta(seconds=int(time()-self.start))
            ), end='')
    
    def get_metric(self, reset=True):
        
        print('\nStart writing files !!!')
        generated_summaries = []
        reference_summaries = []
        for i, ext in enumerate(self.ext):
            sent_ids = self.data[i]['indices'][ext]
            dec, ref = [], []
            
            for j in sent_ids:
                dec.append(self.data[i]['text'][j])
            for sent in self.data[i]['summary']:
                ref.append(sent)

            generated_summaries.append("\n".join(dec))
            reference_summaries.append("\n".join(ref))
        
        print('Start evaluating ROUGE score !!!')
        R_1, R_2, R_L = get_rouge_scores(generated_summaries, reference_summaries)
        eval_result = {'ROUGE-1': R_1, 'ROUGE-2': R_2, 'ROUGE-L':R_L}

        if reset == True:
            self.cur_idx = 0
            self.ext = []
            self.data = []
            self.start = time()
        
        return eval_result

class MatchExportMetric(MetricBase):
    def __init__(self, data, csv_path="./result/result.csv", score=None):
        super(MatchExportMetric, self).__init__()
        self._init_param_map(score=score)
        self.data = data
        self.n_total = len(data)
        self.cur_idx = 0
        self.ext = []
        self.start = time()
        assert(os.path.exists(csv_path) == False)
        self.csv_path = csv_path
    
    def evaluate(self, score):
        ext = int(torch.max(score, dim=1).indices) # batch_size = 1
        self.ext.append(ext)
        self.cur_idx += 1
        print('{}/{} ({:.2f}%) decoded in {} seconds\r'.format(
            self.cur_idx, self.n_total, self.cur_idx/self.n_total*100, timedelta(seconds=int(time()-self.start))
            ), end='')
    
    def get_metric(self, reset=True):
        
        print('\nStart writing files !!!')
        generated_summaries = []
        for i, ext in enumerate(self.ext):
            sent_ids = self.data[i]['indices'][ext]
            dec = []
            
            for j in sent_ids:
                dec.append(self.data[i]['text'][j])
            generated_summaries.append("\n".join(dec))

        df = pd.DataFrame({"summary": generated_summaries})
        df.to_csv(self.csv_path, encoidng='utf-8')
        eval_result = {'ROUGE-1': 0, 'ROUGE-2': 0, 'ROUGE-L':0}

        if reset == True:
            self.cur_idx = 0
            self.ext = []
            self.data = []
            self.start = time()
        
        return eval_result
    
class MatchResultMetric(MetricBase):
    def __init__(self, data, score=None):
        super(MatchResultMetric, self).__init__()
        self._init_param_map(score=score)
        self.data = data
        self.ext = []
        self.prob = []
    
    def evaluate(self, score):
        # ext = int(torch.max(score, dim=1).indices) # batch_size = 1
        ext = torch.argsort(score, descending=True).numpy()[0]
        self.ext.append(ext)
        prob = score.numpy()[0][ext]
        self.prob.append(prob.tolist())
    
    def get_metric(self, reset=True):
        
        result = {"index": [], "probs": []}
        for i, ext in enumerate(self.ext):
            sent_ids = np.array(self.data[i]['indices'])[ext]
            result["index"].append(sent_ids.tolist())
            result["probs"].append(self.prob[i])

        if reset == True:
            self.ext = []
            self.data = []
            self.prob = []

        return result
    