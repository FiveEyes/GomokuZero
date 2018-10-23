import os
os.environ["CUDA_VISIBLE_DEVICES"] = '-1'

import numpy as np
import time
import copy

from mcts_player import MCTSPlayer

#from policy_value_net import PolicyValueNet 
from board import Board
from game import Game 
from players import HumanPlayer, HumanWASDPlayer, BetterNoobPlayer
from memory import Memory
from replay import replay
import config

board_n = config.board_config['board_n']
win = config.board_config['win']

model_filename = config.pvn_config['model_filename']

def play(p1, p2, dp):
	board = Board(board_n, win)
	game = Game()
	return game.play(board, p1, p2, dp)

def main():		
	human = HumanWASDPlayer()
	#bh, ph, vh = play(human, human, None)
	#replay(bh, BetterNoobPlayer())
	replay([112, 96, 111, 95, 109, 94, 108, 93, 110], BetterNoobPlayer())

		
if __name__ == "__main__":
	main()