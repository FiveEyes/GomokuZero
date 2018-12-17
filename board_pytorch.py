import numpy as np

class Board(object):
	def __init__(self, n=15, m=5, no_init=False):
		self.n = n
		self.n2 = n * n
		self.m = m
		self.history = []
		if no_init != False:
			return
		
		self.board = np.zeros((4,n,n), dtype='float32')
		
		self.available = np.zeros(n * n, dtype='int')
		self.available[n // 2 * n + n // 2] = 1
		
		self.board[0,:,:] = 1.0

	def init(self):
		self.history = []
		self.board = np.zeros((4,self.n,self.n), dtype='float32')
		self.available = np.zeros(self.n * self.n, dtype='int')
		self.available[self.n // 2 * self.n + self.n // 2] = 1

		self.board[0,:,:] = 1.0
				
	def show(self):
		print("{0}x{0}-{1}, player {2}".format(self.n, self.m, self.get_cur_player()))
		board = self.board
		for i in range(self.n):
			str = ''
			for j in range(self.n):
				if board[0,i,j] == 1.0:
					str += '_'
				elif board[0,i,j] == 1.0:
					str += '1'
				else:
					str += '2'
			print(str)
		print(self.history)
		
	def get_available(self):
		return self.available
		
	def get_len(self):
		return len(self.history)

	def get_board(self):
		player = self.get_cur_player()
		self.board[3,:,:] = player - 1.0
		return self.board
	def get_history(self):
		return self.history
		
	def get_cur_player(self):
		if (len(self.history) & 1) == 0:
			return 1
		else:
			return 2
		
	def move_is_enable(self, pos):
		x = pos // self.n
		y = pos % self.n
		return self.board[0,x,y] == 1.0
	
	
	def update_available(self, pos):
		x = pos // self.n
		y = pos % self.n
		lx = max(0, x - 3)
		hx = min(self.n, x + 4)
		ly = max(0, y - 3)
		hy = min(self.n, y + 4)
		for i in range(lx, hx):
			for j in range(ly, hy):
				if self.board[0, i, j] > 0.0:
					self.available[i * self.n + j] = 1
		self.available[x * self.n + y] = 0
		
	def move(self, pos):
		player = self.get_cur_player()
		#print("player:", player)
		x = pos // self.n
		y = pos % self.n
		#print("move", player, x, y)
		if self.board[0,x,y] != 1.0:
			print('move error:', x, y)
			raise ValueError('move error: ' + str(x) + ' ' + str(y))
			return False
		self.board[0,x,y] = 0.0
		self.board[player,x,y] = 1.0
		self.history.append(pos)
		self.update_available(pos)
		return True
	
	def last_move_is_end(self):
		if self.history == []:
			return 0
		pos = self.history[-1]
		player = 3 - self.get_cur_player()
		x = pos // self.n
		y = pos % self.n

		cnt = 0
		for i in range(max(x-self.m, 0), min(x+self.m+1, self.n)):
			if self.board[player,i,y] != 0:
				cnt += 1
			else:
				cnt = 0
			if cnt == self.m:
				return player
		cnt = 0
		for i in range(max(y-self.m, 0), min(y+self.m+1, self.n)):
			if self.board[player,x,i] != 0:
				cnt += 1
			else:
				cnt = 0
			if cnt == self.m:
				return player
		
		l = min(x,y,self.m)
		px = x - l
		py = y - l
		
		cnt = 0
		for i in range(2 * self.m):
			if self.board[player,px, py] != 0:
				cnt += 1
			else:
				cnt = 0
			if cnt == self.m:
				return player
			px += 1
			py += 1
			if px >= self.n or py >= self.n:
				break
				
		l = min(x, self.n - 1 - y, self.m)
		px = x - l
		py = y + l
		
		cnt = 0
		for i in range(2 * self.m):
			if self.board[player, px, py] != 0:
				cnt += 1
			else:
				cnt = 0
			if cnt == self.m:
				return player
			px += 1
			py -= 1
			if px >= self.n or py < 0:
				break
		if len(self.history) == self.n2:
			return -1
		return 0

def show_board_policy_value(board, policy, value):
	history = board.get_history()
	last_x = history[-1] // board.n
	last_y = history[-1] % board.n
	
	move_policy = zip(policy[0], policy[1])
	move_policy = sorted(move_policy, key=lambda mp: mp[1])
	if len(policy[0]) > 0:
		best_x = move_policy[-1][0] // board.n
		best_y = move_policy[-1][0] % board.n
	else:
		best_x = -1
		best_y = -1
	print("{0}x{0}-{1}, player {2}, len {3}".format(board.n, board.m, 3 - board.get_cur_player(), len(history)))
	b = board.get_board()
	for i in range(board.n):
		s = ''
		for j in range(board.n):
			if i == last_x and j == last_y:
				s += str(5 - board.get_cur_player())
			elif i == best_x and j == best_y:
				s += "S"
			elif b[0,i,j] == 1.0:
				s += '_'
			elif b[1,i,j] == 1.0:
				s += '1'
			else:
				s += '2'
		print(s)
	print(history)
	move_policy = list(filter(lambda mp: mp[1] > 0.01, move_policy))
	print("policy:", sorted(move_policy, key=lambda mp: mp[1]))
	print("value: ", value)