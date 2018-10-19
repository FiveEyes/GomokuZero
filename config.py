board_config = {
	'board_n': 15,
	'win': 5
}

game_config = {
	'show': True
}

mcts_config = {
	'temperature_step': 20
}

mcts_player_config = {
	'dirichlet_eps': 0.25,
	'rollout_times': 1200
}

pvn_config = {
	'epochs': 20,
	'batch_size': 512,
	'model_filename': "second_model_" + str(board_config['board_n']) + '_' +str(board_config['win']) + '.h5'
}

train_config = {
	'train_samples': 50,
	'buff_max_sz': -1,
}

server_config = {
	'game_num': 100,
	'worker_n': 20,
	'best_player': True
}

memory_config = {
	'game_id': 400,
	'save_path': 'selfplaydata/'
}