import numpy as np
import copy
import math

import config
from players import NoobPlayer

c_PUCT = 5


class MCTSNode:
	def __init__(self, parent, move, pr):
		self.parent = parent
		self.move = move
		self.pr = pr
		self.children = {}
		self.N = 0
		self.Q = 0
		self.U = pr
	def select(self):
		mv, node = max(self.children.items(), key=lambda mv_node: mv_node[1].get_value())
		return mv, node
	def expand(self, policy, value):
		self.Q = value
		for mv,pr in zip(policy[0], policy[1]):
			if mv not in self.children:
				self.children[mv] = MCTSNode(self, mv, pr)
	def get_value(self):
		self.U = c_PUCT * math.sqrt(self.parent.N) * self.pr / (1.0 + self.N)
		return self.Q + self.U
	def backup_value(self, value):
		self.N += 1
		self.Q = self.Q + (value - self.Q) / self.N
		if self.parent is None:
			return
		#self.U = c_PUCT * math.sqrt(self.parent.N+1.0) * self.pr / (1.0 + self.N)
		self.parent.backup_value(-value)
		
	def is_leaf(self):
		return self.children == {}
	def is_root(self):
		return self.parent is None
		
	def get_child(self, mv):
		if mv not in self.children:
			print(self.children.keys())
			node = MCTSNode(None, None, 1.0)
			return node
		return self.children[mv]
	
class MCTS(object):
	def __init__(self, board, pvnet_fn):
		self.root = MCTSNode(None, None, 1.0)
		self.board = board
		self.step = board.get_len()
		self.pvnet_fn = pvnet_fn
		self.using_temperature = True
		self.temperature_step = config.mcts_config['temperature_step']
		self.noob = NoobPlayer(board.n, board.m)
		
	def select_leaf(self):
		board = copy.deepcopy(self.board)
		node = self.root
		while True:
			if node.is_leaf():
				break
			move, node = node.select()
			board.move(move)
		return node, board
		
	def rollout_with_play(self, node, board):
		player = board.get_cur_player()
		#board = copy.deepcopy(node_board)
		while board.last_move_is_end() == 0:
			if np.random.random_sample() < 0.9:
				move_probs, _ = self.pvnet_fn(board)
				mv, prob = max(
					move_probs,
					key=lambda mv_prob: mv_prob[1])
			else:
				move_probs, _ = self.pvnet_fn(board)
				k = np.random.randint(len(move_probs))
				mv, prob = move_probs[k]
			board.move(mv)
		winner = board.last_move_is_end()
		if winner > 0:
			if winner == player:
				return -1.0
			else:
				return 1.0
		return 0.0
	def rollout_without_play(self, node, board):
		return node.Q
	def expand(self, node, board):
		mv, policy, value = self.noob.suggest(board)
		if mv == None:
			policy, value = self.pvnet_fn(board)
		node.expand(policy, value)
	
	def tree_search(self):
		chosen_leaf, board = self.select_leaf()
		winner = board.last_move_is_end()
		value = 0.0
		if winner > 0:
			value = 1.0
		else:
			self.expand(chosen_leaf, board)
			value = self.rollout_without_play(chosen_leaf, board)
		chosen_leaf.backup_value(value)
	
	def get_policy_value(self):
		policy_move = list(self.root.children.keys())
		policy_probs = []
		if self.using_temperature:
			if self.step <= self.temperature_step:
				policy_probs = [ node.N / self.root.N for (mv, node) in self.root.children.items()]
			else:
				best_move = max(self.root.children.items(), key=lambda mv_node: mv_node[1].N)[0]
				policy_probs = np.zeros(len(policy_move))
				policy_probs[policy_move.index(best_move)] = 1.0
		else:
			policy_probs = [ node.N / self.root.N for (mv, node) in self.root.children.items()]
		policy = [np.asarray(policy_move), np.asarray(policy_probs)]
		value = self.root.Q
		return policy, value
	def update_move(self, board):
		for i in range(self.step, len(board.history)):
			self.root = self.root.get_child(board.history[i])
		self.step = len(board.history)
		self.root.parent = None
