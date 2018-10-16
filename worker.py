import threading

import copy
import numpy as np

from policy_value_net import PolicyValueNet
from board import Board
from game import Game
from mcts_player import MCTSPlayer
import train

import config

class Worker(threading.Thread):
	def __init__(self, id, n, server):
		threading.Thread.__init__(self)
		self.id = id
		self.n = n
		self.server = server
	def run(self):
		for i in range(self.n):
			print("Worker", self.id, "Match", i)
			pvnet = self.server.get_pvnet()
			bh, ph, vh = train.gen_selfplay_data(pvnet.get_pvnet_fn())
			self.server.push_history_queue(bh, ph, vh)
			