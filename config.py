board_config = {
	'board_n': 15,
	'win': 5
}

game_config = {
	'show': True
}

mcts_config = {
	'temperature_step': 40
}

mcts_player_config = {
	'rollout_times': 400
}

pvn_config = {
	'epochs': 30,
	'batch_size': 512,
	'model_filename': "first_model_" + str(board_config['board_n']) + '_' +str(board_config['win']) + '.h5'
}

train_config = {
	'train_samples': 50,
	'buff_max_sz': -1,
}

server_config = {
	'game_num': 100,
	'worker_n': 20,
	'worker_play_n': 5
}

memory_config = {
	'game_id': 0,
	'save_path': 'selfplaydata/'
}