from os.path import exists
import json
from MatchSum.MatchSum_forMatch.preprocess.preprocess_utils import get_tokenizer, get_rouge

def read_jsonl(path):
    data = []
    with open(path) as f:
        for line in f:
            data.append(json.loads(line))
    return data

def get_datas(mode, datatype, encoder):
    paths = {}
    if mode == 'train':
        assert exists(f'data/train_{datatype}_{encoder}.jsonl')
        assert exists(f'data/val_{datatype}_{encoder}.jsonl')
        paths['train'] = read_jsonl(f'data/train_{datatype}_{encoder}.jsonl')
        paths['val']   = read_jsonl(f'data/val_{datatype}_{encoder}.jsonl')
    else:
        paths['test']  = read_jsonl(f'data/test_{datatype}_{encoder}.jsonl')
    return paths

def get_model(model_type):
    return get_tokenizer(model_type)

def get_rouge_scores(dec, ref):
    return get_rouge(dec, ref)