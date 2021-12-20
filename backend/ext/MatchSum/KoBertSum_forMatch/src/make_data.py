import os
import re
#import MeCab
from bs4 import BeautifulSoup
import kss
import pandas as pd
from tqdm import tqdm
import argparse

from .prepro.data_builder import full_selection

PROBLEM = 'ext'

## 사용할 path 정의
# PROJECT_DIR = '/home/uoneway/Project/PreSumm_ko'
PROJECT_DIR = './KoBertSum'

DATA_DIR = f'{PROJECT_DIR}/{PROBLEM}/data'
RAW_DATA_DIR = DATA_DIR + '/raw'
JSON_DATA_DIR = DATA_DIR + '/json_data'
BERT_DATA_DIR = DATA_DIR + '/bert_data' 
LOG_DIR = f'{PROJECT_DIR}/{PROBLEM}/logs'
LOG_PREPO_FILE = LOG_DIR + '/preprocessing.log' 


# special_symbols_in_dict = ['!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-']
# unused_tags = ['SF', 'SE', 'SSO', 'SSC', 'SC', 'SY']
# def korean_tokenizer(text, unused_tags=None, print_tag=False): 
#     # assert if use_tags is None or unuse_tags is None
    
#     tokenizer = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ko-dic")
#     parsed = tokenizer.parse(text)
#     word_tag = [w for w in parsed.split("\n")]
#     result = []
    
#     if unused_tags:
#         for word_ in word_tag[:-2]:
#             word = word_.split("\t")
#             tag = word[1].split(",")[0]
#             if tag not in unused_tags:
#                 if print_tag:
#                     result.append((word[0], tag))
#                 else:
#                     result.append(word[0]) 
#     else:
#         for word_ in word_tag[:-2]:
#             word = word_.split("\t")
#             result.append(word[0]) 

#     return result

def number_split(sentence):
    # 1. 공백 이후 숫자로 시작하는 경우만(문자+숫자+문자, 문자+숫자 케이스는 제외), 해당 숫자와 그 뒤 문자를 분리
    num_str_pattern = re.compile(r'(\s\d+)([^\d\s])')
    sentence = re.sub(num_str_pattern, r'\1 \2', sentence)

    # 2. 공백으로 sentence를 분리 후 숫자인경우만 공백 넣어주기
    #numbers_reg = re.compile("\s\d{2,}\s")
    sentence_fixed = ''
    for token in sentence.split():
        if token.isnumeric():
            token = ' '.join(token)
        sentence_fixed+=' '+token
    return sentence_fixed

def noise_remove(text):
    text = text.lower()
    
    # url 대체
    # url_pattern = re.compile(r'https?://\S*|www\.\S*')
    # text = url_pattern.sub(r'URL', text)

    # html 삭제
    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text(separator=" ")

    # 숫자 중간에 공백 삽입하기
    # text = number_split(text)
    #number_pattern = re.compile('\w*\d\w*') 
    #     number_pattern = re.compile('\d+') 
    #     text = number_pattern.sub(r'[[NUMBER]]', text)
    

    # PUCTUACTION_TO_REMOVED = string.punctuation.translate(str.maketrans('', '', '\"\'#$%&\\@'))  # !"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ 중 적은것을 제외한 나머지를 삭제
    # text = text.translate(str.maketrans(PUCTUACTION_TO_REMOVED, ' '*len(PUCTUACTION_TO_REMOVED))) 

    # remove_redundant_white_spaces
    text = re.sub(' +', ' ', text)

    # tgt special token 으로 활용할 204; 314[ 315] 대체/삭제해줘서 없애주기
    text = re.sub('¶', ' ', text)
    text = re.sub('----------------', ' ', text)
    text = re.sub(';', '.', text)

    return text

def preprocessing(text, tokenizer=None):
    text = noise_remove(text)
    if tokenizer is not None:
        text = tokenizer(text)
        text = ' '.join(text)

    return text

def korean_sent_spliter(doc):
    sents_splited = kss.split_sentences(doc)
    if len(sents_splited) == 1:
        # .이나 ?가 있는데도 kss가 분리하지 않은 문장들을 혹시나해서 살펴보니
        # 대부분 쉼표나 가운데점 대신 .을 사용하거나 "" 사이 인용문구 안에 들어가있는 점들. -> 괜찮.
        # aa = sents_splited[0].split('. ')
        # if len(aa) > 1:
        #     print(sents_splited)
        return sents_splited
    else:  # kss로 분리가 된 경우(3문장 이상일 때도 고려)
        #print(sents_splited)
        for i in range(len(sents_splited) - 1):
            idx = 0
            # 두 문장 사이에 .이나 ?가 없는 경우: 그냥 붙여주기
            if sents_splited[idx][-1] not in ['.','?' ] and idx < len(sents_splited) - 1:
                sents_splited[idx] = sents_splited[idx] + ' ' + sents_splited[idx + 1] if doc[len(sents_splited[0])] == ' ' \
                                        else sents_splited[idx] + sents_splited[idx + 1] 
                del sents_splited[idx + 1]
                idx -= 1
        #print(sents_splited)
        return sents_splited


