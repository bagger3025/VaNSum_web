import argparse
from os.path import exists
import json
import multiprocessing as mp
from time import time
from datetime import timedelta
from itertools import combinations

from cytoolz import curry
from MatchSum.MatchSum_forMatch.preprocess.preprocess_utils import get_tokenizer, load_jsonl, get_rouge

MAX_LEN = 512
original_data, sent_ids = [], []

@curry
def get_candidates(tokenizer, cls, sep_id, idx):
    
    # load data
    data = {}
    data['text'] = original_data[idx]['article_original']   # original_data[idx]['text']
    try:
        data['summary'] = [original_data[idx]['abstractive']]   # original_data[idx]['summary']
    except:
        data['summary'] = [original_data[idx]['article_original'][0]]
        data['id'] = original_data[idx]['id']

    # get candidate summaries
    # truncate each document into the 5 most important sentences (using BertExt), 
    # then select 3 sentences to form a candidate summary, so there are C(5,3)=10 candidate summaries.
    # if you want to process other datasets, you may need to adjust these numbers according to specific situation.
    sent_id = sent_ids[idx]['sent_id'][:5]
    indices = list(combinations(sent_id, 3))
    if len(sent_id) <= 3:
        indices = [sent_id] + [sent_id]
    
    # get ROUGE score for each candidate summary and sort them in descending order
    score = []
    for i in indices:
        i = list(i)
        i.sort()
        dec = []
        for j in i:
            sent = data['text'][j]
            dec.append(sent)
        s1, s2, sl = get_rouge('\n'.join(dec), data['summary'][0])
        score.append((i, (s1 + s2 + sl) / 3))
    score.sort(key=lambda x : x[1], reverse=True)
    
    # write candidate indices and score
    data['ext_idx'] = sent_id
    data['indices'] = []
    data['score'] = []
    for i, R in score:
        data['indices'].append(list(map(int, i)))
        data['score'].append(R)

    # tokenize and get candidate_id
    candidate_summary = []
    for i in data['indices']:
        cur_summary = [cls]
        for j in i:
            cur_summary += data['text'][j].split()
        cur_summary = cur_summary[:MAX_LEN]
        cur_summary = ' '.join(cur_summary)
        candidate_summary.append(cur_summary)
    
    data['candidate_id'] = []
    for summary in candidate_summary:
        token_ids = tokenizer.encode(summary, add_special_tokens=False)[:(MAX_LEN - 1)]
        token_ids += sep_id
        data['candidate_id'].append(token_ids)

    # tokenize and get text_id
    text = [cls]
    for sent in data['text']:
        text += sent.split()
    text = text[:MAX_LEN]
    text = ' '.join(text)
    token_ids = tokenizer.encode(text, add_special_tokens=False)[:(MAX_LEN - 1)]
    token_ids += sep_id
    data['text_id'] = token_ids
    
    # tokenize and get summary_id
    summary = [cls]
    for sent in data['summary']:
        summary += sent.split()
    summary = summary[:MAX_LEN]
    summary = ' '.join(summary)
    token_ids = tokenizer.encode(summary, add_special_tokens=False)[:(MAX_LEN - 1)]
    token_ids += sep_id
    data['summary_id'] = token_ids
    
    return data

def get_candidates_mp(args, preloaded = None):

    # load original data and indices
    global original_data, sent_ids
    if preloaded is None:
        # choose tokenizer
        # if type is added, add tokenizer in get_tokenizer function
        tokenizer, _, special_tokens = get_tokenizer(args.tokenizer)

        original_data = load_jsonl(args.data_path)
        sent_ids = load_jsonl(args.index_path)
    else:
        tokenizer, special_tokens, original_data, sent_ids = preloaded

    cls, sep_id = special_tokens["cls"], [special_tokens["sep_id"]]
    n_files = len(original_data)
    assert len(sent_ids) == len(original_data)
    print('total {} documents'.format(n_files))

    # use multi-processing to get candidate summaries
    start = time()
    print('start getting candidates with multi-processing !!!')

    with mp.Pool(processes=args.n_cpus) as pool:
        res = pool.map_async(get_candidates(tokenizer, cls, sep_id), range(n_files), chunksize=64)
        res_get = res.get()
        pool.close()
        pool.join()
    
    print('finished in {}'.format(timedelta(seconds=time()-start)))
    
    # write processed data
    if preloaded is None:
        print('start writing {} files'.format(n_files))
        with open(args.write_path, 'a') as f:
            for i in range(n_files):
                print(json.dumps(res_get[i], ensure_ascii=False), file=f)
    
    return res_get

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description='Process truncated documents to obtain candidate summaries'
    )
    parser.add_argument('--tokenizer', type=str, required=True,
        help='BERT/RoBERTa/kobert/koelectra/klue/kluebert')
    parser.add_argument('--data_path', type=str, required=True,
        help='path to the original dataset, the original dataset should contain text and summary')
    parser.add_argument('--index_path', type=str, required=True,
        help='indices of the remaining sentences of the truncated document')
    parser.add_argument('--write_path', type=str, required=True,
        help='path to store the processed dataset')
    parser.add_argument('--n_cpus', type=int, required=True,
        help='number of cpus')

    args = parser.parse_args()
    assert args.tokenizer in ['bert', 'roberta', 'kobert', 'koelectra', 'klue', 'kluebert']
    assert exists(args.data_path)
    assert exists(args.index_path)

    get_candidates_mp(args)
