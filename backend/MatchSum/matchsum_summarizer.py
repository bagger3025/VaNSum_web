import os
import sys
import torch
import argparse

sys.path.append(os.path.abspath(os.path.dirname(__file__)) + "/MatchSum_forMatch/")

from MatchSum.KoBertSum_forMatch.src.make_data import df
from MatchSum.KoBertSum_forMatch.src.train import test
from MatchSum.MatchSum_forMatch.preprocess.get_candidate import get_candidates_mp

from MatchSum.MatchSum_forMatch.preprocess.tokenization_kobert import KoBertTokenizer
from MatchSum.MatchSum_forMatch.train_matching import test_model

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

class MatchSum_Summarizer():

    def __init__(self):
        self.tokenizer = KoBertTokenizer.from_pretrained('monologg/kobert', do_lower_case=True)
        self.trainer = test(True)
        self.model = torch.load(PROJECT_DIR + "/MatchSum_forMatch/models/epoch-3_step-15000_ROUGE-0.449044.pt")
        # torch.save(self.model, PROJECT_DIR+ "/MatchSum_forMatch/models/best_model_resave/epoch-3_step-15000_ROUGE-0.449044.pt")
        cls, sep, pad = "[CLS]", "[SEP]", "[PAD]"
    
        self.special_tokens = {
            "cls":cls,
            "sep":sep,
            "pad":pad,
            "cls_id": self.tokenizer.encode(cls, add_special_tokens=False)[0],
            "sep_id": self.tokenizer.encode(sep, add_special_tokens=False)[0],
            "pad_id": self.tokenizer.encode(pad, add_special_tokens=False)[0]
        }
        
        parser = argparse.ArgumentParser()
        parser.add_argument('--n_cpus', type=int, default=1)
        self.args = parser.parse_args()
        self.matchsum_args = self.MatchSum_args()

    def MatchSum_args(self):
        parser = argparse.ArgumentParser()

        parser.add_argument('--save_path', default=PROJECT_DIR + "/MatchSum_forMatch/model/kobert_DOO7abs/best_model",
                            help='root of the model', type=str)
        parser.add_argument('--gpus', default="-1",
                            help='available gpus for training(separated by commas)', type=str)
        parser.add_argument('--encoder', default="kobert",
                            help='the encoder for matchsum (bert/kobert/roberta)', type=str)

        parser.add_argument('--batch_size', default=1,
                            help='the training batch size', type=int)
        parser.add_argument('--accum_count', default=2,
                            help='number of updates steps to accumulate before performing a backward/update pass', type=int)
        parser.add_argument('--candidate_num', default=20,
                            help='number of candidates summaries', type=int)
        parser.add_argument('--max_lr', default=2e-5,
                            help='max learning rate for warm up', type=float)
        parser.add_argument('--margin', default=0.01,
                            help='parameter for MarginRankingLoss', type=float)
        parser.add_argument('--warmup_steps', default=10000,
                            help='warm up steps for training', type=int)
        parser.add_argument('--n_epochs', default=5,
                            help='total number of training epochs', type=int)
        parser.add_argument('--valid_steps', default=1000,
                            help='number of update steps for validation and saving checkpoint', type=int)

        args = parser.parse_known_args()[0]
        return args

    def summarize(self, data, n_candidates=1):
        
        # write_jsonl("./data/DATA.jsonl", string)
        #os.chdir(PROJECT_DIR + '/KoBertSum/src/')
        # os.system("""python make_data.py -task df -target_summary_sent abs -n_cpus 20 -matchsum_datapath ../../data/DATA.jsonl""")
        # os.system("""python make_data.py -task test_bert -n_cpus 20""")
        
        # data = load_jsonl("./data/DATA.jsonl")
        # bert = df(data, self.tokenizer)
        
        # os.chdir(PROJECT_DIR + '/KoBertSum/')
        # os.system("""python main.py -task test -test_from 0702_1932/model_step_7000.pt -visible_gpus 1""")
        
        # index = test(False, bert, self.trainer)
        index = data["index"]
        text = data["data"]
        preloaded = self.tokenizer, self.special_tokens, text, index
        #os.system("python get_candidate.py --tokenizer kobert --data_path ../../data/DATA.jsonl --index_path ../../result/DATA.jsonl --write_path ../data/test_DATA_kobert.jsonl --dacon y")
        matchsum_processed_data = get_candidates_mp(self.args, preloaded)
        
        #os.chdir(PROJECT_DIR + "/MatchSum/")
        #os.system("rm -r ./model/kobert_DOO7abs/result")
        #os.system("python train_matching.py --mode=test --encoder=kobert --save_path=./model/kobert_DOO7abs/best_model --gpus=0 --to_csv ../result/DATA.csv")
        summary = test_model(self.matchsum_args, self.model, matchsum_processed_data, self.special_tokens)
        # os.chdir(PROJECT_DIR)
        # summary = import_csv("./result/DATA.csv")
        return summary['index'][0][:n_candidates], summary['probs'][0][:n_candidates]
    
    def summarize_only_text(self, text, n_candidates=1):
        bert = df(text, self.tokenizer)
        index = test(False, bert, self.trainer)
        matchsum_processed_data = get_candidates_mp(self.tokenizer, text, index)
        summary = test_model(self.matchsum_args, self.model, matchsum_processed_data)
        return summary['index'][0][:n_candidates], summary['probs'][0][:n_candidates]
