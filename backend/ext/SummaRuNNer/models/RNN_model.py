import lightning.pytorch as pl
import torch
import torch.nn as nn
import torch.nn.functional as F

class RNN_pl_model(pl.LightningModule):

    def __init__(self, encoder, vocab):
        super().__init__()
        self.encoder = encoder
        self.criterion = nn.BCELoss()
        self.vocab = vocab

    def forward(self, batch):
        features, targets, _, doc_lens = self.vocab.make_features(batch)
        features, targets = Variable(features), Variable(targets.float())
        probs = self.encoder(features, doc_lens)
        return probs
        
    def training_step(self, batch):
        x, y = batch
        y_hat = self(batch)
        loss = self.criterion(x, y)
