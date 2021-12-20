import os
import argparse
import time

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

DATA_DIR = f'{PROJECT_DIR}/ext/data'
RAW_DATA_DIR = DATA_DIR + '/raw'
JSON_DATA_DIR = DATA_DIR + '/json_data'
BERT_DATA_DIR = DATA_DIR + '/bert_data' 
LOG_DIR = f'{PROJECT_DIR}/ext/logs'
LOG_PREPO_FILE = LOG_DIR + '/preprocessing.log' 

MODEL_DIR = f'{PROJECT_DIR}/ext/models' 
RESULT_DIR = f'{PROJECT_DIR}/ext/results' 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-task", default='test', type=str, choices=['install', 'make_train_data', 'make_test_data', 'train', 'valid', 'test', 'train_abs', 'valid_abs', 'test_abs'])
    parser.add_argument("-n_cpus", default='2', type=str)
    parser.add_argument("-visible_gpus", default='0', type=str)
    
    parser.add_argument("-train_from", default=None, type=str)
    parser.add_argument("-model_path", default=None, type=str)
    parser.add_argument("-test_from", default=None, type=str)
    parser.add_argument("-test_for", default="dacon", type=str, choices=["dacon", "matchsum", "rouge_test"])
    parser.add_argument("-test_save_to", default="", type=str)
    parser.add_argument("-now", default="1117_1111", type=str)
    args = parser.parse_args()

    # now = time.strftime('%m%d_%H%M')
    now = args.now
    
    model_type="klue"

    # python main.py -task install
    if args.task == 'install':
        os.chdir(PROJECT_DIR)
        os.system("pip install -r requirements.txt")
        os.system("pip install Cython")
        os.system("python src/others/install_mecab.py")
        os.system("pip install -r requirements_prepro.txt")

    # python main.py -n_cpus 10 -model klue -make_for train
    elif args.task == 'make_train_data':
        os.chdir(PROJECT_DIR + '/src')
        os.system(f"python make_data.py -n_cpus {args.n_cpus} -model {model_type} -make_for train")

    # python main.py -n_cpus 10 -model klue -make_for test
    elif args.task == 'make_test_data':
        os.chdir(PROJECT_DIR + '/src')
        os.system(f"python make_data.py -n_cpus {args.n_cpus} -model {model_type} -make_for test")

    # python main.py -task train -visible_gpus 0
    # python main.py -task train -visible_gpus 0 -train_from 1209_1236/model_step_7000.pt 
    elif args.task == 'train':
        """
        파라미터별 설명은 trainer_ext 참고
        """
        os.chdir(PROJECT_DIR + '/src')

        # python train.py -task ext -mode train -bert_data_path BERT_DATA_PATH -ext_dropout 0.1 -model_path MODEL_PATH -lr 2e-3 -visible_gpus 0,1,2 -report_every 50 -save_checkpoint_steps 1000 -batch_size 3000 -train_steps 50000 -accum_count 2 -log_file ../logs/ext_bert_cnndm -use_interval true -warmup_steps 10000 -max_pos 512
        # python train.py  -task abs -mode train -train_from /kaggle/input/absbert-weights/model_step_149000.pt -bert_data_path /kaggle/working/bert_data/news  -dec_dropout 0.2  -model_path /kaggle/working/bertsumextabs -sep_optim true -lr_bert 0.002 -lr_dec 0.02 -save_checkpoint_steps 1000 -batch_size 140 -train_steps 150000 -report_every 100 -accum_count 5 -use_bert_emb true -use_interval true -warmup_steps_bert 1000 -warmup_steps_dec 500 -max_pos 512 -visible_gpus 0  -temp_dir /kaggle/working/temp -log_file /kaggle/working/logs/abs_bert_cnndm
        do_str = f"python train.py -task ext -mode train -model {model_type}"  \
            + f" -bert_data_path {BERT_DATA_DIR}/train"  \
            + f" -save_checkpoint_steps 1000 -visible_gpus {args.visible_gpus} -report_every 50"

        param1 = " -ext_dropout 0.1 -lr 2e-3 -batch_size 500 -train_steps 5000 -accum_count 2 -use_interval true -warmup_steps 3000 -max_pos 512"
        param2 = " -ext_dropout 0.1 -lr 2e-3 -batch_size 1000 -train_steps 5000 -accum_count 2 -use_interval true -warmup_steps 3000 -max_pos 512"
        param3 = " -ext_dropout 0.1 -max_pos 512 -lr 2e-3 -warmup_steps 10000 -batch_size 3000 -accum_count 2 -train_steps 50000  -use_interval true"
        # param3 = " -ext_dropout 0.2 -max_pos 512 -lr 2e-3 -warmup_steps 10000 -batch_size 3000 -accum_count 2 -train_steps 50000  -use_interval true"
        # temporary for test
        # param3 = " -ext_dropout 0.1 -max_pos 512 -lr 2e-3 -warmup_steps 100 -batch_size 1 -accum_count 2 -train_steps 500  -use_interval true"  

        do_str += param3

        if args.train_from is None:
            os.system(f'mkdir {MODEL_DIR}/{now}')
            do_str += f" -model_path {MODEL_DIR}/{now}"  \
                + f" -log_file {LOG_DIR}/train_{now}.log"
        else:
            model_folder, model_name = args.train_from.rsplit('/', 1)
            do_str += f" -train_from {MODEL_DIR}/{args.train_from}"  \
                + f" -model_path {MODEL_DIR}/{model_folder}"  \
                + f" -log_file {LOG_DIR}/train_{model_folder}.log"

        print(do_str)
        os.system(do_str)

    elif args.task == "train_abs":
        os.chdir(PROJECT_DIR + '/src')
        os.system(f'mkdir {MODEL_DIR}/{now}')
        """
        python train.py  -task abs -mode train -bert_data_path BERT_DATA_PATH -dec_dropout 0.2 -model_path MODEL_PATH 
        -sep_optim true -lr_bert 0.002 -lr_dec 0.2 -save_checkpoint_steps 2000 -batch_size 140 -train_steps 200000 -report_every 50 
        -accum_count 5 -use_bert_emb true -use_interval true -warmup_steps_bert 20000 -warmup_steps_dec 10000 -max_pos 512 
        -visible_gpus 0,1,2,3 -log_file ../logs/abs_bert_cnndm  -load_from_extractive EXT_CKPT   
        """
        
        do_str = f"python train.py  -task abs -mode train -model {model_type} -bert_data_path {BERT_DATA_DIR}/train -dec_dropout 0.2" \
        + f" -model_path {MODEL_DIR}/{now} -sep_optim true -lr_bert 0.002 -lr_dec 0.2 -save_checkpoint_steps 2000" \
        + f" -batch_size 140 -train_steps 200000 -report_every 50 -accum_count 5 -use_bert_emb true -use_interval true -warmup_steps_bert 20000" \
        + f" -warmup_steps_dec 10000 -max_pos 512 -visible_gpus {args.visible_gpus} -log_file {LOG_DIR}/train_{now}.log" \
        + f" -load_from_extractive /home/vaiv2021/yong/KoBertSum/ext/models/1106_2222/model_step_19000.pt"
        # + f" -train_from /home/vaiv2021/mook/KoBertSum/ext/models/1109_1111/model_step_16000.pt"
        print(do_str)
        os.system(do_str)

    elif args.task == "valid_abs":
        os.chdir(PROJECT_DIR + '/src')
        """
        python train.py -task abs -mode validate -batch_size 3000 -test_batch_size 500 
        -bert_data_path BERT_DATA_PATH -log_file ../logs/val_abs_bert_cnndm -model_path MODEL_PATH -result_path ../logs/abs_bert_cnndm 
        -sep_optim true -use_interval true -visible_gpus 0,1
        -max_pos 512 -max_length 200 -alpha 0.95 -min_length 50 
        -max_pos 512 -min_length 20 -max_length 100 -alpha 0.9 
        """

        
        os.system(f"python train.py -task abs -mode validate -model {model_type} -test_all True"
            + f" -model_path {MODEL_DIR}/{args.model_path}"
            + f" -bert_data_path {BERT_DATA_DIR}/valid"
            + f" -result_path {RESULT_DIR}/result_{args.model_path}"
            + f" -log_file {LOG_DIR}/valid_{args.model_path}.log"
            + f" -test_batch_size 500  -batch_size 3000"
            + f" -sep_optim true -use_interval true -visible_gpus {args.visible_gpus}"
            + f" -max_pos 512 -max_length 200 -alpha 0.95 -min_length 50"
            + f" -report_rouge True"
            + f" -max_tgt_len 100"
        )

    elif args.task == 'test_abs':
        os.chdir(PROJECT_DIR + '/src')
        model_folder, model_name = args.test_from.rsplit('/', 1)
        model_name = model_name.split('_', 1)[1].split('.')[0]
        now = time.strftime('%y%m%d_%H%M')

        """
        python train.py -task abs -mode validate -batch_size 3000 -test_batch_size 500 
        -bert_data_path BERT_DATA_PATH -log_file ../logs/val_abs_bert_cnndm -model_path MODEL_PATH -sep_optim true 
        -use_interval true -visible_gpus 1 -max_pos 512 -max_length 200 -alpha 0.95 -min_length 50 -result_path ../logs/abs_bert_cnndm 
        """
        os.system(f"""\
            python train.py -task abs -mode test -model {model_type} \
            -test_from {MODEL_DIR}/{args.test_from} \
            -bert_data_path {BERT_DATA_DIR}/test \
            -result_path {RESULT_DIR}/result_{model_folder} \
            -log_file {LOG_DIR}/test_{model_folder}.log \
            -test_batch_size 1  -batch_size 3000 \
            -sep_optim true -use_interval true -visible_gpus {args.visible_gpus} \
            -max_pos 512 -max_length 150 -alpha 0.95 -min_length 15 \
            -sep_optim true -block_trigram true
        """)

    # python main.py -task valid -model_path 1209_1236
    elif args.task == 'valid':
        os.chdir(PROJECT_DIR + '/src')
        """
        python train.py -task abs -mode validate -batch_size 3000 -test_batch_size 500 
        -bert_data_path BERT_DATA_PATH -log_file ../logs/val_abs_bert_cnndm -model_path MODEL_PATH -result_path ../logs/abs_bert_cnndm 
        -sep_optim true -use_interval true -visible_gpus 0,1
        -max_pos 512 -max_length 200 -alpha 0.95 -min_length 50 
        -max_pos 512 -min_length 20 -max_length 100 -alpha 0.9 
        """
        os.system(f"python train.py -task ext -mode validate -model {model_type} -test_all True"
            + f" -model_path {MODEL_DIR}/{args.model_path}"
            + f" -bert_data_path {BERT_DATA_DIR}/valid"
            + f" -result_path {RESULT_DIR}/result_{args.model_path}"
            + f" -log_file {LOG_DIR}/valid_{args.model_path}.log"
            + f" -test_batch_size 500  -batch_size 3000"
            + f" -sep_optim true -use_interval true -visible_gpus {args.visible_gpus}"
            + f" -max_pos 512 -max_length 200 -alpha 0.95 -min_length 50"
            + f" -report_rouge False"
            + f" -max_tgt_len 100"
        )

    # python main.py -task test -test_from 1209_1236/model_step_7000.pt -visible_gpus 0 -test_for {matchsum/dacon/rouge_test}

    elif args.task == 'test':
        os.chdir(PROJECT_DIR + '/src')
        model_folder, model_name = args.test_from.rsplit('/', 1)
        model_name = model_name.split('_', 1)[1].split('.')[0]
        now = time.strftime('%y%m%d_%H%M')

        os.system(f"""\
            python train.py -mode test -model {model_type} \
            -test_from {MODEL_DIR}/{args.test_from} \
            -bert_data_path {BERT_DATA_DIR}/test \
            -result_path {RESULT_DIR}/result_{model_folder} \
            -log_file {LOG_DIR}/test_{model_folder}.log \
            -test_batch_size 1  -batch_size 3000 \
            -sep_optim true -use_interval true -visible_gpus {args.visible_gpus} \
            -max_pos 512 -max_length 200 -alpha 0.95 -min_length 50 \
            -max_tgt_len 100
        """)

        # -max_pos 512 -max_length 200 -alpha 0.95 -min_length 50 \
        # -report_rouge True  \
        #  -model_path {MODEL_DIR} 
        # args.max_tgt_len=140  이거 수정해도 효과가 거의 없음

        os.system(f"python make_submission.py \
            -test_from_candidate {RESULT_DIR}/result_{model_folder}_{model_name}.candidate \
            -test_from_jsonl {RAW_DATA_DIR}/extractive_test_v2.jsonl \
            -test_for {args.test_for}\
            -save_to {RESULT_DIR}/submission_{now}.csv")
