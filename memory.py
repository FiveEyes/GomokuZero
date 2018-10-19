import copy
import numpy as np
import pickle as pkl
import os.path
 

from multiprocessing import Queue

from board import Board
from game import Game
import config

board_n = config.board_config['board_n']
win = config.board_config['win']

def decode_board(bh):
	bs = []
	board = Board(board_n, win)
	for mv in bh:
		raw_board = copy.deepcopy(board.get_board())
		bs.append(raw_board)
		board.move(mv)
	return bs
def decode_policy(policy):
	raw_policy = np.zeros(board_n * board_n)
	for mv, probs in zip(policy[0], policy[1]):
		raw_policy[mv] = probs
	return raw_policy
	
def gen_mirrors(raw_board, policy, value):
	ret_board = np.zeros((board_n,board_n,4))
	ret_board[:,:,0] = raw_board[:,:,0]
	ret_board[:,:,1] = raw_board[:,:,2]
	ret_board[:,:,2] = raw_board[:,:,1]
	ret_board[:,:,3] = 1.0 - raw_board[:,:,3]
	ret_policy = copy.deepcopy(policy)
	ret_value = value
	return ret_board, ret_policy, ret_value
	
def gen_rotations(raw_board, policy, value):
	n2 = board_n * board_n
	b = raw_board
	p = policy.reshape((board_n, board_n))
	bs = []
	ps = []
	vs = []
	for i in range(4):
		bs.append(b)
		ps.append(p.reshape(n2))
		vs.append(value)
		b = np.rot90(b)
		p = np.rot90(p)
		
	b = np.flip(b, axis=0)
	p = np.flip(p, axis=0)
	for i in range(4):
		bs.append(b)
		ps.append(p.reshape(n2))
		vs.append(value)
		b = np.rot90(b)
		p = np.rot90(p)
	return bs, ps, vs

class Memory(object):
	def __init__(self, save_path = None):
		self.buff_max_sz = config.train_config['buff_max_sz']
		self.bhb = []
		self.phb = []
		self.vhb = []
		self.bpv_queue = Queue()
		self.game_id = config.memory_config['game_id']
		if save_path == None:
			save_path = config.memory_config['save_path']
		self.file_prefix = save_path + str(board_n) + '_' + str(win) + '_'
		self.load_files(save_path)
	
	def get_game_id(self):
		return self.game_id
		
	def push_history_queue(self, bh, ph, vh):
		bpvh = (bh, ph, vh)
		self.save_data(bpvh)
		self.bpv_queue.put(bpvh)
	def save_data(self, bpvh):
		file_name = self.file_prefix + str(self.game_id) + '.sav'
		while os.path.isfile(file_name):
			self.game_id += 1
			file_name = self.file_prefix + str(self.game_id) + '.sav'
		with open(self.file_prefix + str(self.game_id) + '.sav', 'wb') as f:
			pkl.dump(bpvh, f)
		self.game_id += 1
		
	def load_file(self, file_name):
		if not os.path.isfile(file_name):
			return False
		#print(file_name)
		with open(file_name, 'rb') as f:
			bpvh = pkl.load(f)
			self.bpv_queue.put(bpvh)
		return True

	def load_files(self, path):
		while self.load_file(self.file_prefix + str(self.game_id) + '.sav'):
			self.game_id += 1
			
			
	def push_history(self, bh, ph, vh):
		if self.buff_max_sz > 0 and len(self.vhb) >= self.buff_max_sz:
			self.bhb = self.bhb[len(self.vhb)//2:]
			self.phb = self.phb[len(self.vhb)//2:]
			self.vhb = self.vhb[len(self.vhb)//2:]
		bh = decode_board(bh)
		ph = [decode_policy(policy) for policy in ph]
		#print("match size:", len(bh))
		for i in range(len(vh)):
			bm, pm, vm = gen_mirrors(bh[i], ph[i], vh[i])
			bs, ps, vs = gen_rotations(bh[i], ph[i], vh[i])
			self.bhb += bs
			self.phb += ps
			self.vhb += vs
			bs, ps, vs = gen_rotations(bm, pm, vm)
			self.bhb += bs
			self.phb += ps
			self.vhb += vs
		#print("buff size:", len(self.bhb))
		
	def get_history(self):
		while not self.bpv_queue.empty():
			bh, ph, vh = self.bpv_queue.get()
			self.push_history(bh, ph, vh)
		print("buff size:", len(self.bhb))
		return self.bhb, self.phb, self.vhb
	