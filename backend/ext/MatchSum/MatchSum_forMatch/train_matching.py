import argparse
import os
import json
import torch
from os.path import join, exists
from torch.optim import Adam

from MatchSum.MatchSum_forMatch.utils import get_model, get_datas

from dataloader import MatchSumPipe
from model import MatchSum
from metrics import MarginRankingLoss, ValidMetric, MatchRougeMetric, MatchResultMetric, MatchExportMetric
from callback import MyCallback
from fastNLP.core.trainer import Trainer
from fastNLP.core.tester import Tester
from fastNLP.core.callback import SaveModelCallback

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

def configure_training(args):
    devices = [int(gpu) for gpu in args.gpus.split(',')]
    params = {}
    params['encoder']       = args.encoder
    params['candidate_num'] = args.candidate_num
    params['batch_size']    = args.batch_size
    params['accum_count']   = args.accum_count
    params['max_lr']        = args.max_lr
    params['margin']        = args.margin
    params['warmup_steps']  = args.warmup_steps
    params['n_epochs']      = args.n_epochs
    params['valid_steps']   = args.valid_steps
    return devices, params

def train_model(args):
    
    # check if the data_path exists
    datas = get_datas(args.mode, args.datatype, args.encoder)
    _, encoder, special_tokens = get_model(args.encoder)
    if not exists(args.save_path):
        os.makedirs(args.save_path)
    
    # load summarization datasets
    datasets = MatchSumPipe(special_tokens["sep_id"], special_tokens["pad_id"]).process_from_file(datas)
    print('Information of dataset is:')
    print(datasets)
    train_set = datasets.datasets['train']
    valid_set = datasets.datasets['val']
    
    # configure training
    devices, train_params = configure_training(args)
    with open(join(args.save_path, 'params.json'), 'w') as f:
        json.dump(train_params, f, indent=4)
    print('Devices is:')
    print(devices)
    assert args.batch_size % len(devices) == 0

    # configure model
    model = MatchSum(args.candidate_num, encoder, special_tokens["pad_id"])
    optimizer = Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=0)
    
    callbacks = [MyCallback(args), 
                SaveModelCallback(save_dir=args.save_path, top=5)]
    
    criterion = MarginRankingLoss(args.margin)
    val_metric = [ValidMetric(save_path=args.save_path, data=datas['val'])]
    
    trainer = Trainer(train_data=train_set, model=model, optimizer=optimizer,
                    loss=criterion, batch_size=args.batch_size,
                    update_every=args.accum_count, n_epochs=args.n_epochs, 
                    print_every=10, dev_data=valid_set, metrics=val_metric, 
                    metric_key='ROUGE', validate_every=args.valid_steps, 
                    save_path=args.save_path, device=devices, callbacks=callbacks)
    
    print('Start training with the following hyper-parameters:')
    print(train_params)
    trainer.train()


def test_model(args, myModel = None, myData = None, mySpecialTokens = None):

    if myModel is None:
        models = os.listdir(args.save_path)
    else:
        models = [myModel]
    
    # load dataset
    if myData is None:
        datas = get_datas(args.mode, args.datatype, args.encoder)
    else:
        datas = {"test": myData}
    
    if mySpecialTokens is None:
        _, _, special_tokens = get_model(args.encoder)
    else:
        special_tokens = mySpecialTokens
    
    datasets = MatchSumPipe(special_tokens["sep_id"], special_tokens["pad_id"]).process_from_file(datas)
    print('Information of dataset is:')
    print(datasets)
    test_set = datasets.datasets['test']
    
    # need 1 gpu for testing
    device = int(args.gpus)
    if device == -1:
        device = "cpu"
    args.batch_size = 1

    for cur_model in models:
        
        # print('Current model is {}'.format(cur_model))

        # load model
        if myModel is None:
            model = torch.load(join(args.save_path, cur_model))
        else:
            model = cur_model
    
        # configure testing
        test_metric = MatchResultMetric(data=datas['test'])
        tester = Tester(data=test_set, model=model, metrics=[test_metric], 
                        batch_size=args.batch_size, device=device, use_tqdm=False)
        summary = tester.test()
    
    return summary['MatchResultMetric']

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='training/testing of MatchSum'
    )
    parser.add_argument('--mode', required=True,
                        help='training or testing of MatchSum', type=str)

    parser.add_argument('--save_path', required=True,
                        help='root of the model', type=str)
    # example for gpus input: '0,1,2,3'
    parser.add_argument('--gpus', required=True,
                        help='available gpus for training(separated by commas)', type=str)
    parser.add_argument('--encoder', required=True,
                        help='the encoder for matchsum', type=str)
    parser.add_argument('--datatype', required=True,
                        help='type of data', type=str)

    parser.add_argument('--batch_size', default=16,
                        help='the training batch size', type=int)
    parser.add_argument('--accum_count', default=2,
                        help='number of updates steps to accumulate before performing a backward/update pass', type=int)
    parser.add_argument('--candidate_num', default=20,
                        help='number of candidates summaries', type=int)
    parser.add_argument('--max_lr', default=2e-5,
                        help='max learning rate for warm up', type=float)
    parser.add_argument('--margin', default=0.01,
                        help='parameter for MarginRankingLoss', type=float)
    parser.add_argument('--warmup_steps', default=10000,
                        help='warm up steps for training', type=int)
    parser.add_argument('--n_epochs', default=5,
                        help='total number of training epochs', type=int)
    parser.add_argument('--valid_steps', default=1000,
                        help='number of update steps for validation and saving checkpoint', type=int)
    parser.add_argument('--csv_path', default="result/result.csv",
                        help='path to csv file', type=str)

    args = parser.parse_known_args()[0]
    
    if args.mode == 'train':
        print('Training process of MatchSum !!!')
        train_model(args)
    else:
        print('Testing process of MatchSum !!!')
        test_model(args)

