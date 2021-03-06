import numpy as np

class Board(object):
	def __init__(self, n=15, m=5, no_init=False):
		self.n = n
		self.n2 = n * n
		self.m = m
		self.history = []
		if no_init != False:
			return
		
		self.board = np.zeros((n,n,4), dtype='float32')
		
		self.available = np.zeros(n * n, dtype='int')
		self.available[n // 2 * n + n // 2] = 1
		
		for i in range(self.n):
			for j in range(self.n):
				self.board[i,j,0] = 1.0

	def init(self):
		self.history = []
		self.board = np.zeros((self.n,self.n,4), dtype='float32')
		self.available = np.zeros(self.n * self.n, dtype='int')
		self.available[self.n // 2 * self.n + self.n // 2] = 1

		for i in range(self.n):
			for j in range(self.n):
				self.board[i,j,0] = 1.0
				
	def show(self):
		print("{0}x{0}-{1}, player {2}".format(self.n, self.m, self.get_cur_player()))
		board = self.board
		for i in range(self.n):
			str = ''
			for j in range(self.n):
				if board[i,j,0] == 1.0:
					str += '_'
				elif board[i,j,1] == 1.0:
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
		self.board[:,:,3] = player - 1.0
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
		return self.board[x,y,0] == 1.0
	
	
	def update_available(self, pos):
		x = pos // self.n
		y = pos % self.n
		lx = max(0, x - 3)
		hx = min(self.n, x + 4)
		ly = max(0, y - 3)
		hy = min(self.n, y + 4)
		for i in range(lx, hx):
			for j in range(ly, hy):
				if self.board[i, j, 0] > 0.0:
					self.available[i * self.n + j] = 1
		self.available[x * self.n + y] = 0
		
	def move(self, pos):
		player = self.get_cur_player()
		#print("player:", player)
		x = pos // self.n
		y = pos % self.n
		#print("move", player, x, y)
		if self.board[x,y,0] != 1.0:
			print('move error:', x, y)
			raise ValueError('move error: ' + str(x) + ' ' + str(y))
			return False
		self.board[x,y,0] = 0.0
		self.board[x,y,player] = 1.0
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
			if self.board[i,y,player] != 0:
				cnt += 1
			else:
				cnt = 0
			if cnt == self.m:
				return player
		cnt = 0
		for i in range(max(y-self.m, 0), min(y+self.m+1, self.n)):
			if self.board[x,i,player] != 0:
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
			if self.board[px, py, player] != 0:
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
			if self.board[px, py, player] != 0:
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
		