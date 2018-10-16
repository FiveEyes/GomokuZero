import threading
from queue import Queue

from memory import Memory
from smart_worker import SmartWorker
import config
class PredictWorker(threading.Thread):
	def __init__(self, server):
		threading.Thread.__init__(self)
		self.server = server
	def run(self):
		#count = self.worker_n
		server = self.server
		pvnet_fn = server.pvnet.get_pvnet_fn(single=False)
		while True:
			#while not self.quit_queue.empty():
			#	count -= 1
			#	self.quit_queue.get()
			#	print("count:", count)
			#if count == 0:
			#	break
			ids = []
			bs = []
			while True:
				id, board = server.call_queue.get()
				ids.append(id)
				bs.append(board)
				if server.call_queue.empty():
					break
			#print(ids)
			ret = pvnet_fn(bs)
			
			for i in ids:
				m, p, v = next(ret)
				server.ret_qs[i].put((m,p,v))
	
class SmartServer(object):
	def __init__(self, pvnet):
		self.mem = Memory()
		self.pvnet = pvnet
		self.train_fn = pvnet.get_train_fn()
		self.worker_n = config.server_config['worker_n']
		self.worker_play_n = config.server_config['worker_play_n']
		self.call_queue = Queue()
		self.quit_queue = Queue()
		self.ret_qs = []
		self.pw = PredictWorker(self)
		self.pw.start()
		return
	def get_pvnet(self):
		return self.pvnet
	def get_call_queue(self):
		return self.call_queue
		
	def get_quit_queue(self):
		return self.quit_queue
		
	def push_history_queue(self, bh, ph, vh):
		self.mem.push_history_queue(bh, ph, vh)

	def train(self):
		workers = [ SmartWorker(i, self.worker_play_n, self) for i in range(self.worker_n)]
		self.ret_qs = [ w.get_ret_queue() for w in workers]
		
		for i, worker in enumerate(workers):
			print("Starting worker {}".format(i))
			worker.start()

		[w.join() for w in workers]
		
		print("Training")
		self.train_fn(*self.mem.get_history())
		print("Done")
		
			
		
	