import json
import os
import torch

from SummaRuNNer import models
from SummaRuNNer.main import predict
from SummaRuNNer.utils.Vocab import Vocab
import numpy as np

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))

DEVICE = None
use_gpu = DEVICE is not None

class SummaRuNNer_Summarizer():

    def __init__(self):
        EMBEDDING = PROJECT_DIR + "/data/embedding_mecab_ko.npz"
        LOAD_DIR = PROJECT_DIR + "/checkpoints/RNN_RNN_seed_1_mecababs.pt"
        WORD2ID = PROJECT_DIR + "/data/word2id_mecab_ko.json"

        embed = torch.Tensor(np.load(EMBEDDING)['embedding'])
        if use_gpu:
            torch.cuda.set_device(DEVICE)
        
        with open(WORD2ID) as f:
            word2id = json.load(f)
        
        checkpoint = torch.load(LOAD_DIR, map_location=lambda storage, loc: storage)

        # checkpoint['args']['device'] saves the device used as train time
        # if at test time, we are using a CPU, we must override device to None
        if not use_gpu:
            checkpoint['args'].device = None
        else:
            checkpoint['args'].device = 0
        self.net = getattr(models,checkpoint['args'].model)(checkpoint['args'])
        self.net.load_state_dict(checkpoint['model'])
        if use_gpu:
            self.net.cuda()
        self.net.eval()
        self.vocab = Vocab(embed, word2id)
        self.preloaded = self.vocab, self.net

    def summarize(self, article, n_sents=3):
        article = ["\n".join(article)]
        result = predict(article, self.preloaded)
        return result[0]['index'][:n_sents], result[0]['probs'][:n_sents]