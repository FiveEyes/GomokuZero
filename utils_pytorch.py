import torch
from torch import nn, optim, autograd
from torch.autograd import Variable

import numpy as np

class Model(object):
    def __init__(self, model, optimizer):
        self.set_model(model)
        self.set_optimizer(optimizer)
        
    def set_model(self, model):
        self.model = model
        if torch.cuda.is_available():
            self.model.cuda()
    def set_optimizer(self, optimizer):
        self.optimizer = optimizer
        
    def get_slice(self, xs, i, j):
        if type(xs) is list:
            if torch.cuda.is_available():
                slice = [ Variable(torch.from_numpy(x[i:j].astype('float32')), requires_grad=False).cuda() for x in xs ]
            else:
                slice = [ Variable(torch.from_numpy(x[i:j].astype('float32')), requires_grad=False) for x in xs ]
        else:
            if torch.cuda.is_available():
                slice = [Variable(torch.from_numpy(xs[i:j].astype('float32')), requires_grad=False).cuda()]
            else:
                slice = [Variable(torch.from_numpy(xs[i:j].astype('float32')), requires_grad=False)]
        return slice
        
    def predict(self, x):
        n = x.shape[0]
        self.model.eval()
        x = self.get_slice(x, 0, n)
        py = self.model.forward(*x)
        if type(py) is list or type(py) is tuple:
            ret = [y.data.cpu().numpy() for y in py]
        else:
            ret = py.data.cpu().numpy()
        return ret
        
    def fit(self, x, y, batch_size, epochs):
        n = x.shape[0]
        self.model.train()
        for epoch in range(epochs):
            print("epoch", epoch, "/", epochs)
            for i in range(0, n, batch_size):
                
                j = i + batch_size
                if j > n:
                    j = n
                
                batch_x = self.get_slice(x, i, j)
                batch_y = self.get_slice(y, i, j)
                
                self.optimizer.zero_grad()
                py = self.model.forward(*batch_x)
                
                loss = self.model.loss(*py, *batch_y)
                print("\rbatch", i, "/", n, "loss =", loss.data.cpu().numpy(), end='')
                loss.backward()
                self.optimizer.step()
            print("")