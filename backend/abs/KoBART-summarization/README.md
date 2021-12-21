# KoBART-summarization

## Install KoBART
```
pip install git+https://github.com/SKT-AI/KoBART#egg=kobart
```

## Download binary
```
pip install gdown
python download_binary.py

kobart_summary
├── config.json
├── pytorch_model.bin
```
## Requirements
```
pytorch==1.9.0
transformers==4.8.2
pytorch-lightning==1.3.8
streamlit==0.72.0
```
## Data
- [Dacon 한국어 문서 생성요약 AI 경진대회](https://dacon.io/competitions/official/235673/overview/) 의 학습 데이터를 활용함
- 학습 데이터에서 임의로 Train / Test 데이터를 생성함
- 데이터 탐색에 용이하게 tsv 형태로 데이터를 변환함
- Data 구조
    - Train Data : 34,242
    - Test Data : 8,501
- default로 data/train.tsv, data/test.tsv 형태로 저장함
  
| news  | summary |
|-------|--------:|
| 뉴스원문| 요약문 |

### 다른 데이터를 tsv 형태로 데이터를 변환할 때의 주의사항
  - tsv 파일을 저장하는 데에는 pandas 라이브러리 사용
  - 데이터에 빈 문자열이 있는 경우 NaN 값이 입력되어 오류를 발생함. 이 때에는 `df.isna().sum()`과 같은 명령어로 NaN 값이 있는지를 확인해야 함
  - 만약 NaN 값이 있다면 `df = df.loc[df.loc[:,"summary"].isna()==False]`와 같은 식으로 NaN 값을 없앤 후 다시 저장해야 함



## How to Train
- KoBART summarization fine-tuning
- default_root_dir이 모델이 저장되는 폴더명
```
bash install_kobart.sh
pip install -r requirements.txt

[use gpu]
python train.py  --gradient_clip_val 1.0 --max_epochs 50 --default_root_dir logs  --gpus 1 --batch_size 4 --num_workers 4 --dropout 0.2 --kl_alpha 0.1 --train_file data/train.tsv --test_file data/test.tsv

[use cpu]
python train.py  --gradient_clip_val 1.0 --max_epochs 50 --default_root_dir logs  --batch_size 4 --num_workers 4
```


## Model Performance (original github)
- Test Data 기준으로 rouge score를 산출함
- Score 산출 방법은 Dacon 한국어 문서 생성요약 AI 경진대회 metric을 활용함
  
| | rouge-1 |rouge-2|rouge-l|
|-------|--------:|--------:|--------:|
| Precision| 0.515 | 0.351|0.415|
| Recall| 0.538| 0.359|0.440|
| F1| 0.505| 0.340|0.415|

## Model Performance (SKKU)
- Test set은 AIHub 뉴스데이터의 1.1버전 validation set을 사용
  - 10000개의 데이터셋으로 되어 있음
- Score 산출은 DACON 한국어 문서 생성요약 AI 경진대회의 코드를 활용

1. `KoBARTConditionalGeneration`을 활용하여 KoBART를 사용했을 때
  
  ||f1 score|
  |---|---|
  |rouge-1|0.513|
  |rouge-2|0.344|
  |rouge-l|0.420|

2. `KoBARTRDropGeneration`을 활용하여 KoBART R-Drop을 사용했을 때, `--dropout 0.1 --kl_alpha 0.1`을 활용하여 훈련했을 때

  ||f1 score|
  |---|---|
  |rouge-1|0.521|
  |rouge-2|0.355|
  |rouge-l|0.429|

3. KoBART R-Drop, `--dropout 0.2 --kl_alpha 0.1`을 활용하여 훈련했을 때

  ||rouge-1|rouge-2|rouge-l|
  |---|---|---|---|
  |뉴스(DACON) 데이터|0.522|0.356|0.430|
  |뉴스(AIHub) 데이터|-|-|-|
  |사설잡지 데이터|0.441|0.246|0.349|
  |도서 데이터|0.476|0.264|0.368|
  |뉴스 + 도서 데이터|0.502|0.315|0.397|

  단, 사설잡지 데이터와 도서 데이터, 뉴스+도서 데이터로 훈련한 모델은 test set을 각각 따로 마련하여 rouge 스코어를 측정했습니다.

## Demo
- 학습한 model binary 추출 작업이 필요함
   - pytorch-lightning binary --> huggingface binary로 추출 작업 필요
   - hparams의 경우에는 <b>./logs/tb_logs/default/version_0/hparams.yaml</b> 파일을 활용
   - model_binary 의 경우에는 <b>./logs/kobart_summary-model_chp</b> 안에 있는 .ckpt 파일을 활용
   - 변환 코드를 실행하면 <b>./kobart_summary</b> 에 model binary 가 추출 됨
  
```
 python get_model_binary.py --hparams hparam_path --model_binary model_binary_path
```

- streamlit을 활용하여 Demo 실행
    - 실행 시 <b>http://localhost:8501/</b> 로 Demo page가 실행됨
```
streamlit run infer.py
```

## Reference
- [KoBART](https://github.com/SKT-AI/KoBART)
- [KoBART-chatbot](https://github.com/haven-jeon/KoBART-chatbot)
