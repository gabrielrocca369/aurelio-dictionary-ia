# main.py

import logging
import os
import sys
import tkinter as tk
from tkinter import messagebox
from core.task_manager import TaskManager
from interface.interface_gui import QAInterface

def setup_logging():
    """
    Configura o sistema de logging para gravar logs tanto em arquivo quanto no console.
    """
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)  # Cria o diretório 'logs/' se não existir

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Define o nível de log

    # Formato do log
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Handler para o arquivo de log
    file_handler = logging.FileHandler(os.path.join(log_dir, 'qa_system.log'), encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Handler para o console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logger.info("Logging configurado com sucesso.")

def on_closing(root, logger):
    """
    Função chamada quando a janela principal é fechada.

    Parâmetros:
    - root (tk.Tk): Instância da janela principal do Tkinter.
    - logger (logging.Logger): Instância do logger para registrar o fechamento.
    """
    if messagebox.askokcancel("Sair", "Deseja realmente sair do A.U.R.E.L.I.O.?"):
        logger.info("Encerrando o A.U.R.E.L.I.O.")
        root.destroy()

def check_and_create_directories():
    """
    Verifica e cria os diretórios necessários, como 'assets' para o ícone e 'data' para os arquivos do dicionário.
    """
    required_dirs = ['assets', 'data', 'data/export']
    for directory in required_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logging.info(f"Diretório '{directory}' criado.")

def load_icon(root, logger):
    """
    Carrega o ícone da aplicação, se disponível.
    
    Parâmetros:
    - root (tk.Tk): Instância da janela principal.
    - logger (logging.Logger): Instância do logger para registrar o processo.
    """
    icon_path = os.path.join('assets', 'logo_icon.ico')  # Exemplo de caminho do ícone
    if os.path.exists(icon_path):
        try:
            root.iconbitmap(icon_path)
            logger.info(f"Ícone carregado a partir de '{icon_path}'.")
        except Exception as e:
            logger.warning(f"Falha ao carregar o ícone '{icon_path}': {e}")
    else:
        logger.warning(f"Ícone '{icon_path}' não encontrado. Continuando sem ícone.")

def main():
    """
    Função principal que inicializa e executa o aplicativo A.U.R.E.L.I.O.
    """
    try:
        setup_logging()
        logger = logging.getLogger('Main')
        logger.info("Iniciando o A.U.R.E.L.I.O.")
        
        # Verifica e cria os diretórios necessários
        check_and_create_directories()

        # Cria a janela principal do Tkinter
        root = tk.Tk()
        root.title("A.U.R.E.L.I.O. - Dicionário Multilíngue")
        root.geometry("900x800")  # Define o tamanho da janela
        root.resizable(False, False)  # Desativa o redimensionamento da janela
        root.configure(bg='#1e1e1e')  # Define a cor de fundo
        

        # Carregar o ícone
        load_icon(root, logger)

        # Cria instância do TaskManager
        task_manager = TaskManager()

        # Cria e executa a interface gráfica
        interface = QAInterface(root, task_manager)

        # Configura a função de fechamento da janela
        root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root, logger))

        # Inicia a interface
        interface.run()

    except Exception as e:
        # Log de qualquer exceção não tratada
        logging.getLogger('Main').exception(f"Erro crítico: {e}")
        messagebox.showerror("Erro Crítico", f"Ocorreu um erro crítico: {e}\nO aplicativo será encerrado.")
        sys.exit(1)

if __name__ == "__main__":
    main()
