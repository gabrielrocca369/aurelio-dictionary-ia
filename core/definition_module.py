# core/definition_module.py

import json
import os
import logging
from typing import Optional, Dict, Any

class DefinitionModule:
    """Módulo para buscar definições e exemplos no dicionário."""

    def __init__(
        self,
        language: str = 'en',
        dictionary_path: str = 'data/dictionary_data.json',
        language_data_path: str = 'data/language_data.json'
    ):
        """
        Inicializa o DefinitionModule com o idioma especificado e caminhos para os dados.

        Parâmetros:
        - language (str): Código do idioma (por exemplo, 'en', 'pt').
        - dictionary_path (str): Caminho para o arquivo JSON do dicionário.
        - language_data_path (str): Caminho para o arquivo JSON dos dados de idiomas.
        """
        self.language = language
        self.dictionary_path = dictionary_path
        self.language_data_path = language_data_path
        
        # Inicializa o logger antes de chamar métodos que o utilizam
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Inicializando DefinitionModule.")
        
        self.dictionary: Dict[str, Dict[str, Any]] = {}
        self.language_data: Dict[str, Any] = {}
        
        self.load_language_data()
        self.load_dictionary()

    def load_dictionary(self) -> None:
        """
        Carrega o dicionário a partir do arquivo JSON.

        Se o arquivo não for encontrado ou contiver JSON inválido, o dicionário será vazio.
        """
        try:
            with open(self.dictionary_path, 'r', encoding='utf-8') as file:
                self.dictionary = json.load(file)
            self.logger.info("Dicionário carregado com sucesso.")
        except FileNotFoundError:
            self.logger.error(f"Arquivo {self.dictionary_path} não encontrado. Usando dicionário vazio.")
            self.dictionary = {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar JSON em {self.dictionary_path}: {e}. Usando dicionário vazio.")
            self.dictionary = {}
        except Exception as e:
            self.logger.error(f"Erro inesperado ao carregar o dicionário: {e}. Usando dicionário vazio.")
            self.dictionary = {}

    def load_language_data(self) -> None:
        """
        Carrega os dados dos idiomas a partir do arquivo JSON.

        Se o arquivo não for encontrado ou contiver JSON inválido, os dados de idiomas serão vazios.
        """
        try:
            with open(self.language_data_path, 'r', encoding='utf-8') as file:
                self.language_data = json.load(file)
            self.logger.info("Dados de idiomas carregados com sucesso.")
        except FileNotFoundError:
            self.logger.error(f"Arquivo {self.language_data_path} não encontrado. Dados de idiomas vazios.")
            self.language_data = {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar JSON em {self.language_data_path}: {e}. Dados de idiomas vazios.")
            self.language_data = {}
        except Exception as e:
            self.logger.error(f"Erro inesperado ao carregar os dados de idiomas: {e}. Dados de idiomas vazios.")
            self.language_data = {}

    def set_language(self, language: str) -> None:
        """
        Define o idioma atual e recarrega o dicionário se necessário.

        Parâmetros:
        - language (str): Código do idioma (por exemplo, 'en', 'pt').
        """
        if not isinstance(language, str):
            self.logger.error(f"Idioma inválido: {language}. Deve ser uma string.")
            return

        if language not in self.language_data:
            self.logger.warning(f"Idioma '{language}' não está disponível. Mantendo o idioma atual '{self.language}'.")
            return

        self.language = language
        self.logger.info(f"Idioma definido para '{language}'.")
        self.load_dictionary()

    def get_definition(self, word: str) -> Optional[Dict[str, Any]]:
        """
        Retorna a definição e parte do discurso da palavra.

        Parâmetros:
        - word (str): Palavra para buscar a definição.

        Retorna:
        - Optional[Dict[str, Any]]: Dicionário com 'definition' e 'part_of_speech' se a palavra existir, caso contrário None.
        """
        if not isinstance(word, str) or not word.strip():
            self.logger.warning(f"Entrada inválida para get_definition: {word}")
            return None

        word = word.lower()
        language_dict = self.dictionary.get(self.language, {})
        definition_data = language_dict.get(word)

        if definition_data:
            self.logger.debug(f"Definição encontrada para '{word}' no idioma '{self.language}'.")
        else:
            self.logger.debug(f"Definição para '{word}' não encontrada no idioma '{self.language}'.")
        return definition_data

    def get_example(self, word: str) -> str:
        """
        Retorna um exemplo de uso da palavra.

        Parâmetros:
        - word (str): Palavra para buscar o exemplo.

        Retorna:
        - str: Exemplo de uso ou mensagem padrão se não encontrado.
        """
        if not isinstance(word, str) or not word.strip():
            self.logger.warning(f"Entrada inválida para get_example: {word}")
            return f"Exemplo de uso para '{word}' não encontrado."

        definition_data = self.get_definition(word)
        if definition_data and 'example' in definition_data and definition_data['example'].strip():
            self.logger.debug(f"Exemplo encontrado para '{word}'.")
            return definition_data['example']
        else:
            self.logger.info(f"Exemplo de uso para '{word}' não encontrado.")
            return f"Exemplo de uso para '{word}' não encontrado."

    def reload_dictionary(self) -> None:
        """
        Recarrega o dicionário a partir do arquivo JSON.

        Útil se o arquivo de dicionário for atualizado durante a execução do programa.
        """
        self.logger.info("Recarregando o dicionário.")
        self.load_dictionary()

    def reload_language_data(self) -> None:
        """
        Recarrega os dados dos idiomas a partir do arquivo JSON.

        Útil se os dados de idioma forem atualizados durante a execução do programa.
        """
        self.logger.info("Recarregando os dados de idiomas.")
        self.load_language_data()
        # Após recarregar os dados de idiomas, verifica se o idioma atual ainda é válido
        if self.language not in self.language_data:
            self.logger.warning(f"Idioma atual '{self.language}' não está mais disponível após recarregar dados de idiomas.")
            self.language = next(iter(self.language_data), 'en')  # Define para o primeiro idioma disponível ou 'en'
            self.logger.info(f"Idioma definido para '{self.language}'.")
            self.load_dictionary()

    def add_word(
        self, 
        word: str, 
        definition: str, 
        part_of_speech: str, 
        example: Optional[str] = None
    ) -> bool:
        """
        Adiciona uma nova palavra ao dicionário.

        Parâmetros:
        - word (str): Palavra a ser adicionada.
        - definition (str): Definição da palavra.
        - part_of_speech (str): Classe gramatical da palavra.
        - example (Optional[str]): Exemplo de uso da palavra.

        Retorna:
        - bool: True se a palavra foi adicionada com sucesso, False se já existir ou houver erro.
        """
        if not all(isinstance(arg, str) and arg.strip() for arg in [word, definition, part_of_speech]):
            self.logger.error(
                f"Parâmetros inválidos para adicionar palavra: word='{word}', definition='{definition}', part_of_speech='{part_of_speech}'."
            )
            return False

        word = word.lower()
        language_dict = self.dictionary.setdefault(self.language, {})
        if word in language_dict:
            self.logger.warning(f"Palavra '{word}' já existe no dicionário para o idioma '{self.language}'.")
            return False

        language_dict[word] = {
            'definition': definition.strip(),
            'part_of_speech': part_of_speech.strip(),
            'example': example.strip() if example and isinstance(example, str) else ""
        }
        self.logger.info(f"Palavra '{word}' adicionada com sucesso ao dicionário para o idioma '{self.language}'.")
        self.save_dictionary()
        return True

    def save_dictionary(self) -> bool:
        """
        Salva o dicionário de volta para o arquivo JSON.

        Retorna:
        - bool: True se salvo com sucesso, False em caso de erro.
        """
        try:
            with open(self.dictionary_path, 'w', encoding='utf-8') as file:
                json.dump(self.dictionary, file, ensure_ascii=False, indent=4)
            self.logger.info("Dicionário salvo com sucesso.")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar o dicionário: {e}")
            return False

    def remove_word(self, word: str) -> bool:
        """
        Remove uma palavra do dicionário.

        Parâmetros:
        - word (str): Palavra a ser removida.

        Retorna:
        - bool: True se a palavra foi removida, False se não existir ou houver erro.
        """
        if not isinstance(word, str) or not word.strip():
            self.logger.error(f"Entrada inválida para remover palavra: '{word}'.")
            return False

        word = word.lower()
        language_dict = self.dictionary.get(self.language, {})
        if word not in language_dict:
            self.logger.warning(f"Palavra '{word}' não encontrada no dicionário para o idioma '{self.language}'.")
            return False

        del language_dict[word]
        self.logger.info(f"Palavra '{word}' removida com sucesso do dicionário para o idioma '{self.language}'.")
        self.save_dictionary()
        return True
