# 전처리 관련 설명

## /api/original_text, /api/original_text_with_title, /api/mkreport

### Input

|키|타입|설명|
|---|---|---|
|url|문자열|네이버 뉴스 url주소|

- `/api/mkreport`의 경우 url은 MK증권의 분석 레포트 URL 주소

### Output

|키|타입|설명|
|---|---|---|
|text|문자열 배열|문장별로 나뉜 문자열 배열|

- 네이버 뉴스 url을 받아 안에 있는 기사를 문장을 나누어 리스트로 반환합니다.
- `original_text_with_title`의 경우 첫 문장은 제목이 됩니다.
- `mkreport`의 경우 안에 있는 레포트를 문장을 나누어 리스트로 반환합니다.

## /api/split_sentences

### Input

|키|타입|설명|
|---|---|---|
|text|문자열|원문 문자열|

### Output

|키|타입|설명|
|---|---|---|
|sent_list|문자열 배열|문장별로 나뉜 문자열 배열|

- 원문 텍스트를 받아 문장을 나누어 리스트로 반환합니다.

## /api/naver_summary

### Input

|키|타입|설명|
|---|---|---|
|url|문자열|네이버 뉴스기사 url주소|

### Output

|키|타입|설명|
|---|---|---|
|sent_list|문자열 배열|문장별로 나뉜 문자열 배열|

- 네이버 뉴스 기사 url을 받아 네이버 뉴스 요약문을 리스트로 반환합니다. 

- 없다면 "This article does not support Naver Summary Bot."라는 문자열로 반환합니다.

## /api/aiHub, /api/aiHub_title, /api/cnnTest

### Input
|키|타입|설명|
|---|---|---|
|random|숫자|AIHUB데이터의 인덱스|
|type|문자열|"ext" 또는 "abs"|

### Output

- type가 ext일 경우

|키|타입|설명|
|---|---|---|
|article_original|문자열 배열|AIHUB 데이터의 article_original|
|extractive|숫자 배열|AIHUB 데이터의 extractive|

- type가 abs일 경우

|키|타입|설명|
|---|---|---|
|article_original|문자열 배열|AIHUB 데이터의 article_original|
|abstractive|문자열|AIHUB 데이터의 abstractive|

- AIHUB 데이터의 인덱스를 받아 article_original과 extractive, abstractive를 반환합니다.
- `/api/cnnTest`의 경우 `cnn_dailymail_test` 데이터의 인덱스를 받아 article_original과 extractive, abstractive를 반환합니다.

# Extractive 모델 관련 설명

## /api/TextRank, /api/LexRank, /api/SummaRuNNer, /api/KoBertSum, /api/MatchSum
    
### Input
|키|타입|설명|
|---|---|---|
|text|문자열 배열|문장별로 나눈 원문|
|topk|숫자|추출할 문장 개수|
|sort|문자열|확률순 정렬: prob   문장순 정렬: sent|

### Output
|키|타입|설명|
|---|---|---|
|summary|숫자 배열|뽑힌 문장의 인덱스 배열|
|prob|숫자 배열|summary의 원소 각각에 대응되는 확률/점수|
|time|숫자|요약하는 데 걸린 시간|

- 각각의 모델에 대해 원문 문자열 배열과 몇 개의 문장을 추출할지(topk)와 정렬 방법(prob: 확률순, sent: 문장 등장 순)을 입력으로 받습니다. 

- 요약 결과를 summary로 인덱스를 반환하며, list[int]의 길이는 topk와 같습니다.

    - MatchSum일 경우 조합의 개수가 topk가 되므로 list[list[int]]로 반환되고 크기는 (topk, 3)이 됩니다(아래 예시 참고).

- summary의 각각의 원소에 해당하는 확률/점수를 prob에 반환합니다. 모델이 요약하는 데 걸린 시간을 time에 반환합니다.


ex) /api/TextRank

Input: 

```
{
    "text": [
        '"출발점이 다르다. 카카오뱅크는 금융 플랫폼으로서의 역량이 충분해 기존 국내 금융사들과 차이가 있다고 본다."',
        "윤호영 카카오뱅크 대표는 20일 오전 온라인으로 열린 IPO 기자간담회에서 최근 불거진 '고평가 논란'에 대해 이같이 답했다.", 
        '이날 윤호영 대표는 "인터넷은행이라는 출발점부터 다르다고 생각한다"며 "카카오뱅크는 존재하지 않았던 새로운 섹터를 담당하고 있기 때문에 국내(금융사)와 비교는 어렵다"고 말했다.',
        '앞서 카카오뱅크 공모가 밴드는 3만3000원부터 3만9000원 사이로, 공모가 고평가 논란이 불거진 바 있다.', (생략)],
    "topk": 4,
    "sort": "prob"
}
```

Output: 
```
{
    "summary": [7, 4, 2, 8]
    "prob": [0.7648976, 0.7492174, 0.74888676, 0.7327756]
    "time": 3.456713521763
}
```

ex) /api/MatchSum

Input: 
```
{
    "text": [
        '"출발점이 다르다. 카카오뱅크는 금융 플랫폼으로서의 역량이 충분해 기존 국내 금융사들과 차이가 있다고 본다."',
        "윤호영 카카오뱅크 대표는 20일 오전 온라인으로 열린 IPO 기자간담회에서 최근 불거진 '고평가 논란'에 대해 이같이 답했다.", 
        '이날 윤호영 대표는 "인터넷은행이라는 출발점부터 다르다고 생각한다"며 "카카오뱅크는 존재하지 않았던 새로운 섹터를 담당하고 있기 때문에 국내(금융사)와 비교는 어렵다"고 말했다.',
        '앞서 카카오뱅크 공모가 밴드는 3만3000원부터 3만9000원 사이로, 공모가 고평가 논란이 불거진 바 있다.', (생략)],
    "topk": 2,
    "sort": "sent"  // MatchSum은 정렬 무시
}
```

Output: 
```
{
    "summary": [[0, 3, 7], [0, 2, 7]]   // [0, 7, 3]이 아니라 [0, 3, 7]로 정렬
    "prob": [0.7648976, 0.7492174]   // 큰 순서부터 정렬
    "time": 3.456713521763
}
```

# Abstractive 모델 관련 설명

## /api/kobart, /api/kobart_rdrop, /api/kobart_rdrop_aihubnews, /api/kobart_rdrop_magazine, /api/kobart_rdrop_book, /api/KobertSumExtAbs, /api/pegasus_lage, /api/pegasus_large_skku, /api/pegasus_base_skku

### Input
|키|타입|설명|
|---|---|---|
|text|문자열 배열|문장별로 나눈 원문|

### Output
|키|타입|설명|
|---|---|---|
|summary|문자열|생성 요약문|
|score|숫자|summary에 대응되는 확률/점수|
|time|숫자|요약하는 데 걸린 시간|

- 각각의 모델에 대해 원문 문자열 배열을 입력으로 받습니다.
- 생성요약문을 summary에 담아 score과 time과 함께 반환합니다. KoBERTSumExtAbs 모델의 경우 score은 NaN이라는 문자열을 반환합니다.