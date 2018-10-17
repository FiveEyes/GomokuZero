import threading

import copy
import numpy as np
from queue import Queue


from policy_value_net import PolicyValueNet
from board import Board
from game import Game
from mcts_player import MCTSPlayer
import train

import config

class SmartWorker(threading.Thread):
	def __init__(self, id, n, server):
		threading.Thread.__init__(self)
		self.id = id
		self.n = n
		self.server = server
		self.call_queue = server.get_call_queue()
		self.ret_queue = Queue()
		self.quit_queue = server.get_quit_queue()
		
	def get_ret_queue(self):
		return self.ret_queue
	def get_predict_fn(self):
		def predict_fn(board):
			self.call_queue.put((self.id, board))
			m,p,v =  self.ret_queue.get()
			return (m,p),v
		return predict_fn
		
	def run(self):
		while True:
			game_id = self.server.get_next_game_id()
			if game_id == None:
				break
			print("Worker", self.id, "Match", game_id)
			bh, ph, vh = train.gen_selfplay_data(self.get_predict_fn(), "Worker " + str(self.id) + ", Match " + str(game_id))
			self.server.push_history_queue(game_id, bh, ph, vh)
		self.quit_queue.put(self.id)