board_config = {
	'board_n': 15,
	'win': 5
}

game_config = {
	'show': True
}

mcts_config = {
	'temperature_step': 30,
	'temp_mode': 1,
	'threshold': 0.01,
	'expand_eps': 0.8
}

mcts_player_config = {
	'dirichlet_eps': 0.20,
	'rollout_times': 3200,
}

pvn_config = {
	'epochs': 15,
	'batch_size': 512,
	'model_filename': "first_model_" + str(board_config['board_n']) + '_' +str(board_config['win']) + '.pt',
}

train_config = {
	#'train_samples': 50,
	'buff_max_sz': 120000,
}

server_config = {
	'game_num': 64,
	'worker_n': 24,
}

memory_config = {
	'game_id': 1200,
	'save_path': 'selfplaydata/',
}