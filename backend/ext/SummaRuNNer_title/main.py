#!/usr/bin/env python3

from . import utils, models
import json
import argparse,random,logging
import torch
import numpy as np
from torch.autograd import Variable
from torch.utils.data import DataLoader

logging.basicConfig(level=logging.INFO, format='%(asctime)s [INFO] %(message)s')
parser = argparse.ArgumentParser(description='extractive summary')
# model
parser.add_argument('-save_dir',type=str,default='checkpoints/')
parser.add_argument('-embed_dim',type=int,default=100)
parser.add_argument('-embed_num',type=int,default=100)
parser.add_argument('-pos_dim',type=int,default=50)
parser.add_argument('-pos_num',type=int,default=100)
parser.add_argument('-seg_num',type=int,default=10)
parser.add_argument('-kernel_num',type=int,default=100)
parser.add_argument('-kernel_sizes',type=str,default='3,4,5')
parser.add_argument('-model',type=str,default='RNN_RNN')
parser.add_argument('-hidden_size',type=int,default=200)
# train
parser.add_argument('-lr',type=float,default=1e-3)
parser.add_argument('-batch_size',type=int,default=32)
parser.add_argument('-epochs',type=int,default=5)
parser.add_argument('-seed',type=int,default=1)
parser.add_argument('-train_dir',type=str,default='data/train.json')
parser.add_argument('-val_dir',type=str,default='data/val.json')
parser.add_argument('-embedding',type=str,default='data/embedding_mecab_ko.npz')
parser.add_argument('-word2id',type=str,default='data/word2id_mecab_ko.json')
parser.add_argument('-report_every',type=int,default=1500)
parser.add_argument('-seq_trunc',type=int,default=50)
parser.add_argument('-max_norm',type=float,default=1.0)
# test
parser.add_argument('-load_dir',type=str,default='checkpoints/RNN_RNN_seed_1_mecababs.pt')
parser.add_argument('-test_dir',type=str,default='data/test.json')
parser.add_argument('-filename',type=str,default='x.txt') # TextFile to be summarized
parser.add_argument('-topk',type=int,default=3)
parser.add_argument('-dacon',type=str,default="result.csv")
# device
parser.add_argument('-device',type=int)
# option
parser.add_argument('-test',action='store_true')
parser.add_argument('-debug',action='store_true')
parser.add_argument('-predict',action='store_true')
args = parser.parse_args()
use_gpu = args.device is not None

if torch.cuda.is_available() and not use_gpu:
    print("WARNING: You have a CUDA device, should run with -device 0")

# set cuda device and seed
if use_gpu:
    torch.cuda.set_device(args.device)
torch.cuda.manual_seed(args.seed)
torch.manual_seed(args.seed)
random.seed(args.seed)
np.random.seed(args.seed) 

def pre_compare_title():
    embed = torch.Tensor(np.load("/home/skkuedu/VANSum/backend/SummaRuNNer_title/data/embedding_mecab_ko.npz")['embedding'])
    with open("/home/skkuedu/VANSum/backend/SummaRuNNer_title/data/word2id_mecab_ko.json") as f:
        word2id = json.load(f)
    vocab = utils.Vocab(embed, word2id)
    if use_gpu:
        checkpoint1 = torch.load("/home/skkuedu/VANSum/backend/SummaRuNNer_title/checkpoints/RNN_RNN_title_seed_1.pt", map_location=lambda storage, loc: storage)     # title, mecab abs
    else:
        checkpoint1 = torch.load("/home/skkuedu/VANSum/backend/SummaRuNNer_title/checkpoints/RNN_RNN_title_seed_1.pt", map_location=lambda storage, loc: storage)
    
    # checkpoint['args']['device'] saves the device used as train time
    # if at test time, we are using a CPU, we must override device to None
    if not use_gpu:
        checkpoint1['args'].device = None
    
    net1 = getattr(models,checkpoint1['args'].model)(checkpoint1['args'], title=True)
    net1.load_state_dict(checkpoint1['model'])
    if use_gpu:
        net1.cuda()
    net1.eval()
    args.batch_size = 1

    return net1, vocab

