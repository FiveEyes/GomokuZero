import numpy as np

class HumanPlayer(object):
	def __init__(self):
		self.board = None
		self.computed = False
	def set_board(self, board):
		self.board = board
		self.computed = False
		return self
	
	def get_move_policy_value(self, board):
		return (self.get_move(board), [[self.last_mv], [1.0]], 1.0)

	def get_move(self, board):
		pos = input("Your move:")
		pos = pos.split()
		pos = [int(i) for i in pos]
		self.last_mv = pos[0] * board.n + pos[1]
		return self.last_mv
		
class NoobPlayer(object):
	def __init__(self, n=15, m=5):
		self.n = n
		self.m = m
	def suggest(self, board):
		p1 = board.get_cur_player()
		p2 = 3 - p1
		policy_move = []
		board = board.get_board()
		for i in range(self.n):
			for j in range(self.n):
				if board[i,j,p2] == 1:
					continue
				for (dx, dy) in [(1,0), (0,1), (1,1), (1,-1)]:
					selfcnt = 0
					oppcnt = 0
					empty_pos = None
					x = i
					y = j
					for l in range(self.m):
						if board[x,y,0] == 1:
							if empty_pos is None:
								empty_pos = x * self.n + y
						elif board[x,y,p1] == 1:
							selfcnt += 1
						elif board[x,y,p2] == 1:
							oppcnt += 1
						x += dx
						y += dy
						if x < 0 or y < 0 or x >= self.n or y >= self.n:
							break
					if empty_pos is None or oppcnt != 0:
						continue
					if selfcnt == self.m - 1:
						policy_move.append(empty_pos)
		if policy_move == []:
			return None, None, None
		else:
			return np.random.choice(policy_move), [policy_move, np.ones(len(policy_move)) / len(policy_move)], -1.0
		
				
		