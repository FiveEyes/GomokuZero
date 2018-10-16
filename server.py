import config
from memory import decode_board, decode_policy, gen_mirrors, gen_rotations
from threading import Lock
from worker import Worker
from queue import Queue
import config
class Server(object):
	def __init__(self, pvnet):
		self.buff_max_sz = config.train_config['buff_max_sz']
		self.pvnet = pvnet
		self.train_fn = pvnet.get_train_fn()
		#self.push_lock = Lock()
		self.worker_n = config.server_config['worker_n']
		self.worker_play_n = config.server_config['worker_play_n']
		self.bhb = []
		self.phb = []
		self.vhb = []
		self.bpv_queue = Queue()
		return
	def get_pvnet(self):
		return self.pvnet
		
	def push_history_queue(self, bh, ph, vh):
		self.bpv_queue.put((bh, ph, vh))

	def push_history(self, bh, ph, vh):
		#self.push_lock.acquire()
		if len(self.vhb) >= self.buff_max_sz:
			self.bhb = self.bhb[len(self.vhb)//2:]
			self.phb = self.phb[len(self.vhb)//2:]
			self.vhb = self.vhb[len(self.vhb)//2:]
		bh = decode_board(bh)
		ph = [decode_policy(policy) for policy in ph]
		print("match size:", len(bh))
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
		print("buff size:", len(self.bhb))
		#self.push_lock.release()

	def train(self):
		workers = [ Worker(i, self.worker_play_n, self) for i in range(self.worker_n)]
		for i, worker in enumerate(workers):
			print("Starting worker {}".format(i))
			worker.start()
		[w.join() for w in workers]
		while not self.bpv_queue.empty():
			bh, ph, vh = self.bpv_queue.get()
			self.push_history(bh, ph, vh)
		print("Training")
		self.train_fn(self.bhb, self.phb, self.vhb)
		print("Done")
		
			
		
	