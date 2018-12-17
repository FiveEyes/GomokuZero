from multiprocessing import Process, Queue

from threading import Thread

from memory_pytorch import Memory
from smart_worker import SmartWorker
import config
class PredictWorker(Thread):
	def __init__(self, server):
		Thread.__init__(self)
		self.server = server
	def set_ret_qs(self, ret_qs):
		self.ret_qs = ret_qs
	def run(self):
		server = self.server
		pvnet_fn = server.pvnet.get_pvnet_fn(single=False)
		call_queue = server.call_queue
		ret_qs = self.ret_qs
		while True:
			ids = []
			bs = []
			while True:
				id, board = call_queue.get()
				ids.append(id)
				bs.append(board)
				if call_queue.empty():
					break
			#print(ids)
			ret = pvnet_fn(bs)
			
			for i in ids:
				m, p, v = next(ret)
				ret_qs[i].put((m,p,v))
	
class SmartServer(object):
	def __init__(self, pvnet):
		self.mem = Memory()
		self.pvnet = pvnet
		self.train_fn = pvnet.get_train_fn()
		self.worker_n = config.server_config['worker_n']
		self.call_queue = Queue()
		self.quit_queue = Queue()
		self.ret_qs = []
		
		self.game_id = self.mem.get_game_id()
		self.game_num = config.server_config['game_num']
		self.game_id_queue = Queue()
		
		self.init_workers()
		
		return
	def get_pvnet(self):
		return self.pvnet
	def get_call_queue(self):
		return self.call_queue
	def get_next_game_id(self):
		return self.game_id_queue.get()
		#try:
		#	id = self.game_id_queue.get_nowait()
		#	return id
		#except:
		#	return None
		
	def get_quit_queue(self):
		return self.quit_queue
		
	def push_history_queue(self, game_id, bh, ph, vh):
		self.mem.push_history_queue(bh, ph, vh)
		
	def init_workers(self):
		self.pw = PredictWorker(self)
		self.workers = [ SmartWorker(i, self, play_style=0) for i in range(self.worker_n)]
		#self.workers[0].play_style = 1
		#self.workers[1].play_style = 2
		self.workers[0].set_moves([112, 128, 126])
		#self.workers[1].set_moves([112, 97, 96, 128, 80, 64, 110, 111, 124, 138, 125, 95, 126, 127, 79, 78, 122, 123, 108, 143, 159, 94, 140, 98, 92, 76, 156])
		#self.workers[2].set_moves([112, 98, 114, 113, 128, 142, 144, 160, 129, 99, 127, 126, 130, 131, 158, 172, 100, 174])
		#self.workers[3].set_moves([112, 98, 114, 113, 128, 142, 144, 160, 129, 99, 127, 126, 130, 131, 158, 172, 100, 174, 116, 102, 115, 85, 132, 84, 148, 164, 146, 117, 145, 147, 162, 178, 176, 57, 71, 87, 72, 86, 83, 88])
		#self.workers[4].set_moves([112, 98, 114, 113, 128, 142, 144, 160, 129, 99, 127, 126, 130, 131, 158, 172, 100, 174, 87])
		
		workers_processes = [Process(target=w.get_run_fn()) for w in self.workers]
		
		self.ret_qs = [ w.get_ret_queue() for w in self.workers]
		self.pw.set_ret_qs(self.ret_qs)
		
		self.pw.start()
		for i, worker_process in enumerate(workers_processes):
			print("Starting worker {}".format(i))
			worker_process.start()
			

	def train(self):
		#print("Training")
		#self.train_fn(*self.mem.get_history())
		#self.pvnet.save_model(config.pvn_config['model_filename'])
		#print("Done")
		
		for i in range(self.game_num):
			self.game_id_queue.put(self.game_id + i)
		self.game_id += self.game_num
		
		for _ in range(self.game_num):
			print("Match", self.quit_queue.get(), "is done.")
		
		print("Training")
		self.train_fn(*self.mem.get_history())
		print("Done")
		
			
		
	