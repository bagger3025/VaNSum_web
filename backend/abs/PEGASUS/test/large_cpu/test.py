#from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import PegasusTokenizer, PegasusForConditionalGeneration
import torch
import time

model = PegasusForConditionalGeneration.from_pretrained('/home/skkuedu/VANSum/backend/PEGASUS/large/model-210000')
tokenizer = PegasusTokenizer.from_pretrained('/home/skkuedu/VANSum/backend/PEGASUS/large/model-210000')
input = "/home/skkuedu/VANSum/backend/cnn_dailymail_test/inputs-210000-.dev.txt"

f = open(input, 'r')
lines = f.readlines()
total= 0.0
batch_total= 0.0
translate_total= 0.0
decode_total= 0.0

for line in lines:
    if line[:4] == "----":
        pass
    elif line[:4] == "[0]:":
        pass
    else:
        source = line
        start = time.time()
        
        batch_start = time.time()
        batch = tokenizer(source, truncation=True, padding='longest', return_tensors="pt")
        batch_time = time.time() - batch_start
        
        translate_start = time.time()
        translated = model.generate(**batch)
        translate_time = time.time() - translate_start
        
        decode_start = time.time()
        result = tokenizer.batch_decode(translated, skip_special_tokens=True)
        decode_time = time.time() - decode_start
        
        t = time.time() - start
        
        batch_total += batch_time
        translate_total += translate_time
        decode_total += decode_time
        total += t
        
        print(batch_time, translate_time, decode_time, t)

average = total/1000
average_batch = batch_total/1000
average_translate = translate_total/1000
average_decode = decode_total/1000

print("-----------------------------------------")
print(average_batch, average_translate, average_decode, average)

