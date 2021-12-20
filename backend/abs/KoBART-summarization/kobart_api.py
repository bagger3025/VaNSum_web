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

    #     # if type(text) != list:
    #     #     logging.info("Error returned -- Text is not list")
    #     #     response.set_data(json.dumps({"summary": "ERROR! Text is not list"}, ensure_ascii=False))
    #     #     return response
    #     # logging.info("kobart text: {}".format(str(text)))
    #     # text = " ".join(text)
    #     # if len(text.strip()) == 0:
    #     #     logging.info("Error returned -- Text is empty")
    #     #     response.set_data(json.dumps({"summary": "ERROR! Text is empty"}, ensure_ascii=False))
    #     #     return response
    #     # text = text.replace("\n", " ")
    #     # start = time.time()
    #     # input_ids = tokenizer_kobart.encode(text)[:1024]
    #     # input_ids = torch.tensor(input_ids)
    #     # input_ids = input_ids.unsqueeze(0)
    #     # output = kobart_summarizer.generate(input_ids, eos_token_id=1, max_length=512, num_beams=5, no_repeat_ngram_size=5, output_scores=True, return_dict_in_generate=True)
    #     # score = output.sequences_scores.tolist()[0]
    #     # output = tokenizer_kobart.decode(output.sequences[0], skip_special_tokens=True)
    #     # end = time.time()

    #     # result = {
    #     #     "summary": output,
    #     #     "score": score,
    #     #     "time": end - start
    #     # }
    #     # logging.info("kobart output: {}".format(output))
    #     # logging.info("kobart time: {}".format(end - start))
    #     response.set_data(json.dumps(result, ensure_ascii=False))
    # return response

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
        # print(data)
        text = data["text"]
        response_data = summarize(tok_rdrop, model_rdrop, text, "kobart rdrop")
        response.set_data(response_data)

        # logging.info("kobart rdrop text: {}".format(str(text)))
        # if type(text) != list:
        #     logging.info("Error returned -- Text is not list")
        #     response.set_data(json.dumps({"summary": "ERROR! Text is not list"}, ensure_ascii=False))
        #     return response
        # text = " ".join(text)
        # text = text.replace("\n", " ")
        # if len(text.strip()) == 0:
        #     logging.info("Error returned -- Text is empty")
        #     response.set_data(json.dumps({"summary": "ERROR! Text is empty"}, ensure_ascii=False))
        #     return response
        # start = time.time()
        # input_ids = tokenizer_kobart_rdrop.encode(text)[:1024]
        # input_ids = torch.tensor(input_ids)
        # input_ids = input_ids.unsqueeze(0)
        # output = rdrop_summarizer.generate(input_ids, eos_token_id=1, max_length=512, num_beams=5, no_repeat_ngram_size=5, output_scores=True, return_dict_in_generate=True)
        # score = output.sequences_scores.tolist()[0]
        # output = tokenizer_kobart_rdrop.decode(output.sequences[0], skip_special_tokens=True)
        # end = time.time()

        # output2 = rdrop_magazine_summarizer.generate(input_ids, eos_token_id=1, max_length=512, num_beams=5, no_repeat_ngram_size=5, output_scores=True, return_dict_in_generate=True)
        # output2 = tokenizer_kobart_rdrop.decode(output2.sequences[0], skip_special_tokens=True)

        # result = {
        #     "summary": output + "\n\n\n" + output2,
        #     "score": score,
        #     "time": end - start
        # }
        # logging.info("kobart rdrop output: {}".format(result))
        # response.set_data(json.dumps(result, ensure_ascii=False))
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
        # logging.info("kobart rdrop book text: {}".format(str(text)))
        # if type(text) != list:
        #     logging.info("Error returned -- Text is not list")
        #     response.set_data(json.dumps({"summary": "ERROR! Text is not list"}, ensure_ascii=False))
        #     return response
        # text = " ".join(text)
        # text = text.replace("\n", " ")
        # text = re.sub(r" +", " ", text)
        # text = text.strip()
        # if len(text) == 0:
        #     logging.info("Error returned -- Text is empty")
        #     response.set_data(json.dumps({"summary": "ERROR! Text is empty"}, ensure_ascii=False))
        #     return response
        # start = time.time()
        # input_ids = tokenizer_kobart_rdrop.encode(text)
        # logging.info("kobart rdrop book tensor size: {}".format(len(input_ids)))
        # input_ids = input_ids[:1024]
        # input_ids = torch.tensor(input_ids)
        # input_ids = input_ids.unsqueeze(0)
        # output = rdrop_book_summarizer.generate(input_ids, decoder_start_token_id=tokenizer_kobart_rdrop_book.eos_token_id,
        #                                         eos_token_id=tokenizer_kobart_rdrop_book.eos_token_id, max_length=512, 
        #                                         num_beams=5, no_repeat_ngram_size=5, output_scores=True, return_dict_in_generate=True)
        # score = output.sequences_scores.tolist()[0]
        # output = tokenizer_kobart_rdrop.decode(output.sequences[0], skip_special_tokens=True)
        # end = time.time()

        # result = {
        #     "summary": output,
        #     "score": score,
        #     "time": end - start
        # }
        # logging.info("kobart rdrop book output: {}".format(result))
        # response.set_data(json.dumps(result, ensure_ascii=False))
    return response

@app.route('/api/test', methods=['GET', 'POST', 'OPTIONS'])
def test_api():
    result = Response()
    result.headers.add('Access-Control-Allow-Origin', "*")
    result.headers.add('Access-Control-Allow-Headers', "*")
    result.set_data(json.dumps({"body": "TEST"}))

    return result

if __name__ == '__main__':
    model_kobart = BartForConditionalGeneration.from_pretrained("./kobart_model")
    model_rdrop = BartForConditionalGeneration.from_pretrained("./kobart_rdrop_model_drop20")
    model_rdrop_magazine = BartForConditionalGeneration.from_pretrained("./kobart_rdrop_summary1110")
    model_rdrop_book = BartForConditionalGeneration.from_pretrained("./kobart_rdrop_summary1817")
    tok_kobart = get_kobart_tokenizer()
    tok_rdrop = get_kobart_tokenizer()
    tok_rdrop_magazine = get_kobart_tokenizer()
    tok_rdrop_book = get_kobart_tokenizer()
    # app.run(debug=True, port=9886)
    app.run(host="112.175.32.78", port=9500)