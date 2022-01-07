import yaml
import torch
import pandas as pd
import json
from tqdm import tqdm

from train import KoGPTConditionalGeneration
from utils import generate_next_token

from rouge_metric import Rouge
import argparse
import re
import os

DEVICE = 0
TEST_FILE = "data/test_aihub_1-1.tsv"

def read_jsonl(path):
    data = []
    with open(path, "r", encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def read_tsv(path):
    df = pd.read_csv(path, sep="\t")
    data = []
    for i in range(df.shape[0]):
        data.append({
            "article_original": df.loc[i, "news"],
            "summary": df.loc[i, "summary"]
        })
    return data

def read_data():
    # read_jsonl("data/AIHUB_final_val.jsonl")
    return read_tsv(TEST_FILE)

def write_jsonl(path, data):
    with open(path, "w", encoding="utf-8") as f:
        for d in data:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

def model_load(args):
    path = args.model_path
    with open(args.hparams_path) as f:
        hparams = yaml.load(f)
    model = KoGPTConditionalGeneration.load_from_checkpoint(path, hparams=hparams)
    model = model.cuda(DEVICE)
    return model

class RougeScorer:
    def __init__(self):
        self.rouge_evaluator = Rouge(
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

    def compute_rouge(self, ref_df, hyp_df):
        #ref_df = pd.read_csv(ref_path)
        #hyp_df = pd.read_csv(hyp_path)
        hyp_df.iloc[:,1] = hyp_df.iloc[:,1].fillna(' ')
        ids = ref_df['id']
        hyp_df = hyp_df[hyp_df['id'].isin(ids)]
        hyp_df.index = ref_df.index

        ref_df = ref_df.sort_values(by=["id"])
        hyp_df = hyp_df.sort_values(by=["id"])
        ref_df["id"] = ref_df["id"].astype(int)
        hyp_df["id"] = hyp_df["id"].astype(int)

        hyps = [tuple(row) for row in hyp_df.values]
        refs = [tuple(row) for row in ref_df.values]

        reference_summaries = []
        generated_summaries = []

        for ref_tp, hyp_tp in zip(refs, hyps):
            ref_id, ref = ref_tp
            hyp_id, hyp = hyp_tp

            assert ref_id == hyp_id

            reference_summaries.append(ref)
            generated_summaries.append(hyp)

        scores = self.rouge_evaluator.get_scores(generated_summaries, reference_summaries)
        str_scores = self.format_rouge_scores(scores)
        return str_scores

    def format_rouge_scores(self, scores):
        return "ROUGE-1: {:.3f}, ROUGE-2: {:.3f}, ROUGE-l: {:.3f}".format(
            scores["rouge-1"]["f"],
            scores["rouge-2"]["f"],
            scores["rouge-l"]["f"],
        )

# def tokenize():
    # tokenizer = get_kobart_tokenizer()
    # data = read_jsonl("data/AIHUB_final_val.jsonl")
    # tokens = []
    # for d in tqdm(data):
    #     text = " ".join(d["article_original"])
    #     text = text.replace("\n", " ")
    #     input_ids = tokenizer.encode(text)
    #     tokens.append({"id": d["id"], "tokens": input_ids, "abstractive": d["abstractive"]})
    # write_jsonl("data/AIHUB_final_val_tokens.jsonl", tokens)

def inference(args):
    model = model_load(args)
    tokenizer = model.tokenizer
    data = read_data()
    answer = []
    SUMMARY = '<unused1>'
    EOS = '</s>'
    for d in tqdm(data):
    # for d in tqdm(data[:500]):
        text = d["article_original"]
        text = text.replace('\n', '')
        
        # if(text.startswith(']')):
        #     continue
        # text = re.sub(" +", " ", text)
        # text = text.strip()
        input_ids = tokenizer.encode(text) + tokenizer.encode(SUMMARY)
        # print(input_ids)
        # print(tokenizer.decode(input_ids))
        input_ids = torch.tensor(input_ids, device=DEVICE).unsqueeze(0)
        
        eos_id = tokenizer.encode(EOS)[0]
        
        # output = model.generate(input_ids, eos_token_id=1, max_length=512, num_beams=5, no_repeat_ngram_size=args.ngram_size, num_return_sequences=1)
        # print(output)
        # output_lists = []
        # for o in output:
        #     output_text = tokenizer.decode(o, skip_special_tokens=True)
        #     output_lists.append(output_text)

        temperature = 1.0
        top_p = 0.9
        top_k = 0
        while True:
            # print(input_ids.shape, end=' ')
            if(input_ids.size(1)>1024):
                # input_ids = input_ids.squeeze()[512:].unsqueeze(0)
                # print('*truc')
                # print('*q')
                break;
                
            pred = model.model(input_ids)
            next_token = generate_next_token(pred.logits, temperature=temperature, top_p=top_p, top_k=top_k)
            # print(f'{next_token.shape=}')

            if next_token.item() == eos_id:
                # print('b*')
                break
            else:
                input_ids = torch.cat([input_ids, next_token.unsqueeze(0)],1)
                # print("m*", end='')

        if(input_ids.size(1)>1024):
                print('skip...') # skip this data..
                continue
        
        output = tokenizer.decode(input_ids[0]).split(SUMMARY)[-1].strip()        
        
        answer.append({'summary': output, "abstractive": d["summary"]})
        # print(d["article_original"])
        print(d["summary"]) #정답요약==abstractive
        print(output) #모델요약
        # if len(answer) > 5:
        #     break

    return answer

def save_to_csv(path, data):
    if not os.path.exists(path):
        data.to_csv(path, sep=",", encoding="utf-8", index=False)
    else:
        print('appending..')
        data.to_csv(path, mode='a', header=False, sep=",", encoding="utf-8", index=False)

def get_reference_df():
    data = read_data()
    return pd.DataFrame(data).loc[:, ["id", "abstractive"]]

def load_summary_and_print_rouge(path):
    # hyp_df = pd.read_csv(path, dtype=str)
    # reference_df = get_reference_df()

    df = pd.read_csv(path, dtype=str)
    hyp_df = []
    reference_df = []
    for i in range(df.shape[0]):
        hyp_df.append({"id": str(i), "summary":df.loc[i, "summary"]})
        reference_df.append({"id": str(i), "abstractive":df.loc[i, "abstractive"]})
    hyp_df = pd.DataFrame(hyp_df)
    reference_df = pd.DataFrame(reference_df)

    rs = RougeScorer()
    print(rs.compute_rouge(reference_df, hyp_df))

def init(args):

    # answer = inference(model_path=args.model_path, args=args)
    answer = inference(args)
    answer_df = pd.DataFrame(answer)
    save_to_csv(args.save_path, answer_df)

    # load_summary_and_print_rouge("rdrop210_block_3grams_result.csv")
    load_summary_and_print_rouge(args.save_path)

parser = argparse.ArgumentParser()

parser.add_argument('--model_path', type=str, default="./log/model1/model_chp/epoch=03-val_loss=1.443.ckpt")
parser.add_argument('--hparams_path', type=str, default="./log/model1/tb_logs/default/version_2/hparams.yaml")
parser.add_argument('--save_path', type=str, default="")
# parser.add_argument('--ngram_size', type=int, default=5)

args = parser.parse_args()

init(args)