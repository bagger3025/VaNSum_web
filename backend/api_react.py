from flask import Flask, Response, request
import json
import jsonlines
import time
import numpy as np
import requests
from konlpy.tag import Kkma
from kss import split_sentences
from load_article import load_article_from_url, load_article_from_url_mk
from naversum import make_gsum, make_gsum_title
from werkzeug.utils import secure_filename
from random import *

import ext.TextRank.textrank as textrank
import ext.LexRank.lexrank as lexrank
from ext.SummaRuNNer.str_to_summarize import SummaRuNNer_Summarizer
from ext.SummaRuNNer_title.main import summary_with_title, pre_compare_title
from ext.mKoBertSum import kobertsum_summarizer, make_jsonlf
from ext.MatchSum.matchsum_summarizer import MatchSum_Summarizer

app = Flask(__name__)

TOPK = 3

def validate_data(text, topk, sort):
    if sort not in ['prob', 'sent']:
        return False, {
            "summary": "sort is not in ['prob', 'sent']"
        }
    if len(text) < 3:
        return False, {
            "summary": "text is too short"
        }
    if type(text) != list or type(text[0]) != str:
        return False, {
            "summary": "Wrong type of text"
        }
    if type(topk) != int:
        return False, {
            "summary": "Wrong type of topk"
        }
    return True, {"summary":"ok"}

# convert idx order from "prob order" to "sent order"
# ex) idx=[5,2,3], "probs=[0.7,0.5,0.3]" => "idx=[2,3,5]", probs=[0.5,0.3,0.7]
def probs_to_sents(idx, probs, topk):
    assert len(idx) == topk and len(probs) == topk

    idx_np = np.array(idx).argsort()
    idx = np.array(idx)[idx_np].tolist()
    probs = np.array(probs)[idx_np].tolist()
    return idx, probs

# delete some text, length of the text is less than 10
def preprocess_text(text):
    index_lists = []
    text_len = [len(t) >= 10 for t in text]
    index_lists = [i for i, _ in enumerate(text_len) if _ == False]
    text = np.delete(text, index_lists).tolist()
    return text, index_lists

# restore index with deleted indices
# ex) summary_list=[2,4,6], deleted_indices=[2,4,6] => [3,7,9]
def to_original_indices(summary_list, deleted_indices):
    deleted_indices.sort()
    for i in range(len(deleted_indices)):
        summary_list = [t + 1 if t >= deleted_indices[i] else t for t in summary_list]
    return summary_list

@app.route('/api/LexRank', methods=['POST', 'OPTIONS'])
def lexrank_summarize():
    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        text, topk, sort = data['text'], data['topk'], data['sort']
        text, index_lists = preprocess_text(text)
        ok, result = validate_data(text, topk, sort)
        if ok:
            start = time.time()
            print("====================LexRank Start====================")
            li, probs = lexrank.newssumModified(text, kkma, topk)
            if sort == "sent":
                li, probs = probs_to_sents(li, probs, topk)
            li = to_original_indices(li, index_lists)
            end = time.time()

            result = {
                "summary": li,
                "prob": probs,
                "time": end - start
            }
        response.set_data(json.dumps(result, ensure_ascii=False))
    return response

@app.route('/api/TextRank', methods=['POST', 'OPTIONS'])
def textrank_summarize():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        text, topk, sort = data['text'], data['topk'], data['sort']
        text, index_lists = preprocess_text(text)
        ok, result = validate_data(text, topk, sort)
        if ok:
            start = time.time()
            li, probs = textrank.newssumModified(text, kkma, topk)
            if sort == "sent":
                li, probs = probs_to_sents(li, probs, topk)
            li = to_original_indices(li, index_lists)
            end = time.time()

            result = {
                "summary": li,
                "prob": probs,
                "time": end - start
            }
        response.set_data(json.dumps(result, ensure_ascii=False))
    return response

@app.route('/api/SummaRuNNer', methods=['POST', 'OPTIONS'])
def summarunner_summarize():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        text, topk, sort = data['text'], data['topk'], data['sort']
        text, index_lists = preprocess_text(text)
        ok, result = validate_data(text, topk, sort)
        if ok:
            start = time.time()
            li, probs = summaraunner_summarizer_model.summarize(text, n_sents=topk)
            if sort == 'sent':
                li, probs = probs_to_sents(li, probs, topk)
            li = to_original_indices(li, index_lists)
            end = time.time()

            result = {
                "summary": li,
                "prob": probs,
                "time": end - start
            }
        response.set_data(json.dumps(result, ensure_ascii=False))
    return response

