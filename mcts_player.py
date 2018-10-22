from mcts import MCTS
import numpy as np
import copy
import config

class MCTSPlayer(object):
	def __init__(self, pvnet_fn, play_style = 0):
		self.mcts = None
		self.pvnet_fn = pvnet_fn
		self.play_style = play_style
		self.rollout_times = config.mcts_player_config['rollout_times']
		self.dirichlet_eps = config.mcts_player_config['dirichlet_eps']
	def init(self):
		self.mcts = None
	def start_tree_search(self):
		for i in range(self.rollout_times):
			self.mcts.tree_search()
	
	def get_move_policy_value(self, board):
		if self.mcts == None:
			self.mcts = MCTS(board, self.pvnet_fn)
		else:
			self.mcts.update_move(board)
		
		
		self.start_tree_search()
		
		policy, value = self.mcts.get_policy_value()
		#policy[1][policy[1] < 0.01] = 0.0
		sum = policy[1].sum()
		#if sum == 0.0:
		#	print("sum err:", sum)
		#if sum != 1.0:
		#	policy[1] /= policy[1].sum()
		#print(policy)
		
		
		# lose
		if sum == 0.0:
			move = np.random.choice(policy[0])
		# win
		elif sum > 1.5:
			move = policy[0][np.random.choice(np.nonzero(policy[1])[0])]
		elif self.play_style == 0:
			eps = self.dirichlet_eps
			dirichlet = np.random.dirichlet(0.03*np.ones(len(policy[0])))
			p = (1.0-eps)*policy[1]+eps*dirichlet
			p /= p.sum()
			move = np.random.choice(policy[0], p = p)
			#print("real policy", p, "move", move)
		elif self.play_style == 1:
			move = np.random.choice(policy[0], p=policy[1])
		elif self.play_style == 2:
			p = copy.deepcopy(policy[1])
			p[p<0.01] = 0.0
			
			p /= p.sum()
			move = np.random.choice(policy[0], p = p)
			#move = np.random.choice(policy[0], p = policy[1])
		else:
			print("mode 3")
			move = policy[0][np.argmax(policy[1])]
		return move, policy, value