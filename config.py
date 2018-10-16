board_config = {
	'board_n': 15,
	'win': 5
}

game_config = {
	'show': True
}

mcts_config = {
	'temperature_step': 400
}

mcts_player_config = {
	'rollout_times': 10
}

pvn_config = {
	'epochs': 30,
	'batch_size': 512,
	'model_filename': "first_model_" + str(board_config['board_n']) + '_' +str(board_config['win']) + '.h5'
}

train_config = {
	'train_samples': 50,
	'buff_max_sz': 100000,
}

server_config = {
	'worker_n': 20,
	'worker_play_n': 5
}