@app.route('/api/KoBertSum', methods=['POST', 'OPTIONS'])
def kobertsum_summarize():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        text, topk, sort = data['text'], data['topk'], data['sort']
        text, index_lists = preprocess_text(text)
        ok, result = validate_data(text, topk, sort)
        if ok:
            start = time.time()
            make_jsonlf.mk_jsonl(text)
            _, li, probs = kobertsum_summarizer.bertSum(kobertsum_summarizer_model, n_sents=topk, sort_by_pred=True)
            # _, li, probs = kobertsum_summarizer.bertSum_with_title(kobertsum_summarizer_model_with_title, n_sents=topk, sort_by_pred=True)
            if sort == 'sent':
                li, probs = probs_to_sents(li, probs, topk)
            li = to_original_indices(li, index_lists)
            end = time.time()

            result = {
                "summary": li,
                "prob": probs,
                "time": end - start
            }
        response.set_data(json.dumps(result, ensure_ascii=False))
    return response

@app.route('/api/MatchSum', methods=['POST', 'OPTIONS'])
def matchsum_summarize():
    
    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        text, topk, sort = data['text'], data['topk'], data['sort']
        text, index_lists = preprocess_text(text)
        ok, result = validate_data(text, topk, sort)
        if ok:
            start = time.time()
            li, probs = matchsum_summarize_sub(text, topk)
            for i, li_ele in enumerate(li):
                li[i] = to_original_indices(li_ele, index_lists)
            end = time.time()

            result = {
                "summary": li,
                "prob": probs,
                "time": end - start
            }
        response.set_data(json.dumps(result, ensure_ascii=False))
    return response

def matchsum_summarize_sub(text, topk):
    INDEX_SENTNUM = 5
    def matchsum_1(text, topk):
        if INDEX_SENTNUM < len(text):
            make_jsonlf.mk_jsonl(text)
            _, index, _ = kobertsum_summarizer.bertSum(kobertsum_summarizer_model, sort_by_pred=True, n_sents=INDEX_SENTNUM, block_trigram=False)
        else:
            index = [t for t in range(len(text))]
        li, probs = matchsum_summarizer_model.summarize({
            "data": [{
                "id": "12",
                "article_original": text,
            }],
            "index": [{
                "sent_id": index
            }]
        }, topk)
        return li, probs
    def matchsum_2(text, topk):
        _, li, probs = matchsum_summarizer_model.summarize([{
            "id": "12",
            "article_original": text,
        }], topk)
        return li, probs

    li, probs = matchsum_1(text, topk)
    return li, probs

##### EXT with Title #####
@app.route('/api/KoBertSum_with_title', methods=['POST', 'OPTIONS'])
def kobertsum_summarize_with_title():
    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        text, topk, sort = data['text'], data['topk'], data['sort']
        text, index_lists = preprocess_text(text)
        ok, result = validate_data(text, topk, sort)
        if ok:
            start = time.time()
            make_jsonlf.mk_jsonl_with_title(text)
            _, li, probs = kobertsum_summarizer.bertSum_with_title(kobertsum_summarizer_model_with_title, n_sents=topk, sort_by_pred=True)
            if sort == 'sent':
                li, probs = probs_to_sents(li, probs, topk)
            #for with title
            for i in range(len(li)):
                li[i] = li[i] + 1
            li = to_original_indices(li, index_lists)
            end = time.time()

            result = {
                "summary": li,
                "prob": probs,
                "time": end - start
            }
        response.set_data(json.dumps(result, ensure_ascii=False))
    return response

@app.route('/api/SummaRuNNer_with_title', methods=['POST', 'OPTIONS'])
def summarunner_summarize_with_title():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        text, topk, sort = data['text'], data['topk'], data['sort']
        text, index_lists = preprocess_text(text)
        ok, result = validate_data(text, topk, sort)
        if ok:
            start = time.time()
            li, probs = summary_with_title(["\n".join(text)], summarunner_with_title_preloaded);
            if sort == 'sent':
                li, probs = probs_to_sents(li, probs, topk)
            for i in range(len(li)):
                li[i] = li[i] + 1
            li = to_original_indices(li, index_lists)
            end = time.time()

            result = {
                "summary": li,
                "prob": probs,
                "time": end - start
            }
        response.set_data(json.dumps(result, ensure_ascii=False))
    return response

