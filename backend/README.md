# Quick Start

backend폴더 내 `api_react.py`파일의 맨 마지막 줄에 있는 `app.run()` 내의 호스트와 포트번호를 맞는 것으로 바꿉니다. [여기](https://drive.google.com/file/d/1H20Ira-Nx-Pd6Gea7L7R5T9Pqzureiko/view?usp=sharing)에서 데이터를 다운받아 저장한 후, 다음 명령어를 입력하면 api가 켜집니다. 실행하기 전 [여기](https://konlpy.org/ko/v0.5.2/install/#ubuntu)를 참고해 Mecab을 깔아야 합니다.

```bash
pip install -r requirements.txt
Mecab 설치

python api_react.py
```

저장해야 하는 경로는 다음과 같습니다.
|파일이름|저장위치|
|---|---|
|KoBertSum/model/model_step_35000.pt|mKoBertSum/ext/models/0727_0000/|
|MatchSum/model/epoch-3_step-15000_ROUGE-0.449044.pt|MatchSum/MatchSum_forMatch/models/|
|SummaRuNNer/Mecab/embedding_mecab_ko.npz   SummaRuNNer/Mecab/word2id_mecab_ko.json|SummaRuNNer/data/|
|SummaRuNNer/model/RNN_RNN_seed_1_mecababs.pt|SummaRuNNer/checkpoints/|

# Extractive

## SummaRuNNer

[hpzhao/SummaRuNNer](https://github.com/hpzhao/SummaRuNNer)을 바탕으로 수정하였습니다.

1. 전처리
    - Vocab 구성

        word2id파일과 embedding파일이 있어야 합니다.
        
        - 영어용 word2id, embedding [다운로드](https://github.com/hpzhao/SummaRuNNer)(서머러너 원본 깃허브)
        - 한국어용 Kkma wordvector [다운로드](https://github.com/Kyubyong/wordvectors)
        - 한국어용 Mecab wordvector와 한국어용 word2id, embedding은 [여기](https://drive.google.com/file/d/1H20Ira-Nx-Pd6Gea7L7R5T9Pqzureiko/view?usp=sharing)에서 다운로드
        

        워드벡터를 다운받은 후 word2id와 embedding을 구축하는 명령어는 다음과 같습니다.

        ```bash
        python preprocess.py -build_vocab -embed data/ko.tsv -vocab data/embedding_ko.npz -word2id data/word2id_ko.json
        ```

    - 데이터

        [AIHub 데이터](https://aihub.or.kr/aidata/8054)를 사용합니다. 전처리하는 명령어는 다음과 같습니다.
        ```bash
        python preprocess.py -worker_num 10 -source_dir {AIHUB 데이터 경로} -target_dir {처리된 데이터 저장 경로}
        ```

        Mecab으로 전처리된 데이터는 여기에서 다운받을 수 있습니다.

2. 훈련

    다음 명령어로 훈련을 진행합니다.

    ```bash
    python main.py -device 0 -batch_size 32 -model RNN_RNN -seed 1 -save_dir checkpoints/ -train_dir {train셋 경로} -val_dir {val셋 경로} -embedding {embedding 경로} -word2id {word2id 경로}
    ```
    
    `-report_every`옵션을 통해 몇 번의 step마다 val셋을 계산하고 모델을 저장할 것인지를 지정할 수 있습니다.

    이후에 `checkpoints/RNN_RNN_seed_1.pt`로 모델이 저장됩니다. (models/BasicModule.py에서 save메소드 참조)

    훈련된 모델은 [여기](https://drive.google.com/file/d/1H20Ira-Nx-Pd6Gea7L7R5T9Pqzureiko/view?usp=sharing)에서 다운받을 수 있습니다.


3. 테스트

    다음 명령어로 테스트를 진행합니다.

    ```bash
    python main.py -test -batch_size 2 -test_dir {test셋 경로} -load_dir {모델 저장된 경로} -embedding {embedding 경로} -word2id {word2id 경로}
    ```

    `-topk`옵션을 통해 상위 몇 개의 문장을 저장할 것인지를 지정할 수 있습니다.


## KoBertSum

[uoneway/KoBertSum](https://github.com/uoneway/KoBertSum)을 바탕으로 수정하였습니다.

1. 전처리
    다음 명령으로 전처리합니다.
    /ext/data/raw train.jsonl에 학습을 위한 데이터를 넣어줍니다. 
    train.jsonl이 분리되어 일부는 학습에 일부는 validation에 사용됩니다. 
    ```bash
    python main.py -task make_data -n_cpus {사용할 cpu 수}
    ```

    전처리가 완료된 데이터는 /ext/data/bert_data에 저장됩니다. 

2. 훈련

    다음 명령으로 훈련합니다. 

    ```bash
    python main.py -task train -target_summary_sent abs
    ```

    훈련이 완료되면 모델이 /ext/models/{main.py에서의 now} 에 저장됩니다.

    훈련된 모델은 [여기](https://drive.google.com/file/d/1H20Ira-Nx-Pd6Gea7L7R5T9Pqzureiko/view?usp=sharing)에서 다운받을 수 있습니다.

3. Validation

    다음 명령으로 Validation합니다. 

    ```bash
    python main.py -task valid -model_path {main.py에서의 now}
    ```

    Validation을 통해 훈련한 모델의 loss를 측정합니다. 

4. 테스트

    /ext/data/raw/extractive_test_v2.jsonl에 요약할 기사를 넣고 다음 명령어로 테스트 합니다. 

    ```bash
    python kobertsum_summarizer.py
    ```

    요약문, 요약문에 해당하는 인덱스, 요약 모델 내에서의 점수를 차례대로 출력합니다. 


## MatchSum

[maszhongming/MatchSum](https://github.com/maszhongming/MatchSum)을 바탕으로 수정하였습니다.

1. 전처리

    다음 명령어로 전처리합니다.
    
    ```bash
    python get_candidate.py --tokenizer kobert --data_path {데이터 경로} --index_path {index 경로} --write_path {저장 경로}
    ```

    index 파일은 데이터와 같은 순서로 `{"sent_id": [0, 1, 2, 3, 4, 5]}`와 같은 형식으로 저장되어 있는 jsonl파일입니다.

2. 훈련

    다음 명령어로 훈련합니다.

    ```bash
    python train_matching.py --mode=train --encoder=kobert --save_path={모델 저장 경로} --gpus=0,1 --candidate_num 20 --batch_size 8
    ```

    훈련된 모델은 [여기](https://drive.google.com/file/d/1H20Ira-Nx-Pd6Gea7L7R5T9Pqzureiko/view?usp=sharing)에서 다운받을 수 있습니다.

3. 테스트

    다음 명령어로 테스트합니다.
    
    ```bash
    python train_matching.py --mode=test --encoder=kobert --save_path={모델경로} --gpus=1
    ```

    정답이 없는 test셋의 경우 `--csv_path {csv 경로}`를 추가해야 할 수 있습니다.(아래 참조)

    다음 각각의 경우에 대해 `train_matching.py`의 115번째 줄 test_metric을 바꿔야 합니다.

    - 정답이 있는 test셋의 경우: ROUGE 점수를 계산하여 출력합니다. `MatchRougeMetric`를 사용합니다.

    - 정답이 없는 test셋의 경우: ROUGE 점수를 계산할 수 없고, `csv_path` 인자를 받아 csv파일로 출력합니다. `MatchExportMetric`를 사용합니다. `csv_path`를 인자로 넘겨줘야 합니다.

    - 하나씩 요청받아 처리하는 경우: 각각의 경우에 대해 확률과 인덱스를 반환합니다. `MatchResultMetric`를 사용합니다.

# Abstractive

모델이 다양해지고 요구되는 환경이 달라져서 conda 가상환경을 새롭게 만들어 각각 flask를 킨 후 `api_react.py`에서 알맞은 곳으로 요청하는 방식을 활용하였습니다.

## KoBART

[seujung/KoBART-summarization](https://github.com/seujung/KoBART-summarization)을 바탕으로 수정하였습니다.

conda 가상환경을 새로 만들어 `abs/KoBART-summarization` 폴더에 들어가 `pip install -r requirements.txt` 명령어로 설치합니다.

이후 api를 실행하기 위해서는 `python kobart_api.py` 명령어를 사용합니다.

실행 방법 등의 내용은 원래 github의 내용과 동일하므로 참고하시기 바랍니다.

KoBART R-Drop을 구현하면서 달라진 내용은 `abs/KoBART-summarization` 안의 `README.md`를 참고하시기 바랍니다.

## KoBERTSumExtAbs

[uoneway/KoBertSum](https://github.com/uoneway/KoBertSum)과 [nlpyang/PreSumm](https://github.com/nlpyang/PreSumm)을 바탕으로 수정하였습니다.

실행 방법은 [nlpyang/PreSumm](https://github.com/nlpyang/PreSumm)을 참고하시기 바랍니다.

conda 가상환경을 새로 만들어 `abs/KoBertSumAbs` 폴더에 들어가 `pip install -r requirements.txt` 명령어로 설치합니다.

이후 api를 실행하기 위해서는 `python ExtAbs_Summarizer.py` 명령어를 사용합니다.

## KoGPT2

[seujung/KoGPT2-summarization](https://github.com/seujung/KoGPT2-summarization)을 바탕으로 수정하였습니다.

실행 방법 등의 내용은 원래 github README.md의 내용과 동일합니다.

## Pegasus

[google-research/pegasus](https://github.com/google-research/pegasus)를 바탕으로 수정하였습니다.

실행 방법 등의 내용은 원래 github README.md의 내용과 동일합니다.

conda 가상환경을 새로 만들어 `abs/PEGASUS` 폴더에 들어가 `pip install -r requirements.txt` 명령어로 설치합니다.

이후 api를 실행하기 위해서는 `python pegasus_api.py` 명령어를 사용합니다.

# API

자세한 설명은 `API_REACT.md`를 참고하시기 바랍니다.