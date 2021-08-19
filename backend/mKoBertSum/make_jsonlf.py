from konlpy.tag import Kkma
import json

def mk_jsonl(sentences):
    mkj = {
        'media' : "이코노미스트",
        'id' : "12345678900",
        'article_original': sentences,
    }

    with open('/home/skkuedu/TestSite/mKoBertSum/ext/data/raw/extractive_test_v2.jsonl', 'w') as f:
        json.dump(mkj, f, ensure_ascii=False)

    return True

def doc2jsonl(doc):
    kkma=Kkma()
    sentences= kkma.sentences(doc)

    for idx in range(0, len(sentences)):
            if len(sentences[idx])<=10:  #글자수가 10개 이하인 문장은 합친다.
                sentences[idx-1]+=(' '+ sentences[idx])
                sentences[idx] = ''

    mkj={
        'media' : "이코노미스트", 
        'id' : "12345678990",
        "article_original" : sentences,
    }

    with open('/home/skkuedu/TestSite/mKoBertSum/ext/data/raw/extractive_test_v2.jsonl', 'w') as f:
        json.dump(mkj, f, ensure_ascii=False)

    return True