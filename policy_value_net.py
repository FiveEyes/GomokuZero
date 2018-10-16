from keras.layers import Conv2D, Dense, Flatten, Add, Activation, BatchNormalization
from keras.engine.topology import Input
from keras.engine.training import Model
from keras.regularizers import l2
from keras.optimizers import Adam
from keras.models import load_model

import numpy as np
import keras as ks
import tensorflow as tf
import copy
import os
from threading import Lock

import config

block_sz = 5

def softmax(x):
	m = np.max(x)
	probs = np.exp(x - m)
	probs /= np.sum(probs)
	return probs


def conv_block(input_tensor, kernel_size, filter, l2_const):
	x = input_tensor
	x = Conv2D(filter, kernel_size, padding='same', kernel_regularizer=l2(l2_const),
	kernel_initializer='he_normal')(x)
	x = BatchNormalization()(x)
	out = Activation('relu')(x)
	return out
		
def residula_block(input_tensor, kernel_size, filter, l2_const):
	shortcut = Conv2D(filter, kernel_size = (1,1), padding = 'same',
	kernel_regularizer=l2(l2_const),
	kernel_initializer='he_normal')(input_tensor)
	x = input_tensor
	x = Conv2D(filter, kernel_size, padding='same', 
	kernel_regularizer=l2(l2_const),
	kernel_initializer='he_normal')(x)
	x = BatchNormalization()(x)
	x = Activation('relu')(x)
	
	x = Conv2D(filter, kernel_size, padding='same', 
	kernel_regularizer=l2(l2_const),
	kernel_initializer='he_normal')(x)
	x = BatchNormalization()(x)
	
	x = Add()([x, shortcut])
	out = Activation('relu')(x)
	return out


class PolicyValueNet():
	
	def __init__(self, n = 15, filename=None):
		self.n = n
		self.l2_const = 1e-4
		self.pvnet_fn_lock = Lock()
		if filename != None and os.path.exists(filename):
			self.model = load_model(filename)
		else:
			self.build_model()
		self.model._make_predict_function()	
		self.graph = tf.get_default_graph()
		print(self.model.summary())




	
	
	def build_model(self):
		print("build_model")
		x = net = Input((self.n, self.n, 4))
		
		net = conv_block(net, (3,3), 128, self.l2_const)
		for i in range(block_sz):
			net = residula_block(net, (3,3), 128, self.l2_const)

		policy_net = Conv2D(
			filters=2,
			kernel_size=(1, 1), 
			kernel_regularizer=l2(self.l2_const))(net)
		policy_net = BatchNormalization()(policy_net)
		policy_net = Activation('relu')(policy_net)
		policy_net = Flatten()(policy_net)
		self.policy_net = Dense(
			self.n*self.n, 
			activation="softmax", 
			kernel_regularizer=l2(self.l2_const))(policy_net)

		value_net = Conv2D(
			filters=1, 
			kernel_size=(1, 1), 
			kernel_regularizer=l2(self.l2_const))(net)
		value_net = BatchNormalization()(value_net)
		value_net = Activation('relu')(value_net)
		value_net = Flatten()(value_net)
		value_net = Dense(256,
			activation='relu',
			kernel_regularizer=l2(self.l2_const))(value_net)
		self.value_net = Dense(1, 
			activation="tanh", 
			kernel_regularizer=l2(self.l2_const))(value_net)
		
		self.model = Model(x, [self.policy_net, self.value_net])
		
		
		print(self.model.summary())
		

	def get_train_fn(self):
		losses = ['categorical_crossentropy', 'mean_squared_error']
		self.model.compile(optimizer=Adam(lr=0.002), loss=losses)
		batch_size = config.pvn_config['batch_size']
		epochs = config.pvn_config['epochs']
		def train_fn(board, policy, value):
			with self.graph.as_default():
				history = self.model.fit(np.asarray(board), [np.asarray(policy), np.asarray(value)], batch_size=batch_size, epochs=epochs, verbose=0)
			print("train history:", history.history)
		return train_fn
		
	def get_pvnet_fn(self, single = True):
		def pvnet_fn(board):
			nparr_board = board.get_board()
			self.pvnet_fn_lock.acquire()
			with self.graph.as_default():
				probs, value = self.model.predict(nparr_board.reshape(1, self.n, self.n, 4))
			self.pvnet_fn_lock.release()
			policy_move = nparr_board[:,:,0].reshape(self.n * self.n).nonzero()[0]
			policy_probs = probs[0][policy_move]
			
			return (policy_move, policy_probs), value[0][0]
		
		def pvnet_fn_m(boards):
			nparr_boards = np.asarray([b.get_board().reshape(self.n, self.n, 4) for b in boards])
			with self.graph.as_default():
				probs, value = self.model.predict(nparr_boards)
			
			policy_moves = [ b[:,:,0].reshape(self.n * self.n).nonzero()[0] for b in nparr_boards]
			policy_probs = [ p[policy_moves[i]] for i, p in enumerate(probs)]
			return zip(policy_moves, policy_probs, value.ravel())
		return pvnet_fn if single else pvnet_fn_m
		

		
#	def get_policy_param(self):
#		net_params = self.model.get_weights()
#		return net_params
	def save_model(self, model_file):
		if os.path.exists(model_file):
			os.remove(model_file)
		self.model.save(model_file)
#       """ save model params to file """
#       net_params = self.get_policy_param()
#       pickle.dump(net_params, open(model_file, 'wb'), protocol=2)
		
		