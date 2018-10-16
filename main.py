import numpy as np
import time
import copy

from mcts_player import MCTSPlayer

from policy_value_net import PolicyValueNet 
from board import Board
from game import Game 
from players import HumanPlayer
from train import train
from server import Server
from smart_server import SmartServer
import config

board_n = config.board_config['board_n']
win = config.board_config['win']

model_filename = "first_model_" + str(board_n) + '_' +str(win) + '.h5'

def simple_train():
	#board = Board(board_n, win)
	#game = Game()
	pvnet = PolicyValueNet(board_n, model_filename)
	#mcts_player = MCTSPlayer(pvnet.get_pvnet_fn())
	#bh, ph, vh = game.selfplay(board, mcts_player)
	#bh, ph, vh = game.selfplay(board, HumanPlayer())
	#print(vh)
	while True:
		train(pvnet, config.train_config['train_samples'])
		pvnet.save_model(model_filename)
def worker_train():
	pvnet = PolicyValueNet(board_n, model_filename)
	server = Server(pvnet)
	while True:
		server.train()
		pvnet.save_model(model_filename)
def smart_worker_train():
	pvnet = PolicyValueNet(board_n, model_filename)
	server = SmartServer(pvnet)
	while True:
		server.train()
		pvnet.save_model(model_filename)

def main():
	#simple_train()
	#worker_train()
	smart_worker_train()

		
		
if __name__ == "__main__":
	main()