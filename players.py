import numpy as np
import sys
class HumanPlayer(object):
	def __init__(self):
		self.board = None
		self.computed = False
	def set_board(self, board):
		self.board = board
		self.computed = False
		return self
	
	def get_move_policy_value(self, board):
		return (self.get_move(board), [np.asarray([self.last_mv]), np.ones(1)], 1.0)

	def get_move(self, board):
		pos = input("Your move:")
		pos = pos.split()
		pos = [int(i) for i in pos]
		self.last_mv = pos[0] * board.n + pos[1]
		return self.last_mv
		
def getchar():
	# Returns a single character from standard input
	import os
	ch = ''
	if os.name == 'nt': # how it works on windows
		import msvcrt
		ch = msvcrt.getch()
	else:
		import tty, termios, sys
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setraw(sys.stdin.fileno())
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
	if ord(ch) == 3: quit() # handle ctrl+C
	return ch
  
class HumanWASDPlayer(object):
	def __init__(self):
		self.cur = 0

	def get_move_policy_value(self, board):
		return (self.get_move(board), [np.asarray([self.cur]), np.ones(1)], 1.0)

	def show_board(self, board):
		n = board.n
		x = self.cur // n
		y = self.cur % n
		b = board.get_board()
		flag = False
		for i in range(n):
			s = ''
			for j in range(n):
				if i == x and j == y:
					s += '#'
					if b[i,j,0] == 1.0:
						flag = True
				elif b[i,j,0] == 1.0:
					s += '_'
				elif b[i,j,1] == 1.0:
					s += '1'
				else:
					s += '2'
			print(s)
		if flag:
			print(x, y, "is available")
		else:
			print(x, y, "is not available")
	def check_cur(self, board, cur, nxt_cur):
		if nxt_cur < 0 or nxt_cur >= board.n * board.n:
			return cur
		return nxt_cur
	def get_move(self, board):
		h = board.get_history()
		n = board.n
		if len(h) == 0:
			self.cur = n // 2 * n + n // 2
		else:
			self.cur = h[-1]
		while True:
			self.show_board(board)
			c = getchar()
			if c == 'w':
				self.cur = self.check_cur(board, self.cur, self.cur - board.n)
			elif c == 'a':
				self.cur = self.check_cur(board, self.cur, self.cur - 1)
			elif c == 's':
				self.cur = self.check_cur(board, self.cur, self.cur + board.n)
			elif c == 'd':
					self.cur = self.check_cur(board, self.cur, self.cur + 1)
			elif c == '\r':
				break
			try:
				print(int(c))
			except ValueError as err:
				print(err)
				continue
				
		return self.cur
			
			
			
	
		
class NoobPlayer(object):
	def __init__(self, n=15, m=5):
		self.n = n
		self.m = m
	def suggest(self, board):
		if len(board.get_history()) == 0:
			if np.random.randint(2) == 0:
				return (self.n // 2 * self.n + self.n // 2), [[(self.n // 2 * self.n + self.n // 2)], [1.0]], 0.0
			else:
				return None, None, None
		if len(board.get_history()) == 1 and board.get_history()[0] == (self.n // 2 * self.n + self.n // 2):
			if np.random.randint(2) == 0:
				x = self.n // 2
				y = x
				move = []
				for (dx, dy) in [(1,0), (0,1), (1,1), (1,-1)]:
					move.append((x+dx) * self.n + y+dy)
					move.append((x-dx) * self.n + y-dy)
				policy = np.ones(len(move)) / len(move)
				return np.random.choice(move), [move, policy], 0.0
			
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
		
				
		