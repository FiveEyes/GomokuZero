import numpy as np
import sys
class BetterNoobPlayer(object):
	def __init__(self, n=15, m=5):
		self.n = n
		self.m = m
	def get_move_policy_value(self, board):
		return self.suggest(board)
	def suggest(self, board):
		n = self.n
		m = self.m
		if len(board.get_history()) == 0:
			if np.random.randint(2) == 0:
				return (n // 2 * n + n // 2), [[(n // 2 * n + n // 2)], [1.0]], 0.0
			else:
				return None, None, None
		if len(board.get_history()) == 1 and board.get_history()[0] == (n // 2 * n + n // 2):
			if np.random.randint(2) == 0:
				x = n // 2
				y = x
				move = []
				for (dx, dy) in [(1,0), (0,1), (1,1), (1,-1)]:
					move.append((x+dx) * n + y+dy)
					move.append((x-dx) * self.n + y-dy)
				policy = np.ones(len(move)) / len(move)
				return np.random.choice(move), [move, policy], 0.0
		
		
		
		
		players_moves = [[[],[],[]],[[],[],[]]]
		
		#available = board.get_available()
		p1 = board.get_cur_player() - 1
		p2 = 1 - p1
		board = board.get_board()
		
		
		for i in range(n):
			for j in range(n):
				for (dx, dy) in [(1,0), (0,1), (1,1), (1,-1)]:
					cnt = [0,0]
					empty_pos = []
					x = i
					y = j
					for l in range(m):
						if board[0,x,y] == 1.0:
							empty_pos += [x * n + y]
						elif board[1,x,y] == 1.0:
							cnt[0] += 1
						elif board[2,x,y] == 1.0:
							cnt[1] += 1
						x += dx
						y += dy
						if x >= n or y >= n or x < 0 or y < 0:
							break
					if empty_pos == []:
						continue
					for p in range(2):
						if cnt[p] == m - 1:
							#print('cnt[p]', p, cnt[p])
							players_moves[p][0] += empty_pos
						elif cnt[p] == m - 2:
							#print('cnt[p]', p, cnt[p], cnt[1-p], empty_pos)
							if cnt[1 - p] == 0:
								if board[0,i,j] == 1:
									if board[0,x - dx,y - dy] == 1:
										players_moves[p][1] += empty_pos
									elif  x < n and y < n and x >=0 and y >= 0 and board[0,x,y] == 1:
										players_moves[p][1] += empty_pos
										players_moves[p][1] += [x * n + y]
								else:
									players_moves[p][2] += empty_pos
							else:
								players_moves[p][2] += empty_pos
		#print(players_moves)
		if players_moves[p1][0] != []:
			policy_move = players_moves[p1][0]
			return np.random.choice(policy_move), [policy_move, np.ones(len(policy_move))], -1.0
		if players_moves[p2][0] != []:
			policy_move = players_moves[p2][0]
			return np.random.choice(policy_move), [policy_move, np.ones(len(policy_move))], 0.0
		if players_moves[p2][1] != []:
			policy_move = list(set(players_moves[p2][1] + players_moves[p1][1] + players_moves[p1][2] + players_moves[p2][2]))
			return np.random.choice(policy_move), [policy_move, None], 0.0
			
		return None, None, None
		
				
		