from players import NoobPlayer
import config
import numpy as np

def show_policy(policy):
	move_policy = zip(policy[0], policy[1])
	print("policy:", sorted(move_policy, key=lambda mp: mp[1]))
def simpl_policy(policy):
	index = np.nonzero(policy[1])
	return [policy[0][index], policy[1][index]]
	
def show_board_policy_value(board, policy, value):
	move_policy = zip(policy[0], policy[1])
	move_policy = sorted(move_policy, key=lambda mp: mp[1])
	history = board.get_history()
	last_x = history[-1] // board.n
	last_y = history[-1] % board.n
	best_x = move_policy[-1][0] // board.n
	best_y = move_policy[-1][0] % board.n
	print("{0}x{0}-{1}, player {2}, len {3}".format(board.n, board.m, 3 - board.get_cur_player(), len(history)))
	b = board.get_board()
	for i in range(board.n):
		s = ''
		for j in range(board.n):
			if i == last_x and j == last_y:
				s += str(5 - board.get_cur_player())
			elif i == best_x and j == best_y:
				s += "S"
			elif b[i,j,0] == 1.0:
				s += '_'
			elif b[i,j,1] == 1.0:
				s += '1'
			else:
				s += '2'
		print(s)
	print(history)
	move_policy = list(filter(lambda mp: mp[1] > 0.01, move_policy))
	print("policy:", sorted(move_policy, key=lambda mp: mp[1]))
	print("value: ", value)

class Game(object):
	def __init__(self, name = None):
		self.name = name
		return
	def play(self, board, p1, p2, data_player = None):
		show_b = config.game_config['show']
		
		players = [p1,p2]
		cur_player = 0
		
		policy_history = []
		value_history = []
		while True:
			while True:
				move, policy, value = players[cur_player].get_move_policy_value(board)
				if data_player != None and data_player != players[cur_player]:
					_, policy, value = data_player.get_move_policy_value(board)
				if board.move(move):
					policy_history.append(policy)
					value_history.append(value)
					break
			cur_player = 1 - cur_player
			policy = simpl_policy(policy)
			if show_b:
				if self.name != None:
					print(self.name)
				show_board_policy_value(board, policy, value)

			if board.last_move_is_end() != 0:
				if board.last_move_is_end() > 0:
					print("Player {0} wins".format(3 - board.get_cur_player()))
				else:
					print("None wins!")
				break
		return board.get_history(), policy_history, value_history

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
				if self.name != None:
					print(self.name)
				show_board_policy_value(board, policy, value)
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
	
		