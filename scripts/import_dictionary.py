# scripts/import_dictionary.py

import os
from core.dictionary_manager import DictionaryManager

def import_dictionary(csv_path, language):
    """
    Importa palavras de um arquivo CSV para o dicionário.
    
    Parâmetros:
    - csv_path (str): Caminho para o arquivo CSV de entrada.
    - language (str): Código do idioma (ex: 'en', 'pt').
    
    Retorna:
    - bool: True se importado com sucesso, False caso contrário.
    """
    manager = DictionaryManager()
    success, message = manager.import_dictionary_from_csv(csv_path, language)
    if success:
        print(message)
    else:
        print(f"Falha na importação: {message}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Importa palavras de um arquivo CSV para o dicionário.")
    parser.add_argument('csv_path', type=str, help="Caminho para o arquivo CSV de entrada.")
    parser.add_argument('language', type=str, help="Código do idioma (ex: 'en', 'pt').")
    
    args = parser.parse_args()
    import_dictionary(args.csv_path, args.language)