def create_json_files(df):
    NUM_DOCS_IN_ONE_FILE = 1000
    start_idx_list = list(range(0, len(df), NUM_DOCS_IN_ONE_FILE))

    for start_idx in start_idx_list:
        end_idx = start_idx + NUM_DOCS_IN_ONE_FILE
        if end_idx > len(df):
            end_idx = len(df)  # -1로 하니 안됨...

        json_list = []
        for i, row in df.iloc[start_idx:end_idx].iterrows():
            original_sents_list = [preprocessing(original_sent).split()  # , korean_tokenizer
                                    for original_sent in row['article_original']]
            summary_sents_list = []
            json_list.append({'src': original_sents_list,
                                'tgt': summary_sents_list
            })
        return json_list

class BertData():
    used_subtoken_idxs = set()

    def __init__(self, tokenizer):
        self.tokenizer = tokenizer

        self.sep_token = '[SEP]'
        self.cls_token = '[CLS]'
        self.pad_token = '[PAD]'
        self.tgt_bos = '¶' # '[unused0]'   204; 314[ 315]
        self.tgt_eos = '----------------' # '[unused1]'
        self.tgt_sent_split = ';' #'[unused2]'
        self.sep_vid = self.tokenizer.token2idx[self.sep_token]
        self.cls_vid = self.tokenizer.token2idx[self.cls_token]
        self.pad_vid = self.tokenizer.token2idx[self.pad_token]

    def preprocess(self, src, tgt, sent_labels, use_bert_basic_tokenizer=False, is_test=False):

        if ((not is_test) and len(src) == 0):
            return None

        original_src_txt = [' '.join(s) for s in src]

        MIN_SRC_NTOKENS_PER_SENT = 1
        idxs = [i for i, s in enumerate(src) if (len(s) > MIN_SRC_NTOKENS_PER_SENT)]

        _sent_labels = [0] * len(src)
        for l in sent_labels:
            _sent_labels[l] = 1
        MAX_SRC_NTOKENS_PER_SENT = 300
        src = [src[i][:MAX_SRC_NTOKENS_PER_SENT] for i in idxs]
        sent_labels = [_sent_labels[i] for i in idxs]
        MAX_SRC_NSENTS = 120
        src = src[:MAX_SRC_NSENTS]
        sent_labels = sent_labels[:MAX_SRC_NSENTS]

        MIN_SRC_NSENTS = 1
        if ((not is_test) and len(src) < MIN_SRC_NSENTS):
            return None

        src_txt = [' '.join(sent) for sent in src]
        text = ' {} {} '.format(self.sep_token, self.cls_token).join(src_txt)

        src_subtokens = self.tokenizer.tokenize(text)

        src_subtokens = [self.cls_token] + src_subtokens + [self.sep_token]
        src_subtoken_idxs = self.tokenizer.convert_tokens_to_ids(src_subtokens)
        _segs = [-1] + [i for i, t in enumerate(src_subtoken_idxs) if t == self.sep_vid]
        segs = [_segs[i] - _segs[i - 1] for i in range(1, len(_segs))]
        segments_ids = []
        for i, s in enumerate(segs):
            if (i % 2 == 0):
                segments_ids += s * [0]
            else:
                segments_ids += s * [1]
        cls_ids = [i for i, t in enumerate(src_subtoken_idxs) if t == self.cls_vid]
        sent_labels = sent_labels[:len(cls_ids)]

        # kobert transforemrs에 연결되어 있는 transforemrs tokenizer 사용
        tgt_subtokens_str = self.tgt_bos + ' '  \
            + f' {self.tgt_sent_split} '.join([' '.join(self.tokenizer.tokenize(' '.join(tt))) for tt in tgt]) \
            + ' ' + self.tgt_eos
        ## presumm tokenizer 사용
        # """Runs basic tokenization (punctuation splitting, lower casing, etc.)."""
        # tgt_subtokens_str = '[unused0] ' + ' [unused2] '.join(
        #     [' '.join(self.tokenizer.tokenize(' '.join(tt), use_bert_basic_tokenizer=use_bert_basic_tokenizer)) for tt in tgt]) + ' [unused1]'


        MAX_TGT_NTOKENS = 500
        MIN_TGT_NTOKENS = 1
        tgt_subtoken = tgt_subtokens_str.split()[:MAX_TGT_NTOKENS]
        if ((not is_test) and len(tgt_subtoken) < MIN_TGT_NTOKENS):
            return None
        tgt_subtoken_idxs = self.tokenizer.convert_tokens_to_ids(tgt_subtoken)
        tgt_txt = '<q>'.join([' '.join(tt) for tt in tgt])
        src_txt = [original_src_txt[i] for i in idxs]

        return src_subtoken_idxs, sent_labels, tgt_subtoken_idxs, segments_ids, cls_ids, src_txt, tgt_txt

