import os
import argparse
import jsonlines
from utils.rouge_metric import Rouge_kor
import pandas as pd
from pandas import DataFrame

class RougeScorer:
    def __init__(self):
        self.rouge_evaluator = Rouge_kor(
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
    
    def compute_rouge_each_document(self, title, summary):
        scores = self.rouge_evaluator.get_scores(summary, title)

        return scores["rouge-1"]["f"]
        str_scores = self.format_rouge_scores(scores)
        return str_scores

    def format_rouge_scores(self, scores):
        return "ROUGE-1: {:.3f}, ROUGE-2: {:.3f}, ROUGE-l: {:.3f}".format(
            scores["rouge-1"]["f"],
            scores["rouge-2"]["f"],
            scores["rouge-l"]["f"],
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-title_file", default="valid_id_title.jsonl", type=str, help="jsonl with id and title")
    parser.add_argument("-target_file", default="res_without_title.jsonl", type=str, help="jsonl with id and summarization result")
    parser.add_argument("-save_to", default="rouge_result_without_title.csv", type=str, help="csv storing compared result")
    args = parser.parse_args()

    id_title = dict()
    with jsonlines.open(args.title_file) as f:
        for line in f.iter():
            id_title[line["id"]] = line["title"]
    
    print("title_file {} exported".format(len(id_title)))
    rouge_scorer = RougeScorer()
    data = {"id": [], "title": [], "sent1_score": [], "sent2_score": [], "sent3_score": [], "total_score": []}
    number_of_targets = 0
    targets_total_score = 0
    with jsonlines.open(args.target_file) as f:
        for line in f.iter():
            number_of_targets += 1
            id = line["id"]
            title = id_title[line["id"]]
            summary = line["summary"]
            total_summary = ""
            for i in range(len(summary)):
                total_summary += summary[i]

            sent1_score = rouge_scorer.compute_rouge_each_document(title, summary[0])
            sent2_score = rouge_scorer.compute_rouge_each_document(title, summary[1])
            sent3_score = rouge_scorer.compute_rouge_each_document(title, summary[2])
            total_score = (sent1_score + sent2_score + sent3_score) / 3
            targets_total_score += total_score
            
            data["id"].append(id)
            data["title"].append(title)
            data["sent1_score"].append(round(sent1_score, 3))
            data["sent2_score"].append(round(sent2_score, 3))
            data["sent3_score"].append(round(sent3_score, 3))
            data["total_score"].append(round(total_score, 3))
    
    df = DataFrame(data)
    df.to_csv(args.save_to, index=False)

    targets_total_score = targets_total_score / number_of_targets
    with open(args.save_to, "a") as f:
        f.write("total average rouge score : {}".format(round(targets_total_score, 3)))


