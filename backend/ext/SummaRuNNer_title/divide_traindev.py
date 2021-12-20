import random
import json

def import_json(path):
    data = []
    with open(path) as f:
        for line in f:
            data.append(json.loads(line))
    return data

def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        for row in data:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main():
    data = import_json("data/AIHUB_data_with_title.jsonl")
    train_ratio = 0.99
    
    random.shuffle(data)
    train_data = data[:-10000]
    val_data = data[-10000:]
    write_json("data/train_AIHUB.jsonl", train_data)
    write_json("data/val_AIHUB.jsonl", val_data)

def main2():
    data = import_json("data/train_with_title.jsonl")
    for i, d in enumerate(data):
        label = d['labels']
        label = label.split("\n")
        label = [int(l) for l in label]
        doc = d['doc'].split("\n")
        if len(doc) != len(label) + 1:
            print(len(doc), len(label), i)
    
    print("in val")
    data = import_json("data/val_with_title.jsonl")
    for i, d in enumerate(data):
        label = d['labels']
        label = label.split("\n")
        label = [int(l) for l in label]
        doc = d['doc'].split("\n")
        max_sent_num = min(50,len(doc))
        doc = doc[:max_sent_num]
        label = label[:max_sent_num]
        if len(doc) != len(label) + 1:
            print(len(doc), len(label), i)


main2()