def json_to_bert(jobs, tokenizer):

    bert = BertData(tokenizer)
    datasets = []
    for d in jobs:
        source, tgt = d['src'], d['tgt']

        MAX_SRC_NSENTS = 120
        sent_labels = full_selection(source[:MAX_SRC_NSENTS], tgt, 3)
        source = [' '.join(s).lower().split() for s in source]
        tgt = [' '.join(s).lower().split() for s in tgt]
        b_data = bert.preprocess(source, tgt, sent_labels, use_bert_basic_tokenizer=False,
                                    is_test=True)

        if (b_data is None):
            continue
        src_subtoken_idxs, sent_labels, tgt_subtoken_idxs, segments_ids, cls_ids, src_txt, tgt_txt = b_data
        b_data_dict = {"src": src_subtoken_idxs, "tgt": tgt_subtoken_idxs,
                        "src_sent_labels": sent_labels, "segs": segments_ids, 'clss': cls_ids,
                        'src_txt': src_txt, "tgt_txt": tgt_txt}   ##  (원복)원래 키값이 src_txt, tgt_txt 이었는데 수정!!!!!
        datasets.append(b_data_dict)


    return datasets


def df(data, tokenizer):
    # import data
    os.makedirs(LOG_DIR, exist_ok=True)
    test_df = pd.DataFrame(data)
    js = create_json_files(test_df)
    bert = json_to_bert(js, tokenizer)
    return bert

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-task", default=None, type=str, choices=['df', 'train_bert', 'test_bert'])
    parser.add_argument("-target_summary_sent", default='abs', type=str)
    parser.add_argument("-n_cpus", default='2', type=str)
    parser.add_argument("-matchsum_datapath", default=f'{RAW_DATA_DIR}/extractive_test_v2.jsonl', type=str)

    args = parser.parse_args()

    # python make_data.py -make df
    # Convert raw data to df
    if args.task == 'df': # and valid_df
        df()

        # save df
        # test_df.to_pickle(f"{RAW_DATA_DIR}/test_df.pickle")
        # print(f'test_df({len(test_df)}) is exported')
        
    # python make_data.py -make bert -by abs
    # Make bert input file for train and valid from df file
    elif args.task  == 'train_bert':
        os.makedirs(JSON_DATA_DIR, exist_ok=True)
        os.makedirs(BERT_DATA_DIR, exist_ok=True)
        os.makedirs(LOG_DIR, exist_ok=True)

        for data_type in ['train', 'valid']:
            df = pd.read_pickle(f"{RAW_DATA_DIR}/{data_type}_df.pickle")

            ## make json file
            # 동일한 파일명 존재하면 덮어쓰는게 아니라 ignore됨에 따라 폴더 내 삭제 후 만들어주기
            json_data_dir = f"{JSON_DATA_DIR}/{data_type}_{args.target_summary_sent}"
            if os.path.exists(json_data_dir):
                os.system(f"rm {json_data_dir}/*")
            else:
                os.mkdir(json_data_dir)

            create_json_files(df, data_type=data_type, target_summary_sent=args.target_summary_sent, path=JSON_DATA_DIR)
           
            ## Convert json to bert.pt files
            bert_data_dir = f"{BERT_DATA_DIR}/{data_type}_{args.target_summary_sent}"
            if os.path.exists(bert_data_dir):
                os.system(f"rm {bert_data_dir}/*")
            else:
                os.mkdir(bert_data_dir)
            
            os.system(f"python preprocess.py"
                + f" -mode format_to_bert -dataset {data_type}"
                + f" -raw_path {json_data_dir}"
                + f" -save_path {bert_data_dir}"
                + f" -log_file {LOG_PREPO_FILE}"
                + f" -lower -n_cpus {args.n_cpus}")


    # python make_data.py -task test_bert
    # Make bert input file for test from df file
    elif args.task  == 'test_bert':
        os.makedirs(JSON_DATA_DIR, exist_ok=True)
        os.makedirs(BERT_DATA_DIR, exist_ok=True)
        os.makedirs(LOG_DIR, exist_ok=True)

        test_df = pd.read_pickle(f"{RAW_DATA_DIR}/test_df.pickle")

        ## make json file
        # 동일한 파일명 존재하면 덮어쓰는게 아니라 ignore됨에 따라 폴더 내 삭제 후 만들어주기
        json_data_dir = f"{JSON_DATA_DIR}/test"
        if os.path.exists(json_data_dir):
            os.system(f"rm {json_data_dir}/*")
        else:
            os.mkdir(json_data_dir)

        create_json_files(test_df, data_type='test', path=JSON_DATA_DIR)
        
        ## Convert json to bert.pt files
        bert_data_dir = f"{BERT_DATA_DIR}/test"
        if os.path.exists(bert_data_dir):
            os.system(f"rm {bert_data_dir}/*")
        else:
            os.mkdir(bert_data_dir)
        
        os.system(f"python preprocess.py"
            + f" -mode format_to_bert -dataset test"
            + f" -raw_path {json_data_dir}"
            + f" -save_path {bert_data_dir}"
            + f" -log_file {LOG_PREPO_FILE}"
            + f" -lower -n_cpus {args.n_cpus}")
