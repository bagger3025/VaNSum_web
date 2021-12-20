#!/usr/bin/env python3

import argparse
import json
import csv
import numpy as np
from collections import OrderedDict
from glob import glob
from time import time
from multiprocessing import Pool,cpu_count
from itertools import chain
from SummaRuNNer.utils.rouge_metric import Rouge_kor
from konlpy.tag import Mecab

rouge_evaluator = Rouge_kor(
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

def build_vocab(args):
    print('start building vocab')

    PAD_IDX = 0
    UNK_IDX = 1
    PAD_TOKEN = 'PAD_TOKEN'
    UNK_TOKEN = 'UNK_TOKEN'
    
    f = open(args.embed, 'r', encoding='utf-8')
    rdr = csv.reader(f, delimiter='\t')
    r = list(rdr)
    f.close()
    embed_dim = 200     # change according to word vector dim

    word2id = OrderedDict()
    
    word2id[PAD_TOKEN] = PAD_IDX
    word2id[UNK_TOKEN] = UNK_IDX
    
    embed_list = []
    # fill PAD and UNK vector
    embed_list.append([0 for _ in range(embed_dim)])
    embed_list.append([0 for _ in range(embed_dim)])
    
    # build Vocab
    while i < len(r):
        lists = r[i]
        word = lists[1]
        vectors = [float(t) for t in lists[2].replace("[", "").split(" ") if t != ""]
        i += 1
        while len(vectors) < embed_dim:
            vectors += [ float(t) for t in r[i].replace("]","").split(" ") if t != ""]
            i += 1
        embed_list.append(vectors)
        word2id[word] = len(word2id)
    
    embed = np.array(embed_list,dtype=np.float32)
    np.savez_compressed(file=args.vocab, embedding=embed)
    with open(args.word2id,'w') as f:
        json.dump(word2id,f)

# get textlist and gold abstractive summary
# return textlist indices which maximize rouge score with abstractive summary (greedy chosen)
def get_greedy_rouge_list(textlist : list, abs):
    max_rouge = 0
    ans = []
    ans_text = []
    while True:
        candidates = []
        for i, text in enumerate(textlist):
            newlist = ans_text + [text]
            score = rouge_evaluator.get_scores('\n'.join(newlist), abs)
            score = score["rouge-1"]['f']
            if score > max_rouge:
                candidates.append((i, score))
        if len(candidates) == 0:
            break
        max_index, max_rouge = candidates[np.array([t for _, t in candidates]).argmax()]
        
        ans_text.append(textlist[max_index])
        ans.append(max_index)
        textlist.pop(max_index)

    return ans

def worker(files):
    mecab = Mecab()
    examples = []
    for article in files:
        sents,labels,summaries = [],[],[]
        greedy_rouge_list = get_greedy_rouge_list(article['article_original'], article['abstractive'])
        # content&summary
        for i, line in enumerate(article["article_original"]):
            tokens = [token for token, _ in mecab.pos(line)]
            label = '1' if i in greedy_rouge_list else '0'
            if label == "1":
                summaries.append(' '.join(tokens))
            sents.append(' '.join(tokens))
            labels.append(label)
        
        ex = {'doc':'\n'.join(sents),'labels':'\n'.join(labels),'summaries':'\n'.join(summaries)}
        examples.append(ex)
    return examples

def build_dataset(args):
    t1 = time()
    
    print('start building dataset')
    if args.worker_num == 1 and cpu_count() > 1:
        print('[INFO] There are %d CPUs in your device, please increase -worker_num to speed up' % (cpu_count()))
        print("       It's a IO intensive application, so 2~10 may be a good choise")

    files = glob(args.source_dir)
    data_num = len(files)
    group_size = data_num // args.worker_num
    groups = []
    for i in range(args.worker_num):
        if i == args.worker_num - 1:
            groups.append(files[i*group_size : ])
        else:
            groups.append(files[i*group_size : (i+1)*group_size])
    p = Pool(processes=args.worker_num)
    multi_res = [p.apply_async(worker,(fs,)) for fs in groups]
    res = [res.get() for res in multi_res]
    
    with open(args.target_dir, 'w') as f:
        for row in chain(*res):
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    t2 = time()
    print('Time Cost : %.1f seconds' % (t2 - t1))

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    
    parser.add_argument('-build_vocab',action='store_true')
    parser.add_argument('-embed', type=str, default='data/100.w2v')
    parser.add_argument('-vocab', type=str, default='data/embedding.npz')
    parser.add_argument('-word2id',type=str,default='data/word2id.json')

    parser.add_argument('-worker_num',type=int,default=1)
    parser.add_argument('-source_dir', type=str, default='data/neuralsum/dailymail/validation/*')
    parser.add_argument('-target_dir', type=str, default='data/val.json')

    args = parser.parse_args()
    
    if args.build_vocab:
        build_vocab(args)
    else:
        build_dataset(args)
