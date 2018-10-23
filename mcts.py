import numpy as np
import copy
import math

import config
from players import NoobPlayer, BetterNoobPlayer

c_PUCT = 5


class MCTSNode:
	def __init__(self, parent, move, pr):
		self.parent = parent
		self.move = move
		self.pr = pr
		self.children = {}
		self.N = 0
		self.Q = 0.0 if parent == None else -parent.Q
		# unused variable
		self.U = 0
		# if current player wins, winner = -1, else winner = 1
		self.winner = 0
		self.alive_children_count = 0
	def select(self):
		mv, node = max(self.children.items(), key=lambda mv_node: mv_node[1].get_value())
		return mv, node
	def expand(self, policy, value):
		self.Q = value
		for mv,pr in zip(policy[0], policy[1]):
			if mv not in self.children:
				self.children[mv] = MCTSNode(self, mv, pr)
		self.alive_children_count = len(policy[0])
	
	def get_value(self):
		if self.winner == -1:
			return -1.0
		if self.winner == 1:
			return 1.0 + c_PUCT * self.parent.N
		U = c_PUCT * math.sqrt(self.parent.N) * self.pr / (1.0 + self.N)
		return self.Q + U
	
	# TD update
	def get_Q(self):
		if self.is_leaf() or self.winner != 0:
			return self.Q
		
		mv, node = max(self.children.items(), key=lambda mv_node: mv_node[1].N)
		node_prob = node.N / self.N
		return (1.0 - node_prob) * self.Q - (node_prob * node.get_Q())
	def backup_value(self, value):
		self.N += 1
		self.Q += (value - self.Q) / self.N
		if self.parent is None:
			return
		#self.U = c_PUCT * math.sqrt(self.parent.N+1.0) * self.pr / (1.0 + self.N)
		self.parent.backup_value(-value)
		
	def backup_winner(self):
		if self.winner == 0 or self.parent is None or self.parent.winner != 0:
			return
		self.Q = self.winner * 1.0
		if self.winner == -1:
			self.parent.alive_children_count -= 1
			self.pr = 0.0
			self.N = 0
			if self.parent.alive_children_count == 0:
				self.parent.winner = 1
				self.parent.U = self.U + 1
				#print("found 100% win:", "move", self.parent.move)
				for mv, node in self.parent.children.items():
					if node.winner != -1:
						print("winner error")
					if node.U + 1 > self.parent.U:
						self.parent.U = node.U + 1
		else:
			self.parent.winner = -1
			if self.parent.U == 0 or self.parent.U > self.U + 1:
					self.parent.U = self.U + 1
		self.parent.backup_winner()
	def is_leaf(self):
		return self.children == {}
	def is_root(self):
		return self.parent is None
	def get_policy(self):
		policy_move = np.asarray(list(self.children.keys()), dtype='int')
		if self.winner == 0:
			policy_probs = np.asarray([ node.N * 1.0 for (mv, node) in self.children.items()], dtype='float32')
		elif self.winner == 1:
			#policy_probs = np.zeros(len(policy_move), dtype='float32')
			policy_probs = np.asarray([ 0.0 if node.U + 1 < self.U else 1.0 for (mv, node) in self.children.items()], dtype='float32')
			sum = policy_probs.sum()
			if sum > 0:
				policy_probs /= policy_probs.sum()
		else:
			policy_probs = np.asarray([ 0.0 if node.winner == 0 else 1.0 for (mv, node) in self.children.items()], dtype='float32')
		#if self.winner == -1:
		#	print("winner policy:", self.winner, np.nonzero(policy_probs)[0])

		sum = policy_probs.sum()
		if self.winner == 0:
			policy_probs /= policy_probs.sum()
		return [policy_move, policy_probs]
	
	def get_policy_value(self):
		return self.get_policy(), self.get_Q()
		
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
		self.temp_mode = config.mcts_config['temp_mode']
		self.threshold = config.mcts_config['threshold']
		self.noob = BetterNoobPlayer(board.n, board.m)
		
	def select_leaf(self):
		board = copy.deepcopy(self.board)
		node = self.root
		while True:
			if node.is_leaf() or node.winner != 0:
				break
			move, node = node.select()
			board.move(move)
		
		return node, board
		
	def rollout_without_play(self, node, board):
		return node.Q
	def expand(self, node, board):
		mv, policy, value = self.noob.suggest(board)
		if value == -1.0:
			node.winner = -1
			node.U = 2
			node.expand(policy, value)
			for m, c in node.children.items():
				c.winner = 1
				c.U = 1
			node.backup_winner()
			return
			
		if mv == None:
			policy, value = self.pvnet_fn(board)
		elif policy[1] is None:
			policy_moves = policy[0]
			net_policy, value = self.pvnet_fn(board)
			net_policy_dict = dict(zip(net_policy[0], net_policy[1]))
			policy_probs = [net_policy_dict[mv] for mv in policy_moves]
			policy = [policy_moves, policy_probs]
		elif value == 0.0:
			_, value = self.pvnet_fn(board)
		
		node.expand(policy, value)
	
	def tree_search(self):
		chosen_leaf, board = self.select_leaf()
		value = 0.0
		if chosen_leaf.winner != 0:
			value = float(chosen_leaf.winner)
		else:
			winner = board.last_move_is_end()
			if winner > 0:
				chosen_leaf.winner = 1
				chosen_leaf.U = 1
				value = 1.0
				chosen_leaf.backup_winner()
			else:
				self.expand(chosen_leaf, board)
				value = self.rollout_without_play(chosen_leaf, board)
		chosen_leaf.backup_value(value)
	
	def get_policy_value(self):
		[policy_move, policy_probs], value = self.root.get_policy_value()
		if self.root.winner != 0:
			return [policy_move, policy_probs], value
		if self.using_temperature:
			if self.step > self.temperature_step:
				if self.temp_mode == 0:
					best_move = max(self.root.children.items(), key=lambda mv_node: mv_node[1].N)[0]
					policy_probs = np.zeros(len(policy_move))
					if best_move > 0:
						policy_probs[policy_move.index(best_move)] = 1.0
				else:
					threshold = min(self.threshold, policy_probs.max())
					policy_probs[policy_probs < threshold] = 0.0
					policy_probs /= policy_probs.sum()
					#print("policy_probs", policy_probs)
				
		return [policy_move, policy_probs], value
		
	def update_move(self, board):
		for i in range(self.step, len(board.history)):
			self.root = self.root.get_child(board.history[i])
		self.step = len(board.history)
		self.root.parent = None
