import copy
import numpy as np

from policy_value_net import PolicyValueNet
from board import Board
from game import Game
from mcts_player import MCTSPlayer
from memory import Memory
import config

board_n = config.board_config['board_n']
win = config.board_config['win']

def gen_selfplay_data(pvnet_fn):
	board = Board(board_n, win)
	game = Game()
	mcts_player = MCTSPlayer(pvnet_fn)
	bh, ph, vh = game.selfplay(board, mcts_player)
	return bh, ph, vh

		

def train(pvnet, times):
	mem = Memory()
	train_fn = pvnet.get_train_fn()
	for i in range(times):
		print("Match ", i)
		bh, ph, vh = gen_selfplay_data(pvnet)
		mem.push_history(bh, ph, vh)
	train_fn(*mem.get_history())
	
		
