import os
import sys

from flask import Flask, Response, request
import json
import time
from random import *

# /home/skkuedu/VANSum/backend/abs/KoBertSumAbs
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

sys.path.append(os.path.join(PROJECT_DIR, "src"))
sys.path.append(os.path.join(PROJECT_DIR, "src", "models"))
sys.path.append(os.path.join(PROJECT_DIR, "src", "prepro"))

import argparse
from src.prepro.data_builder import BertData
from src.models.data_loader import Dataloader
from src.make_data import preprocessing
from src.train import test_preload

LOG_DIR = f'{PROJECT_DIR}/ext/logs'
RESULT_DIR = f'{PROJECT_DIR}/ext/results'
MODEL_DIR = f'{PROJECT_DIR}/ext/models' 
app = Flask(__name__)

def preload():
	args = {"model": "klue", "dataset": 'test', "with_title": False, "log_file": f'{LOG_DIR}/preprocessing.log', 'lower': True, 'map_path': '../../data/', 'max_src_nsents': 120, 'max_src_ntokens_per_sent': 300, 'max_tgt_ntokens': 500, 'min_src_nsents': 1, 'min_src_ntokens_per_sent': 1, 'min_tgt_ntokens': 1, 'mode': 'format_to_bert', 'n_cpus': 2, 'pretrained_model': 'bert', 'raw_path': f'{PROJECT_DIR}/ext/data/json_data/test', 'save_path': f'{PROJECT_DIR}/ext/data/bert_data/test', 'select_mode': 'greedy', 'shard_size': 2000, 'use_bert_basic_tokenizer': False}
	args = argparse.Namespace(**args)
	bertData= BertData(args)
	model_path = "1117_1111/model_step_22000.pt"
	predictor, train_args = test_preload(model_path)
	return bertData, predictor, train_args

def dataPrepro(data, bert_obj):
	source = [preprocessing(original_sent).lower().split() for original_sent in data]
	tgt = []
	sent_labels = [0,1,2][:len(source)]
	b_data = bert_obj.preprocess(source, tgt, sent_labels, is_test=True)

	src_subtoken_idxs, sent_labels, tgt_subtoken_idxs, segments_ids, cls_ids, src_txt, tgt_txt = b_data
	bert = {"src": src_subtoken_idxs, "tgt": tgt_subtoken_idxs,
			"src_sent_labels": sent_labels, "segs": segments_ids, 'clss': cls_ids,
			'src_txt': src_txt, "tgt_txt": tgt_txt} 
	return bert

def bertSum(models, data):
	bert_obj, predictor, train_args = models
	bert = dataPrepro(data, bert_obj)
	print(bert)

	def loader_for_api(bert):
		yield [bert]
	
	test_iter = Dataloader(train_args, loader_for_api(bert), train_args.test_batch_size, "cpu",
							shuffle=False, is_test=True)
	pred_list, _, _ = predictor.translate_onebatch(test_iter.__iter__().__next__())

	return pred_list[0]

@app.route('/api/extabs', methods = ['POST','OPTIONS'])
def extabs():
	response=Response()
	
	if request.method == 'OPTIONS':
		response.headers.add("Access-Control-Allow-Origin", "*")
		response.headers.add('Access-Control-Allow-Headers', "*")
		response.headers.add('Access-Control-Allow-Methods', "POST")
	elif request.method == 'POST':
		response.headers.add("Access-Control-Allow-Origin", "*")
		data= request.get_json()
		text = data['text']
		start_time = time.time()
		
		pred = bertSum(models, text, block_trigram=True)
		end_time= time.time()
		data = {"summary" : pred, "time": end_time-start_time, "score": "NaN"}
		
		response.set_data(json.dumps(data, ensure_ascii=False))

	return response

