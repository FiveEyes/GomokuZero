from mcts import MCTS
import numpy as np
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
		
		#print(policy)
		
		if self.play_style == 0:
			eps = self.dirichlet_eps
			dirichlet = np.random.dirichlet(0.03*np.ones(len(policy[0])))
			p = (1.0-eps)*policy[1]+eps*dirichlet
			p /= p.sum()
			move = np.random.choice(policy[0], p = p)
			print("real policy", p, "move", move)
		elif self.play_style == 1:
			move = np.random.choice(policy[0], p=policy[1])
		else:
			move = policy[np.argmax(policy[1])]
		return move, policy, value