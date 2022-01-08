from flask import Flask, Response, request
import json
import time
from transformers import PegasusTokenizer, PegasusForConditionalGeneration
import torch
import re
from datetime import datetime
from newspaper import Article
from rouge_score import rouge_scorer

today = datetime.now()

app = Flask(__name__)

def summarize(tokenizer, model, text, index, model_text=""):
    if type(text) == list:
        text = " ".join(text)
        text = text.replace("\n", " ")
        text = re.sub(r" +", " ", text)
        text = text.strip()
    if len(text) == 0:
        return json.dumps({"summary": "ERROR! Text is empty"}, ensure_ascii=False)

    if text.startswith("https://"):
        article = Article(text, language = 'en')
        article.download()
        article.parse()
        text = article.text
    
    startTIME = time.time()

    # Generate abstractive summarize
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    batch = tokenizer(text, truncation=True, padding='longest', return_tensors="pt").to(device)
    translated = model.generate(**batch)
    output= tokenizer.batch_decode(translated, skip_special_tokens=True)
    output= output[0]
    output = output.replace('<n>', '\n')
 
    tot_time = time.time() - startTIME
    
    if(index==-1): 
        rouge1 = "NULL"
        rouge2 = "NULL"
        rougeL = "NULL"
    else:
        ind = "-----:" + str(index) + "\n"
        next = "-----:" + str(index+1) + "\n"
        answer=""
        f2 = "/home/vaiv2021/shbin/pegasus/ckpt/pegasus_ckpt/cnn_dailymail/targets-210000-.dev.txt"
        tmp=0
        f = open(f2, 'r')
        lines = f.readlines()
        for line in lines:
            if(line==next):
                tmp=0
                break;
            if tmp==1:
                answer+=line
            if(line==ind):
                tmp=1
        
        scorer = rouge_scorer.RougeScorer(['rouge1','rouge2','rougeL'], use_stemmer=True)
        rouge1 = scorer.score(answer,output)['rouge1'].fmeasure
        rouge1 = round(rouge1, 3)
        rouge2 = scorer.score(answer,output)['rouge2'].fmeasure
        rouge2 = round(rouge2, 3)
        rougeL = scorer.score(answer,output)['rougeL'].fmeasure
        rougeL = round(rougeL, 3)


    return json.dumps({
            "origin": text,
            "summary": output,
            "time": tot_time,
            "rouge1": rouge1,
            "rouge2": rouge2,
            "rougeL": rougeL,
        }, ensure_ascii=False)

@app.route('/api/pegasus_large', methods=['POST', 'OPTIONS'])
def pegasus_large_summarize():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        text = data["text"]
        index = data["index"]
        response_data = summarize(tok_pegasus_large, model_pegasus_large, text, index, "pegasus_large")
        response.set_data(response_data)
    
    return response

@app.route('/api/pegasus_large_skku', methods=['POST', 'OPTIONS'])
def pegasus_large_skku_summarize():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        text = data["text"]
        index = data["index"]
        response_data = summarize(tok_pegasus_large_skku, model_pegasus_large_skku, text, index, "pegasus_large_skku")
        response.set_data(response_data)
    
    return response

@app.route('/api/pegasus_base_skku', methods=['POST', 'OPTIONS'])
def pegasus_base_skku_summarize():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        text = data["text"]
        index = data["index"]
        response_data = summarize(tok_pegasus_base_skku, model_pegasus_base_skku, text, index, "pegasus_base_skku")
        response.set_data(response_data)
    
    return response

if __name__ == '__main__':
    model_pegasus_large = PegasusForConditionalGeneration.from_pretrained('/home/vaiv2021/shbin/pegasus/model-210000').cuda()
    tok_pegasus_large = tokenizer = PegasusTokenizer.from_pretrained('/home/vaiv2021/shbin/pegasus/model-210000')

    model_pegasus_large_skku = PegasusForConditionalGeneration.from_pretrained('/home/vaiv2021/shbin/pegasus/model-60000').cuda()
    tok_pegasus_large_skku = tokenizer = PegasusTokenizer.from_pretrained('/home/vaiv2021/shbin/pegasus/model-60000')

    model_pegasus_base_skku = PegasusForConditionalGeneration.from_pretrained('/home/vaiv2021/shbin/pegasus_base/model-63000').cuda()
    tok_pegasus_base_skku = tokenizer = PegasusTokenizer.from_pretrained('/home/vaiv2021/shbin/pegasus_base/model-63000')
    # app.run(debug=True, port=9886)
    app.run(host="14.49.45.139", port=8080)
