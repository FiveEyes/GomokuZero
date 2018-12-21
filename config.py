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
    'rollout_times': 1600,
}

pvn_config = {
    'epochs': 15,
    'batch_size': 512,
    'model_filename': "first_model_" + str(board_config['board_n']) + '_' +str(board_config['win']) + '.pt',
}

train_config = {
    #'train_samples': 50,
    'buff_max_sz': 200000,
}

server_config = {
    'game_num': 100,
    'worker_n': 24,
    'playbook': [
        [112, 128, 126],
        [112, 97, 96],
        #[112, 97, 96, 128, 80, 64, 110, 111, 124, 138, 125, 95, 126, 127, 79, 78, 122, 123, 108, 143, 159, 94, 140, 98, 92, 76, 156],
        #[112, 98, 114, 113, 128, 142, 144, 160, 129, 99, 127, 126, 130, 131, 158, 172, 100, 174],
        #[112, 98, 114, 113, 128, 142, 144, 160, 129, 99, 127, 126, 130, 131, 158, 172, 100, 174, 116, 102, 115, 85, 132, 84, 148, 164, 146, 117, 145, 147, 162, 178, 176, 57, 71, 87, 72, 86, 83, 88],
        #[112, 98, 114, 113, 128, 142, 144, 160, 129, 99, 127, 126, 130, 131, 158, 172, 100, 174, 87],
        
    ],
}

memory_config = {
    'game_id': 0,
    'save_path': 'selfplaydata/',
}

