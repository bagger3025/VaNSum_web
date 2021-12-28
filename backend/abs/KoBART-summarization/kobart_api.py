from flask import Flask, Response, request
import json
import time
from transformers import BartForConditionalGeneration
from kobart import get_kobart_tokenizer
import torch
import logging
import re
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter(" [%(asctime)s, %(filename)s line %(lineno)s, %(levelname)s] %(message)s")

today = datetime.now()
filehandler = logging.FileHandler("api/{}.log".format(today.strftime("%m-%d-%H-%M-%S")))
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)

app = Flask(__name__)

def summarize(tokenizer, model, text, model_text=""):
    if type(text) != list:
        logging.info("Error returned -- Text is not list")
        return json.dumps({"summary": "ERROR! Text is not list"}, ensure_ascii=False)
    start = time.time()

    # Text preprocess
    logging.info("{} : text".format(text))
    text = " ".join(text)
    text = text.replace("\n", " ")
    text = re.sub(r" +", " ", text)
    text = text.strip()
    if len(text) == 0:
        logging.info("Error returned -- Text is empty")
        return json.dumps({"summary": "ERROR! Text is empty"}, ensure_ascii=False)
    
    # prepare input id
    input_ids = tokenizer.encode(text)
    logging.info(f"{model_text} len : {len(input_ids)}")
    input_ids = input_ids[:1024]
    logging.info(f"{model_text} input: {tokenizer.decode(input_ids)}")
    input_ids = torch.tensor(input_ids)
    input_ids = input_ids.unsqueeze(0)

    # Generate abstractive summarize
    output = model.generate(input_ids, decoder_start_token_id=tokenizer.eos_token_id, eos_token_id=tokenizer.eos_token_id, 
                            max_length=512, num_beams=5, no_repeat_ngram_size=5, 
                            output_scores=True, return_dict_in_generate=True)

    # Get summarize and score
    score = output.sequences_scores.tolist()[0]
    logging.info(f"{model_text} output.sequences: {output.sequences[0]}")
    output = tokenizer.decode(output.sequences[0], skip_special_tokens=True)
    tot_time = time.time() - start
    logging.info(f"{model_text} output: {output}")
    logging.info(f"{model_text} time: {tot_time}, score: {score}")

    return json.dumps({
            "summary": output,
            "score": score,
            "time": tot_time
        }, ensure_ascii=False)

@app.route('/api/kobart', methods=['POST', 'OPTIONS'])
def kobart_summarize():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        text = data["text"]
        response_data = summarize(tok_kobart, model_kobart, text, "kobart")
        response.set_data(response_data)
    
    return response

@app.route('/api/kobart_rdrop', methods=['POST', 'OPTIONS'])
def kobart_rdrop_summarize():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        text = data["text"]
        response_data = summarize(tok_rdrop, model_rdrop, text, "kobart rdrop")
        response.set_data(response_data)
    
    return response

@app.route('/api/kobart_rdrop_aihubnews', methods=['POST', 'OPTIONS'])
def kobart_rdrop_aihubnews_summarize():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        text = data["text"]
        response_data = summarize(tok_rdrop_aihubnews, model_rdrop_aihubnews, text, "kobart rdrop aihubnews")
        response.set_data(response_data)
    
    return response

@app.route('/api/kobart_rdrop_magazine', methods=['POST', 'OPTIONS'])
def kobart_rdrop_magazine_summarize():
    
    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        text = data["text"]
        response_data = summarize(tok_rdrop_magazine, model_rdrop_magazine, text, "kobart rdrop magazine")
        response.set_data(response_data)
    return response

@app.route('/api/kobart_rdrop_book', methods=['POST', 'OPTIONS'])
def kobart_rdrop_book_summarize():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        text = data["text"]
        response_data = summarize(tok_rdrop_book, model_rdrop_book, text, "kobart rdrop book")
        response.set_data(response_data)
    
    return response

@app.route('/api/test', methods=['GET', 'POST', 'OPTIONS'])
def test_api():
    result = Response()
    result.headers.add('Access-Control-Allow-Origin', "*")
    result.headers.add('Access-Control-Allow-Headers', "*")
    result.set_data(json.dumps({"body": "TEST"}))

    return result

def get_tok_model(path):
    return get_kobart_tokenizer(), BartForConditionalGeneration.from_pretrained(path)

if __name__ == '__main__':
    tok_kobart, model_kobart = get_tok_model("./kobart_model")
    tok_rdrop, model_rdrop = get_tok_model("./kobart_rdrop_model_drop20")
    tok_rdrop_magazine, model_rdrop_magazine = get_tok_model("./kobart_rdrop_summary1110")
    tok_rdrop_book, model_rdrop_book = get_tok_model("./kobart_rdrop_summary1817")
    tok_rdrop_aihubnews, model_rdrop_aihubnews = get_tok_model("./kobart_rdrop_summary2222")

    app.run(host="112.175.32.78", port=9500)