##### ABS models #####
@app.route('/api/kobart', methods=['GET', 'POST', 'OPTIONS'])
def kobart_summarize():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        data = requests.post("http://112.175.32.78:9500/api/kobart", json=data)
        data = data.json()

        response.set_data(json.dumps(data, ensure_ascii=False))
    return response

@app.route('/api/kobart_rdrop', methods=['GET', 'POST', 'OPTIONS'])
def kobart_rdrop_summarize():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        data = requests.post("http://112.175.32.78:9500/api/kobart_rdrop", json=data)
        data = data.json()

        response.set_data(json.dumps(data, ensure_ascii=False))
    return response

@app.route('/api/kobart_rdrop_magazine', methods=['GET', 'POST', 'OPTIONS'])
def kobart_rdrop_magazine_summarize():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        data = requests.post("http://112.175.32.78:9500/api/kobart_rdrop_magazine", json=data)
        data = data.json()

        response.set_data(json.dumps(data, ensure_ascii=False))
    return response

@app.route('/api/kobart_rdrop_book', methods=['GET', 'POST', 'OPTIONS'])
def kobart_rdrop_book_summarize():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        data = requests.post("http://112.175.32.78:9500/api/kobart_rdrop_book", json=data)
        data = data.json()

        response.set_data(json.dumps(data, ensure_ascii=False))
    return response

@app.route('/api/KobertSumExtAbs', methods=['POST', 'OPTIONS'])
def kobertsumextabs_summarize():
    response=Response()
    
    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data= request.get_json()
        data = requests.post("http://112.175.32.78:9550/api/extabs", json=data)
        data = data.json()
        response.set_data(json.dumps(data, ensure_ascii=False))
    return response

@app.route('/api/pegasus_large', methods=['GET', 'POST', 'OPTIONS'])
def pegasus_large_summarize():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        data = requests.post("http://112.175.32.78:8800/api/pegasus_large", json=data)
        data = data.json()

        response.set_data(json.dumps(data, ensure_ascii=False))
    return response

@app.route('/api/pegasus_large_skku', methods=['GET', 'POST', 'OPTIONS'])
def pegasus_large_skku_summarize():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        data = requests.post("http://112.175.32.78:8800/api/pegasus_large_skku", json=data)
        data = data.json()

        response.set_data(json.dumps(data, ensure_ascii=False))
    return response

@app.route('/api/pegasus_base_skku', methods=['GET', 'POST', 'OPTIONS'])
def pegasus_base_skku_summarize():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        data = requests.post("http://112.175.32.78:8800/api/pegasus_base_skku", json=data)
        data = data.json()

        response.set_data(json.dumps(data, ensure_ascii=False))
    return response

##### other apis #####
@app.route('/api/original_text', methods=['POST', 'OPTIONS'])
def get_originaltext():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        article = load_article_from_url(data['url'])
        sentences = []
        for a in article:
            s = split_sentences(a, safe=True)
            sentences.extend(s)

        #for i in range(len(sentences)):
        #    sentences[i]=' '.join(sentences[i].split())
        result = {
            "text": sentences,
        }
        response.set_data(json.dumps(result, ensure_ascii=False))

    return response

@app.route('/api/original_text_with_title', methods=['POST', 'OPTIONS'])
def get_originaltext_with_title():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        article = load_article_from_url(data['url'])
        title = make_gsum_title(data['url'])
        
        sentences = []
        sentences.append(title)
        for a in article:
            s = split_sentences(a, safe=True)
            sentences.extend(s)

        result = {
            "text": sentences,
        }
        response.set_data(json.dumps(result, ensure_ascii=False))

    return response

@app.route('/api/mkreport', methods = ['POST', 'OPTIONS'])
def mkreport():
    response= Response()
    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        url = data["url"]
        text = load_article_from_url_mk(url)
        result={
                "text": text
            }

        response.set_data(json.dumps(result, ensure_ascii=False))
    return response

@app.route('/api/split_sentences', methods=['POST', 'OPTIONS'])
def split_sents():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        sentences = split_sentences(data['text'], safe=True)
        result = {
            "sent_list": sentences,
        }
        response.set_data(json.dumps(result, ensure_ascii=False))

    return response

