import torch
from kobart import get_kobart_tokenizer
from transformers.models.bart import BartForConditionalGeneration
from train import KoBARTConditionalGeneration, KoBARTRDropGeneration
import pandas as pd
import json
from tqdm import tqdm
from time import time 
from rouge_metric import Rouge

DEVICE = 1

def read_jsonl(path):
    data = []
    with open(path, "r", encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data

def write_jsonl(path, data):
    with open(path, "w", encoding="utf-8") as f:
        for d in data:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

def model_load(path):
    model = BartForConditionalGeneration.from_pretrained(path)
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

def tokenize():
    tokenizer = get_kobart_tokenizer()
    data = read_jsonl("data/AIHUB_final_val.jsonl")
    tokens = []
    for d in tqdm(data):
        text = " ".join(d["article_original"])
        text = text.replace("\n", " ")
        input_ids = tokenizer.encode(text)
        tokens.append({"id": d["id"], "tokens": input_ids, "abstractive": d["abstractive"]})
    write_jsonl("data/AIHUB_final_val_tokens.jsonl", tokens)

def inference(model_path):
    model = model_load(model_path)
    tokenizer = get_kobart_tokenizer()
    data = read_jsonl("data/AIHUB_final_val_tokens.jsonl")
    answer = []
    for d in tqdm(data):
        input_ids = d["tokens"]
        input_ids = torch.tensor(input_ids, device=DEVICE)
        input_ids = input_ids.unsqueeze(0)
        # now = time()
        output = model.generate(input_ids, eos_token_id=1, max_length=512, num_beams=5)
        # print(time() - now)
        # print(output)
        # now = time()
        output = tokenizer.decode(output[0], skip_special_tokens=True)
        # print(time() - now)
        # print(output)
        # print(d['abstractive'])
        answer.append({"id": d['id'], 'summary': output})
    return answer

def save_to_csv(path, data):
    data.to_csv(path, sep=",", encoding="utf-8", index=False)

def get_reference_df():
    data = read_jsonl("data/AIHUB_final_val.jsonl")
    return pd.DataFrame(data).loc[:, ["id", "abstractive"]]

def load_summary_and_print_rouge(path):
    hyp_df = pd.read_csv(path, dtype=str)
    reference_df = get_reference_df()
    rs = RougeScorer()
    print(rs.compute_rouge(reference_df, hyp_df))

def init():

    # tokenize()

    # answer = inference(model_path="./kobart_rdrop_summary210")

    # answer_df = pd.DataFrame(answer)
    # save_to_csv("rdrop210_result.csv", answer_df)

    load_summary_and_print_rouge("kobart_result.csv")
    load_summary_and_print_rouge("rdrop207_result.csv")
    load_summary_and_print_rouge("rdrop210_result.csv")

init()