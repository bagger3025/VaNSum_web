# coding: utf-8
import argparse
import codecs
import lxml.etree as ET
import os
import regex
from tqdm import tqdm
from konlpy.tag import Kkma #Mecab
import time
from concurrent.futures import ThreadPoolExecutor
import threading

# arguments setting
parser = argparse.ArgumentParser()
parser.add_argument('--max_corpus_size', type=int, default=1000000000,
                    help='the maximum size of the corpus. Feel free to adjust it according to your computing power.')
parser.add_argument('--xml_name', type=str,
                    help='name of the xml file which will be processed')
args = parser.parse_args()

kkma = Kkma()
# mecab = Mecab()
print("kkma succesfuly loaded!")

max_corpus_size = args.max_corpus_size
fname = args.xml_name
print(f"max_corpus_size={max_corpus_size}")
print(f"fname={fname}")

def remove_empty_line(text):
    text = regex.sub(r"[ ]{2,}", " ", text)
    text = regex.sub(r"([ ]*\n)+", "\n", text)
    text = text.strip()
    return text

def clean_text(text):
    # Common
    text = regex.sub(r"<ref>.+?<\/ref>", "", text)  # remove reference links
    text = regex.sub(r"<[^>]+>", "", text)  # remove html tags
    text = regex.sub(r"&[a-z]+;", "", text)  # remove html entities
    text = regex.sub(r"{{.+?}}", "", text)  # remove markup tags
    text = regex.sub(r"{.+?}", "", text)  # remove markup tags
    # remove link target strings
    # text = regex.sub(r"\[\[([^\]]+\|)", "", text)
    text = regex.sub(r"\[\[([^\]]+\:.+?]])", "", text)  # remove media links

    text = regex.sub(r"[']{5}", "", text)  # remove italic+bold symbols
    text = regex.sub(r"[']{3}", "", text)  # remove bold symbols
    text = regex.sub(r"[']{2}", "", text)  # remove italic symbols

    # Replace unacceptable characters with a space.
    text = regex.sub(r"[^ \r\n가-힣.?!]", " ", text)
    text = remove_empty_line(text)
    return text


def sentence_segment(text):
    sents = regex.split(r"([.?!])?[\n]+|[.?!] ", text)
    return sents


def word_segment(sent):
    words = [word for word, _ in kkma.pos(sent)]
    return words


def handle_text(elem):
    global max_corpus_size
    text = elem.text
    try:
        t1 = time.time()
        text = clean_text(text)
        t2 = time.time()
        sents = sentence_segment(text)
        t3 = time.time()
        sents_list = []

        words_list = []
        with ThreadPoolExecutor(max_workers=1) as ex:
            for sent in sents:
                if sent is None:
                    continue
                words = ex.submit(word_segment, sent)
                # words = word_segment(sent)
                words_list.append(words)
        for word in words_list:
            words = word.result()
            if len(words) <= 10:
                continue
            sents_list.append(" ".join(words))
        t4 = time.time()
        if os.path.isfile("data/ko.txt"):
            fsize = os.path.getsize("data/ko.txt")
            if fsize > max_corpus_size:
                return False
        if len(sents_list) > 0:
            with codecs.open("data/ko.txt", 'a', 'utf-8') as fout:
                fout.write("\n".join(sents_list) + "\n")
        t5 = time.time()
        # print(f"clean_text={t2 - t1}\nsentence_segment={t3-t2}\nprocess_sents={t4-t3}\nwriting={t5-t4}")
    except:
        return False
    elem.clear()  # We need to save memory!
    return True

def build_corpus():
    global max_corpus_size, fname

    ns = "{http://www.mediawiki.org/xml/export-0.10/}"  # namespace

    if os.path.isfile("data/ko.txt"):
        os.remove("data/ko.txt")

    
    with ThreadPoolExecutor(max_workers=16) as ex:
        fs = [ex.submit(handle_text, elem) for _, elem in ET.iterparse("data/{}".format(fname), tag=ns+"text")]
        # fs = ex.map(handle_text, ET.iterparse("data/{}".format(fname), tag=ns+"text"))
        # for _, elem in tqdm(ET.iterparse("data/{}".format(fname), tag=ns+"text")):
        #     ex.submit(handle_text, elem)
            # th = threading.Thread(target=handle_text, args=(elem,))
            # th.start()

        for f in tqdm(fs):
            f.result()


    # for th in tqdm(threading.enumerate()):
    #     if th is main_thread:
    #         continue
    #     th.join()
    

    # with codecs.open("data/ko.txt", 'w', 'utf-8') as fout:
    #     i = 1
    #     ns = "{http://www.mediawiki.org/xml/export-0.10/}"  # namespace
    #     for _, elem in tqdm(ET.iterparse("data/{}".format(fname), tag=ns+"text")):
    #         running_text = elem.text
    #         try:
    #             running_text = clean_text(running_text)
    #             sents = sentence_segment(running_text)
    #             for sent in sents:
    #                 if sent is None:
    #                     continue
    #                 words = word_segment(sent)
    #                 if len(words) <= 10:
    #                     continue
    #                 fout.write(" ".join(words) + "\n")
    #         except:
    #             continue  # it's okay as we have a pretty big corpus!
    #         elem.clear()  # We need to save memory!
    #         if i % 1000 == 0:
    #             print(i)
    #             fsize = os.path.getsize("data/ko.txt")
    #             if fsize > max_corpus_size:
    #                 break
    #         i += 1

if __name__ == "__main__":
    build_corpus()

    print("Done")
