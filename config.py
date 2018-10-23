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
	'threshold': 0.01
}

mcts_player_config = {
	'dirichlet_eps': 0.1,
	'rollout_times': 2400,
}

pvn_config = {
	'epochs': 20,
	'batch_size': 512,
	'model_filename': "first_model_" + str(board_config['board_n']) + '_' +str(board_config['win']) + '.h5',
}

train_config = {
	#'train_samples': 50,
	'buff_max_sz': 120000,
}

server_config = {
	'game_num': 100,
	'worker_n': 20,
}

memory_config = {
	'game_id': 3000,
	'save_path': 'selfplaydata/',
}