if __name__=="__main__":
	models = preload()
	# ans = bertSum(models, ['포스코가 지난 10일 이사회를 열고 지주사 전환 안건을 의결했습니다.', 
	# 	'민영화 21년 만에 지주사 출범을 공식화한 것이죠.', '현재 43조원 수준인 기업가치를 2030년까지 3배 이상 확대하겠다는 청사진도 제시했습니다.', '▷ 관련기사:포스코홀딩스 첫발 뗐다(12월10일)\n\n포스코는 물적분할을 통해 지주사를 개편할 예정인데요.', '포스코에서 철강사업을 떼어내 비상장 회사를 만들고, 포스코는 투자사업을 하는 지주사(포스코홀딩스)로 남게 되는 거죠.', '코스피(유가증권시장)에 상장된 포스코홀딩스가 비상장사인 포스코를 100% 갖는다는 얘기입니다.', '하지만 소액 주주들은 물적분할 방식에 반대하고 있죠.', '물적분할이 철강사업을 상장하기 위한 준비 단계 아니냐는 게 개인주주들의 주장입니다.', "반면 포스코는 '철강 사업의 기업공개(IPO)는 없다'며 주주들을 설득하고 있습니다.", '최정우 포스코 회장은 지난 13일 박태준 명예회장 10주기 추도식에서 "물적분할 후 자회사 상장은 절대 하지 않을 것"이라는 뜻을 밝히기도 했고요.', '정말일까요?', '포스코의 물적분할 과정부터 살펴보도록하겠습니다.', '물적분할한 두가지 이유\n\n/그래픽=김용민 기자 kym5380@\n\n/그래픽=김용민 기자 kym5380@\n포스코가 물적분할을 선택한 이유부터 알아보겠습니다.', '내년부터 공정거래법상 지주회사의 자회사 지분 요건이 강화되는데요.', '지주사의 자회사 지분 의무보유율이 기존 20%에서 30%로 상향됩니다.', '인적분할을 통해 지주사 개편을 할 경우, 자사주 13.3%를 보유한 포스코홀딩스(지주사)는 철강사업 부문인 포스코(자회사)의 지분 17%가량을 시장에서 매입해야 합니다.', '업계에선 이를 위해 필요한 자금만 수조원으로 추정 중이죠.', '하지만 물적분할은 이런 걱정을 할 필요가 없습니다.', '포스코홀딩스가 포스코 지분 100%를 보유해서죠.', '공정거래법 기준을 만족하는 동시에 돈 한 푼 들이지 않고 지주사 전환을 추진할 수 있단 얘기입니다.', '한 가지 이유가 더 있습니다.', '포스코는 삼성, SK, LG 등 일반적인 대기업과 조금 다른 점이 있는데요.', '바로 오너가(家) 체제로 운영되는 기업이 아니라는 점입니다.', '포스코는 소유와 경영이 분리돼있는 전문경영인 체제로 기업이 운영됩니다.', '오너가 체제 중심의 대기업은 종종 인적분할을 통해 지주사 전환을 추진하죠.', '지주사 개편 과정에서 오너가의 지주사 지분율을 최대한 끌어올릴 수 있어서죠.', '이 과정에서 가장 적합한 방법이 인적분할입니다.', '인적분할 이후, 지주사가 유상증자를 실시하면 오너가는 인적분할 과정에서 받은 자회사 주식을 지주사 주식과 맞바꾸는 현물출자 방식으로 지주사 지분을 늘리죠.', '전문경영인 체제인 포스코 입장에선 인적분할 방식을 굳이 택할 이유가 없었겠죠.', '업계 관계자는 "자금을 마련할 필요도 없고 오너의 지주사 권한을 강화할 동기도 없었던 포스고 입장에선 물적분할 방식이 최적의 선택으로 보인다"고 말했습니다.', '안전장치 마련했지만…\n\n/사진=포스코 제공\n\n/사진=포스코 제공\n개인주주들이 물적분할에 반대하는 이유는 무엇일까요.', '사실 이들이 물적분할 자체에 반대하는 건 아닙니다.', "정확히 주주들이 반대하는 이유는 '물적분할 이후 설립되는 철강 사업부문을 상장하지 않을까' 하는 우려 때문입니다.", '소액 주주 입장에선 대기업들이 물적분할 이후 상장을 추진하는 모습을 여러 차례 목격했습니다.', '최근 IPO에 성공한 현대중공업, 상장을 앞두고 있는 LG에너지솔루션이 대표적 사례입니다.', '물적분할 이후, 자회사가 상장하게 되면 기존 주주들은 자회사 주식을 1주도 갖지 못합니다.', '중복상장으로 인해 지주회사 주가가 하락할 가능성도 높고요.', '실제로 지주사 격인 한국조선해양과 모회사인 LG화학의 주가는 자회사의 IPO발표 이후 하락했습니다.', '포스코는 2050년까지 수소환원제철 기술에 40조원을 투입할 계획인데요.', '단순 계산을 해봐도 수소환원제철 기술 확보를 위해 매년 1조원이 넘게 투입돼야합니다.', '주주들은 비상장사를 유지한 채 매년 1조원이 넘는 대규모 투자를 할 수 있을지 의문을 표하고 있죠.', '포스코 측은 지주사의 유상증자를 통해 철강 사업에 필요한 투자 자금을 확보한단 입장입니다.', '물론 포스코의 계획이 말이 안되는건 아닙니다.', '물적분할이 완료되면 지주사인 포스코홀딩스의 부채비율은 8%에 불과한데요.', '이는 굉장히 낮은 수준입니다.', '신용등급(AA+)이 높은 만큼 회사채를 통해 자금을 확보할 수도 있죠.', '하지만 장기적 관점에서 보면 증자, 회사채 발행만으로 수소환원제철에 필요한 막대한 자금을 마련할 수 있을까요.', '소액주주들은 이 질문에 회의적인 것이죠.', '포스코는 물적분할 후 철강 사업 부문 100% 자회사를 상장하지 않겠다고 강조하고 있죠.', '일종의 안전장치도 마련했습니다.', '포스코는 물적분할 발표 당시 "비상장 유지를 명확하게 하기 위해 신설 철강회사의 정관에 \'제3자배정, 일반 공모\' 등 상장에 필요한 규정을 반영하지 않을 예정"이라고 밝혔는데요.', "실제로 포스코의 분할계획서 총칙 제8조 신주인수권 조항을 보면 '본 회사가 신주를 발행할 경우 주주에게 그 소유주식수에 비례하여 신주를 배정한다(제8조 1항)'와 '주주가 신주인수권을 행사하지 아니하여 생긴 실권주 및 신주 배정 시에 생긴 단주는 관계법령에 따라 이사회의 결의로 처리한다(제8조 2항)'는 내용만 명시돼 있습니다.", '제3자배정, 일반 공모 등 상장에 필요한 규정이 포함돼있지 않는 것이죠.', '내년 1월 상장을 앞둔 LG에너지솔루션의 사례와 비교해보면 그 차이를 명확히 볼 수 있는데요.', "LG에너지솔루션의 분할계획서엔 '일반공모증자 방식으로 신주를 발행하는 경우(제10조 1항 5호)', '주권을 한국거래소에 상장하기 위하여 신주를 모집하거나 인수인에게 인수하게 하는 경우(제10조 1항 9호)' 등의 조항이 포함돼있습니다.", '이 안전장치가 철강 사업부문의 상장을 막을 정도로 강력한 장치일까요?', '결론부터 말하면 그렇지는 않아 보입니다.', '정관을 바꾸는게 그리 어렵지 않기 때문이죠.', '앞으로 포스코 지분을 100% 보유하게 되는 포스코홀딩스가 마음만 먹으면 언제든지 이 규정을 바꿀 수 있단 얘기입니다.', '여기에 향후 포스코의 회장이 바뀌면 상황이 또 어떻게 변할지 모릅니다.', '포스코의 물적분할안이 통과할지는 내년 1월 28일에 열리는 임시주주총회에서 판가름날 전망입니다.', '분할 안이 임시 주총을 통과하기 위해서는 출석한 주주의 3분의2이상과 발행주식 총수의 3분의1이상의 동의가 필요합니다.', '결과는 끝까지 가봐야 할 듯합니다.', '포스코 대주주인 국민연금(9.75%)이 찬성표를 던질진 미지수이기 때문입니다.', '국민연금은 그동안 주주가치 훼손 우려로 기업들의 물적분할에 대해 부정적인 입장을 보여왔습니다.', 'LG화학, SK이노베이션 등 물적분할 안건에 대해서도 반대표를 던진 이력도 있습니다.', "포스코가 지주사 전환을 위한 첫발을 잘 떼기 위해선 국민연금과 개인 주주들의 마음을 돌릴 만한 더 '안전한 장치'가 필요해 보입니다."], block_trigram=True)
	# print(ans)
	app.run("112.175.32.78", port=9550)