def summary_with_title(examples1, preloaded):
    
    net1, vocab = preloaded
    # examples1 = ["문재인 대통령 브레인 양정철 원장 전북 방문\n이강모\n송하진 지사 간담 후 전북연구원과 업무협약 체결\n문재인 대통령의 브레인으로 불리는 양정철 더불어민주당 민주연구원장이 송하진 전북도지사를 만나 전북 발전 정책을 논의했다.\n양정철 민주연구원장은 20일 전북도청을 방문해 송 지사와 간담회를 가진 뒤 전북 정책연구기관인 전북연구원과 업무협약을 체결했다.\n양 원장은 간담회에서 \"지난 2012년 대선 이후 우석대학교 교수로 3년쯤 지냈기 때문에 전북은 제게 제2의 고향이나 마찬가지\"라면서 \"대통령이나 당은 전북에 대해 무한한 애정과 책임을 갖고 있다\"고 말했다.\n이에 송 지사는 \"먼저 가장 중요한 문제는 예타(예비타당성조사)인데 굉장히 많은 절차를 거쳐야 한다. 수월하게 가야 한다. 그게 지방이 원하는 것\"이라며 \"(예타는) 중앙정부가 지방정부를 견제하는 수단이 될 수도 있다. (예타를 통해 사업의) 수정·컨트롤은 좋지만 (양 원장이) 풀어주는 역할을 해 달라\"고 요청했다.\n이어 \"지방자치와 지방분권, 지방균형발전이라는 세 용어는 같이 간다. 자치 잘되는데 분권 안되면 의미없고 분권 잘되는데 균형이 안되면 허사\"라며 \"(정부의 자치·분권·균형) 세가지 실행과정은 제가 볼때는 만족스런건 아니며 특히 재정분권은 가야 할 길이 험난하다\"고 말했다.\n양 원장은 \"전북연구원이 갖고 있는 전북발전에 대한 좋은 대안과 축적돼 있는 정책을 이번 협약을 통해 민주연구원이 함께 노력해서 전북발전을 위한 좋은 정책들이 당이나 입법, 예산에 반영될 수 있도록 심부름꾼 역할을 잘 하겠다\"며 \"이번 업무협약을 통해서 중앙정부와 지방정부의 정책을 수행하는데 백업 역할을 잘 감당할 수 있도록 노력하겠다\"고 답했다.\n간담회가 끝난 뒤 양 원장은 전북연구원 김선기 원장과 전북도청 종합상황실에서 상호 연구 협력 및 관계 구축을 위한 협약을 체결했다.\n민주연구원과 전북연구원 두 기관은 전북 발전이 국가 발전이라는 공동 인식 하에 국가와 전북 발전에 필요한 정책 및 비전을 개발하기 위하여 상호 협력하고, 지속적이고 발전적인 상호 관계를 구축하는데 합의했다.\n이날 업무협약에 따라 양 기관은 공동 연구와 정책 협력을 수행하기 위한 실무협의회를 구성하고, 연구 및 정책 성과가 국가 정책과 입법에 반영될 수 있도록 상호협력을 추진할 계획이다.\n김선기 전북연구원장은 \"이번 협약은 국가 입법 의제와 연계한 실효성 있는 현장 정책을 개발·반영하고, 나아가 전북도민과 국민의 삶의 문제를 개선하는데 기여할 수 있을 것으로 기대된다\"고 말했다."]
    pred_dataset1 = utils.Dataset(examples1)
    pred_iter1 = DataLoader(dataset=pred_dataset1, batch_size=args.batch_size, shuffle=False)
    
    summaries = []
    for batch1 in pred_iter1:
        features, doc_lens = vocab.make_predict_features(batch1)
        if use_gpu:
            probs, doc1 = net1(Variable(features).cuda(), doc_lens)
        else:
            probs, doc1 = net1(Variable(features), doc_lens)
        start = 0
        for doc_len in doc_lens:
            stop = start + doc_len
            prob = probs[start:stop].topk(3)
            print(probs[start:stop])
            topk_indices = prob[1].cpu().data.tolist()
            topk_probs = prob[0].cpu().data.tolist()
            summaries.append({"index": topk_indices, "prob": topk_probs})
            start = stop
        
    return summaries[0]["index"], summaries[0]["prob"]

if __name__=='__main__':
    data = [] # with title
    examples = []
    with open("data/dev_with_title.jsonl") as f:
        for line in f:
            d = json.loads(line)
            data.append({"id": d["id"], "article_original": "\n".join(d["article_original"])})
            examples.append("\n".join(d["article_original"]))


