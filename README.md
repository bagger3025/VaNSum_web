# VaNSum

## Working on...
1. test 추가
2. 백엔드 모델들 코드 전체 일원화
3. Kubernetes로 관리

관련 작업내용은 [노션](https://proud-daffodil-e24.notion.site/VaNSum_Web-035ce00d43a848f5ab2102f23b82fd06?pvs=4)에 정리합니다.

## 설치할 것들(linux ubuntu)
1. anaconda 설치 후 ```conda create -n "가상환경이름" python="파이썬 버전(3.7.10)"```로 가상환경 만들기
2. ```pip install -r requirements.txt```
3. ```conda install torchaudio==0.7.0 cpuonly -c pytorch```
4. mecab 설치 
```
> bash <(curl -s https://raw.githubusercontent.com/konlpy/konlpy/master/scripts/mecab.sh)
> cd /tmp/mecab-0.996-ko-0.9.2
> ./configure
> make
> make check
> sudo make install
```

## frontend 설치할 것들
1. ``` npm install react-route-dom```
2. ``` npm install autosize```

## frontend js 파일들 
1. inputField.js : input 받는 부분 (news url, news, AIHub data)
2. HighlightRadioButton.js : 하이라이트 라디오 버튼 부분
3. TextField.js : 기사 본문을 나타내는 부분
4. GoldSummaryField.js : gold summary, naver summary가 나타나는 부분
5. ModelTextField.js : 각각의 추출 요약 모델이 요약한 결과를 나타내는 부분

## 실행 방법
1. ```cd backend``` 후에 ```python react_api.py``` 터미널 창에 입력
2. ```cd ..```
3. ```cd frontend``` ```npm start```
