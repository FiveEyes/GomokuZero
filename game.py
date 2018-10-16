from players import NoobPlayer
import config
import numpy as np

def show_policy(policy):
	move_policy = zip(policy[0], policy[1])
	print("policy:", sorted(move_policy, key=lambda mp: mp[1]))
def simpl_policy(policy):
	index = np.nonzero(policy[1])
	return [policy[0][index], policy[1][index]]

class Game(object):
	def __init__(self):
		return
	def selfplay(self, board, player):
		show_b = config.game_config['show']
		noob = NoobPlayer(board.n, board.m)
		policy_history = []
		value_history = []
		while True:
			while True:
				#move, policy, value = noob.suggest(board)
				#if move == None:
				#	move, policy, value = player.get_move_policy_value(board)
				move, policy, value = player.get_move_policy_value(board)
				if board.move(move):
					break
			policy = simpl_policy(policy)
			if show_b:
				board.show()
				show_policy(policy)
				print("value: ", value)
			#print(str(len(board.get_history())) + ' ', end='', flush=True)


			policy_history.append(policy)
			value_history.append(value)
			#print("policy:", policy)
			if board.last_move_is_end() != 0:
				if board.last_move_is_end() > 0:
					print("Player {0} wins".format(3 - board.get_cur_player()))
				else:
					print("None wins!")
				break
		print('')
		return board.get_history(), policy_history, value_history
	
		