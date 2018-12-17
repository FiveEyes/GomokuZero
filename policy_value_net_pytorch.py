import torch
from torch import nn, optim, autograd
import torch.nn.functional as F

import numpy as np

import copy
import os
#from threading import Lock

import config

import utils_pytorch

block_sz = 7
filter_sz = 256

def same_padding(kernel_size):
    if type(kernel_size) is not tuple:
        return (kernel_size - 1) // 2
    else:
        return tuple([ (ks - 1) // 2 for ks in kernel_size ])
class ConvBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size):
        super(ConvBlock, self).__init__()
        padding = same_padding(kernel_size)
        self.model = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size, padding=padding),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(True),
        )
    def forward(self, x):
        return self.model(x)

class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size):
        super(ResidualBlock, self).__init__()
        padding = same_padding(kernel_size)
        self.shortcut = nn.Conv2d(in_channels, out_channels, kernel_size=1,padding=0, bias=False)
        self.model = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size, padding=padding),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(True),
            nn.Conv2d(in_channels, out_channels, kernel_size, padding=padding),
            nn.BatchNorm2d(out_channels),
        )
    def forward(self, x):
        return F.relu(self.shortcut(x) + self.model(x))



class PolicyValueNetImpl(nn.Module):
    def __init__(self, n = 15):
        super(PolicyValueNetImpl, self).__init__()
        self.n = n
        self.l2_const = 1e-4
        self.build_model()
    def build_model(self):
        self.conv_block = ConvBlock(4, filter_sz, 3)
        self.res_blocks = nn.ModuleList([ResidualBlock(filter_sz, filter_sz, 3) for i in range(block_sz)])
        
        self.policy_net = ConvBlock(filter_sz, 2, 1)
        self.policy_net_linear = nn.Sequential(
            nn.Linear(self.n*self.n*2,self.n*self.n),
            nn.Softmax(1),
        )
        
        self.value_net = ConvBlock(filter_sz, 1, 1)
        self.value_net_linear = nn.Sequential(
            nn.Linear(self.n*self.n,filter_sz*2),
            nn.Linear(filter_sz*2,1),
            nn.Tanh(),
        )
        #self.celoss = nn.CrossEntropyLoss()
        self.mseloss = nn.MSELoss()
    def forward(self, x):
        x = self.conv_block(x)
        for res_block in self.res_blocks:
            x = res_block(x)
        px = self.policy_net(x)
        px = px.view(px.size(0),-1)
        px = self.policy_net_linear(px)
        
        vx = self.value_net(x)
        vx = px.view(vx.size(0),-1)
        vx = self.value_net_linear(vx)
        
        return px, vx
    
    def cross_entropy_loss(self, predict_policy, policy):
        return torch.mean(torch.sum(-torch.log(predict_policy) * policy, 1))
        
    def loss(self, predict_policy, predict_value, policy, value):
        value_loss = self.mseloss(predict_value, value)
        #policy_loss = self.mseloss(predict_policy, policy)
        policy_loss = self.cross_entropy_loss(predict_policy, policy) + self.mseloss(predict_policy, policy)
        return policy_loss + value_loss


class PolicyValueNet():
    def __init__(self, n = 15, filename=None):
        self.n = n
        self.l2_const = 1e-4
        self.model = PolicyValueNetImpl(n)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.002)
        if filename != None and os.path.exists(filename):
            self.model.load_state_dict(torch.load(filename))
            print("load", filename)
        if torch.cuda.is_available():
            self.model.cuda()
            
    def get_train_fn(self):
        batch_size = config.pvn_config['batch_size']
        epochs = config.pvn_config['epochs']
        model = utils_pytorch.Model(self.model, self.optimizer)
        def train_fn(board, policy, value):
            board = np.asarray(board)
            policy = np.asarray(policy)
            value = np.asarray(value)
            print("training")
            model.fit(board, [policy, value], batch_size, epochs)
        return train_fn
    def get_pvnet_fn(self, single = True):
        model = utils_pytorch.Model(self.model, self.optimizer)
        def pvnet_fn(board):
            nparr_board = board.get_board()
            probs, value = model.predict(np.expand_dims(nparr_board, axis=0))
            policy_move = board.get_available().nonzero()[0]
            policy_probs = probs[0][policy_move]
            return (policy_move, policy_probs), value[0][0]
        def pvnet_fn_m(boards):
            nparr_boards = np.asarray([b.get_board() for b in boards])
            #print(nparr_boards.shape)
            probs, value = model.predict(nparr_boards)
            policy_moves = [b.get_available().nonzero()[0] for b in boards]
            policy_probs = [p[policy_moves[i]] for i, p in enumerate(probs)]
            return zip(policy_moves, policy_probs, value.ravel())
        return pvnet_fn if single else pvnet_fn_m
        
    def save_model(self, model_file):
        if os.path.exists(model_file):
            os.remove(model_file)
        torch.save(self.model.state_dict(), model_file)
#       """ save model params to file """
#       net_params = self.get_policy_param()
#       pickle.dump(net_params, open(model_file, 'wb'), protocol=2)
        
        