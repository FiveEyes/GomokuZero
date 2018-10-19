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

def main():
	#simple_train()
	smart_worker_train()
	
		
		
if __name__ == "__main__":
	main()