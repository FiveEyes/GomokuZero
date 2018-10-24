import os
os.environ["CUDA_VISIBLE_DEVICES"] = '-1'

import numpy as np
import time
import copy

from mcts_player import MCTSPlayer

from policy_value_net import PolicyValueNet 
from board import Board
from game import Game 
from players import HumanPlayer, HumanWASDPlayer
from memory import Memory
import config

board_n = config.board_config['board_n']
win = config.board_config['win']

model_filename = config.pvn_config['model_filename']

def play(p1, p2, dp = None):
	board = Board(board_n, win)
	game = Game()
	return game.play(board, p1, p2, dp)

def main():		
	human = HumanWASDPlayer()
	play(human, human)
	pvnet = PolicyValueNet(board_n, model_filename)
	mem = Memory()

	while True:
		
		mcts_player = MCTSPlayer(pvnet.get_pvnet_fn(), play_style = 3)
		bh, ph, vh = play(mcts_player, human, mcts_player)
		mem.save_data((bh, ph, vh))
		
		mcts_player = MCTSPlayer(pvnet.get_pvnet_fn(), play_style = 3)
		bh, ph, vh = play(human, mcts_player, mcts_player)
		mem.save_data((bh, ph, vh))
		
		

		
		
if __name__ == "__main__":
	main()