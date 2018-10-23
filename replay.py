import numpy as np
import time
import copy

from mcts_player import MCTSPlayer

from policy_value_net import PolicyValueNet 
from board import Board
from game import Game 
from players import HumanPlayer
from train import train
from smart_server import SmartServer
import config

board_n = config.board_config['board_n']
win = config.board_config['win']

def replay(bh, player):
	board = Board(board_n, win)
	mv, policy, value = player.get_move_policy_value(board)
	print(mv, policy, value)
	for b in bh:
		board.move(b)
		mv, policy, value = player.get_move_policy_value(board)
		board.show()
		print(mv, policy, value)

	


def main():
	return
		
		
if __name__ == "__main__":
	main()