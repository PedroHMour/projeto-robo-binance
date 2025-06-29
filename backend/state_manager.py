import json
import os
import logging

def save_state(state_data, file_path):
    """Salva o dicionário de estado em um arquivo JSON."""
    try:
        with open(file_path, 'w') as f:
            json.dump(state_data, f, indent=4)
        logging.info(f"Estado salvo com sucesso em {file_path}: {state_data}")
    except IOError as e:
        logging.error(f"Não foi possível salvar o estado em {file_path}: {e}")

def load_state(file_path):
    """
    Carrega o dicionário de estado de um arquivo JSON.
    Se o arquivo não existir, cria um estado inicial padrão.
    """
    if not os.path.exists(file_path):
        logging.warning(f"Arquivo de estado '{file_path}' não encontrado. Criando um novo com estado inicial.")
        initial_state = {'in_position': False}
        save_state(initial_state, file_path)
        return initial_state
    
    try:
        with open(file_path, 'r') as f:
            state = json.load(f)
            logging.info(f"Estado carregado com sucesso de {file_path}: {state}")
            return state
    except (IOError, json.JSONDecodeError) as e:
        logging.error(f"Erro ao carregar ou decodificar o arquivo de estado '{file_path}': {e}. Usando estado padrão.")
        return {'in_position': False}