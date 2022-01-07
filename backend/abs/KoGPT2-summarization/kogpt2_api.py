from flask import Flask, Response, request
import json
import time

import torch
import yaml
from train import KoGPTConditionalGeneration
from utils import generate_next_token

import logging
import re
from datetime import datetime

DEVICE = 1

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

    SUMMARY = '<unused1>'
    EOS = '</s>'
    
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
    eos_id = tokenizer.encode(EOS)[0]
    input_ids = tokenizer.encode(text)
    logging.info("{} len : {}".format(model_text, len(input_ids)))
    input_ids = input_ids[:1023] + tokenizer.encode(SUMMARY)
    input_ids = torch.tensor(input_ids)
    input_ids = input_ids.unsqueeze(0)

    # Generate abstractive summarize
    
    while True:
        if input_ids.size(1)>1024 :
            if len(text) == 0:
                logging.info("Error returned -- Text is too long")
                return json.dumps({"summary": "ERROR! Text is too long"}, ensure_ascii=False)
        
        pred = model.model(input_ids)
        next_token = generate_next_token(   pred.logits,
                                            temperature=1.0,
                                            top_k=0,
                                            top_p=0.9
                                        )
        if next_token.item() == eos_id:
            break;
        else:
            input_ids = torch.cat([input_ids, next_token.unsqueeze(0)], 1)
    
    # Get summarize and score
    # score = output.sequences_scores.tolist()[0]
    output = tokenizer.decode(input_ids[0]).split(SUMMARY)[-1].strip()
    tot_time = time.time() - start
    logging.info("{} output: {}".format(model_text, output))
    logging.info("{} time: {}".format(model_text, tot_time))

    return json.dumps({
            "summary": output,
            "time": tot_time
        }, ensure_ascii=False)

@app.route('/api/kogpt2', methods=['POST', 'OPTIONS'])
def kogpt2_summarize():

    response = Response()

    if request.method == 'OPTIONS':
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "POST")
    elif request.method == 'POST':
        response.headers.add("Access-Control-Allow-Origin", "*")
        data = request.get_json()
        text = data["text"]
        response_data = summarize(tokenizer, model, text, "kogpt2")
        response.set_data(response_data)
    
    return response


@app.route('/api/test', methods=['GET', 'POST', 'OPTIONS'])
def test_api():
    result = Response()
    result.headers.add('Access-Control-Allow-Origin', "*")
    result.headers.add('Access-Control-Allow-Headers', "*")
    result.set_data(json.dumps({"body": "TEST"}))

    return result

if __name__ == '__main__':
    with open("./log/model1/tb_logs/default/version_2/hparams.yaml") as f:
        hparams = yaml.load(f)
    model = KoGPTConditionalGeneration.load_from_checkpoint("./log/model1/model_chp/epoch=03-val_loss=1.443.ckpt", hparams=hparams)
    model = model.cuda(DEVICE)
    tokenizer = model.tokenizer
    # tok_kobart = get_kobart_tokenizer()
    
    # app.run(debug=True, port=9886)
    # app.run(host="112.175.32.78", port=9500)
    app.run(host="14.49.45.139", port=8443)