@app.route('/api/naver_summary', methods=['POST', 'OPTIONS'])
def naver_gsum():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        gsum = make_gsum(data["url"])

        if gsum.strip() == "":
            gsum = "This article does not support Naver Summary Bot."
        else:
            gsum = gsum.split("\n\n")
        result = {
            "sent_list": gsum,
        }
        response.set_data(json.dumps(result, ensure_ascii=False))

    return response

@app.route('/api/fileupload', methods=['POST', 'OPTIONS'])
def fileInputs():
    response = Response()
    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        f = request.files['file']
        f.save(secure_filename(f.filename))

        i=randint(1,3012)
        j=0
        with jsonlines.open(f.filename) as reader:
            for obj in reader:
                if(i==j):
                    k=obj
                    break 
                j+=1

            result = {
                "article_original" : k["article_original"],
                "extractive" : k["extractive"]
            }

            response.set_data(json.dumps(result, ensure_ascii=False))

    return response

##### load random test set #####
@app.route('/api/aiHub', methods = ['POST', 'OPTIONS'])
def aiHub():
    response= Response()
    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        idx = data["random"]
        i=0
        j={}
        with jsonlines.open('sample.jsonl') as reader:
            for obj in reader:
                if(i==idx):
                    j=reader.read()
                    break
                i+=1
        if(data["type"]=="ext"):
            result={
            "article_original" : j["article_original"],
            "extractive" : j["extractive"]
        }
        else:
            result={
                "article_original":j["article_original"],
                "abstractive" : j["abstractive"]
            }


        response.set_data(json.dumps(result, ensure_ascii=False))
    return response

@app.route('/api/aiHub_title', methods = ['POST', 'OPTIONS'])
def aiHub_title():
    response= Response()
    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        idx = data["random"]
        # Temporary checking string
        if type(idx) == str:
            print("idx type is string!!")
        j=aihub_with_title[idx]
        
        if(data["type"]=="ext"):
            result={
                "article_original" : j["article_original"],
                "extractive" : j["extractive"]
            }
        else:
            result={
                "article_original":j["article_original"],
                "abstractive" : j["abstractive"]
            }
        
        response.set_data(json.dumps(result, ensure_ascii=False))
    return response

@app.route('/api/cnnTest', methods = ['POST', 'OPTIONS'])
def cnnTest():
    response= Response()
    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        num = data["random"]

        ind = "-----:" + str(num) + "\n"
        next = "-----:" + str(num+1) + "\n"
        input=""
        answer=""

        tmp=0
        for line in cnn_dailymail_inputs:
            if line==next:
                tmp=0
                break
            if tmp==1:
                input+=line
            if line==ind:
                tmp=1
        
        tmp=0
        for line in cnn_dailymail_targets:
            if line==next:
                tmp=0
                break
            if tmp==1:
                answer+=line
            if line==ind:
                tmp=1
            
        input = input.replace("[0]:\n", "")

        result={
                "article_original":input,
                "answer": answer,
                "index": num,
            }

        response.set_data(json.dumps(result, ensure_ascii=False))
    return response

@app.route('/api/test', methods=['GET', 'POST', 'OPTIONS'])
def test_api():
    result = Response()
    result.headers.add('Access-Control-Allow-Origin', "*")
    result.headers.add('Access-Control-Allow-Headers', "*")
    result.set_data(json.dumps({"body": "TEST"}))

    return result

if __name__ == '__main__':
    kkma = Kkma()
    summaraunner_summarizer_model = SummaRuNNer_Summarizer()
    matchsum_summarizer_model = MatchSum_Summarizer()
    kobertsum_summarizer_model = kobertsum_summarizer.preload()
    kobertsum_summarizer_model_with_title = kobertsum_summarizer.preload_with_title()
    summarunner_with_title_preloaded = pre_compare_title()

    with open("cnn_dailymail_test/inputs-210000-.dev.txt", 'r') as f:
        cnn_dailymail_inputs = f.readlines()
    with open("cnn_dailymail_test/targets-210000-.dev.txt", 'r') as f:
        cnn_dailymail_targets = f.readlines()
    with open("AIHUB_valid_with_title.jsonl", "r", encoding="utf-8") as f:
        aihub_with_title = [json.loads(line) for line in f]

    app.run(host="112.175.32.78", port=8443)