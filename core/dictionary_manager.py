# core/dictionary_manager.py

import json
import os
import logging
import requests
import shutil
from datetime import datetime
from typing import Tuple, Optional, Dict, Any
from .confidence_module import ConfidenceModule  # Importação absoluta
import csv

class DictionaryManager:
    """
    Classe responsável por gerenciar a adição de novas palavras ao dicionário.
    Inclui funcionalidades para buscar definições via API, adicionar palavras manualmente,
    salvar e carregar dados do dicionário e dos idiomas, além de validar a integridade dos dados.
    """

    def __init__(
        self,
        dictionary_path: str = 'data/dictionary_data.json',
        language_data_path: str = 'data/language_data.json',
        export_csv_path: str = 'data/export/dictionary_export.csv'
    ):
        """
        Inicializa o DictionaryManager com os caminhos dos arquivos de dados.
        
        Parâmetros:
        - dictionary_path (str): Caminho para o arquivo JSON do dicionário.
        - language_data_path (str): Caminho para o arquivo JSON dos dados de idiomas.
        - export_csv_path (str): Caminho para o arquivo CSV de exportação.
        """
        self.dictionary_path = dictionary_path
        self.language_data_path = language_data_path
        self.export_csv_path = export_csv_path
        self.logger = logging.getLogger(self.__class__.__name__)
        self.confidence_module = ConfidenceModule()
        self.ensure_files_exist()
        self.load_data()

    def ensure_files_exist(self) -> None:
        """
        Garante que os arquivos de dados existam.
        Se não existirem, cria-os com conteúdo padrão.
        Também garante que o diretório de exportação exista.
        """
        # Verificar e criar dictionary_data.json
        if not os.path.exists(self.dictionary_path):
            try:
                with open(self.dictionary_path, 'w', encoding='utf-8') as file:
                    json.dump({}, file, ensure_ascii=False, indent=4)
                self.logger.info(f"Arquivo '{self.dictionary_path}' criado com conteúdo padrão.")
            except Exception as e:
                self.logger.error(f"Erro ao criar '{self.dictionary_path}': {e}")
        
        # Verificar e criar language_data.json
        if not os.path.exists(self.language_data_path):
            default_languages = {
                "en": {
                    "name": "English",
                    "code": "en-US",
                    "gtts_code": "en"
                },
                "pt": {
                    "name": "Português",
                    "code": "pt-BR",
                    "gtts_code": "pt"
                },
                "es": {
                    "name": "Español",
                    "code": "es-ES",
                    "gtts_code": "es"
                },
                "fr": {
                    "name": "Français",
                    "code": "fr-FR",
                    "gtts_code": "fr"
                }
            }
            try:
                with open(self.language_data_path, 'w', encoding='utf-8') as file:
                    json.dump(default_languages, file, ensure_ascii=False, indent=4)
                self.logger.info(f"Arquivo '{self.language_data_path}' criado com idiomas padrão.")
            except Exception as e:
                self.logger.error(f"Erro ao criar '{self.language_data_path}': {e}")

        # Verificar e criar a pasta de exportação se não existir
        export_dir = os.path.dirname(self.export_csv_path)
        if not os.path.exists(export_dir):
            try:
                os.makedirs(export_dir)
                self.logger.info(f"Diretório de exportação '{export_dir}' criado com sucesso.")
            except Exception as e:
                self.logger.error(f"Erro ao criar diretório de exportação '{export_dir}': {e}")

    def load_data(self) -> None:
        """
        Carrega os dados do dicionário e dos idiomas a partir dos arquivos JSON.
        Se ocorrer algum erro durante o carregamento, os dados são inicializados como vazios.
        """
        try:
            with open(self.dictionary_path, 'r', encoding='utf-8') as file:
                self.dictionary = json.load(file)
            with open(self.language_data_path, 'r', encoding='utf-8') as file:
                self.language_data = json.load(file)
            self.logger.info("Dados do dicionário e idiomas carregados com sucesso.")
        except FileNotFoundError as e:
            self.logger.error(f"Arquivo não encontrado durante o carregamento: {e}")
            self.dictionary = {}
            self.language_data = {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao decodificar JSON durante o carregamento: {e}")
            self.dictionary = {}
            self.language_data = {}
        except Exception as e:
            self.logger.error(f"Erro desconhecido durante o carregamento dos dados: {e}")
            self.dictionary = {}
            self.language_data = {}

    def save_data(self) -> bool:
        """
        Salva os dados atualizados do dicionário e dos idiomas nos arquivos JSON.
        Antes de salvar, cria backups dos arquivos atuais.
        Após salvar, valida os arquivos JSON.
        
        Retorna:
        - bool: True se salvo com sucesso, False caso contrário.
        """
        try:
            # Criação de backups com timestamp
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            backup_dict_path = f"{self.dictionary_path}.backup.{timestamp}"
            backup_lang_path = f"{self.language_data_path}.backup.{timestamp}"
            
            shutil.copy(self.dictionary_path, backup_dict_path)
            shutil.copy(self.language_data_path, backup_lang_path)
            self.logger.info(f"Backups criados: '{backup_dict_path}', '{backup_lang_path}'.")
    
            # Salvando os dados atualizados
            with open(self.dictionary_path, 'w', encoding='utf-8') as file:
                json.dump(self.dictionary, file, ensure_ascii=False, indent=4)
            with open(self.language_data_path, 'w', encoding='utf-8') as file:
                json.dump(self.language_data, file, ensure_ascii=False, indent=4)
            self.logger.info("Dados do dicionário e idiomas salvos com sucesso.")
    
            # Validação pós-salvamento
            if self.validate_json(self.dictionary_path) and self.validate_json(self.language_data_path):
                self.logger.info("Validação dos arquivos JSON concluída com sucesso.")
            else:
                self.logger.error("Validação dos arquivos JSON falhou.")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Erro ao salvar dados: {e}")
            return False

    def validate_json(self, file_path: str) -> bool:
        """
        Valida se o conteúdo do arquivo JSON é válido.
        
        Parâmetros:
        - file_path (str): Caminho para o arquivo JSON a ser validado.
        
        Retorna:
        - bool: True se o JSON for válido, False caso contrário.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                json.load(file)
            self.logger.info(f"Arquivo JSON '{file_path}' é válido.")
            return True
        except json.JSONDecodeError as e:
            self.logger.error(f"Erro ao validar JSON '{file_path}': {e}")
            return False
        except Exception as e:
            self.logger.error(f"Erro desconhecido ao validar JSON '{file_path}': {e}")
            return False

    def fetch_definition_from_api(self, word: str, language: str) -> Optional[Dict[str, Any]]:
        """
        Busca a definição e exemplo de uma palavra usando uma API de dicionário.
        
        Parâmetros:
        - word (str): Palavra para buscar a definição.
        - language (str): Código do idioma (ex: 'en', 'pt').
        
        Retorna:
        - dict: Contendo 'definition', 'part_of_speech' e 'example' se bem-sucedido.
        - None: Se a busca falhar ou os dados não forem encontrados.
        """
        api_url = f"https://api.dictionaryapi.dev/api/v2/entries/{language}/{word}"
        try:
            response = requests.get(api_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    first_entry = data[0]
                    meanings = first_entry.get('meanings', [])
                    if meanings:
                        first_meaning = meanings[0]
                        part_of_speech = first_meaning.get('partOfSpeech', 'N/A')
                        definitions = first_meaning.get('definitions', [])
                        if definitions:
                            first_definition = definitions[0]
                            definition = first_definition.get('definition', 'Definição não disponível.')
                            example = first_definition.get('example', 'Exemplo não disponível.')
                            return {
                                'definition': definition,
                                'part_of_speech': part_of_speech,
                                'example': example
                            }
            self.logger.warning(f"Definição não encontrada para a palavra '{word}' no idioma '{language}'.")
            return None
        except requests.RequestException as e:
            self.logger.error(f"Erro na requisição à API para a palavra '{word}': {e}")
            return None
        except Exception as e:
            self.logger.error(f"Erro inesperado ao buscar definição para '{word}': {e}")
            return None

    def add_word(
        self,
        word: str,
        language: str,
        definition: Optional[str] = None,
        part_of_speech: Optional[str] = None,
        example: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Adiciona uma nova palavra ao dicionário. Tenta buscar a definição via API se necessário.
        
        Parâmetros:
        - word (str): Palavra a ser adicionada.
        - language (str): Código do idioma (ex: 'en', 'pt').
        - definition (str, optional): Definição da palavra.
        - part_of_speech (str, optional): Classe gramatical da palavra.
        - example (str, optional): Exemplo de uso da palavra.
        
        Retorna:
        - tuple: (bool, str) indicando sucesso e mensagem.
        """
        word = word.lower().strip()
        if not word:
            self.logger.warning("Tentativa de adicionar uma palavra vazia.")
            return False, "A palavra não pode estar vazia."

        if language not in self.dictionary:
            self.dictionary[language] = {}
            self.logger.info(f"Idioma '{language}' adicionado ao dicionário.")
    
        if word in self.dictionary[language]:
            self.logger.warning(f"A palavra '{word}' já existe no idioma '{language}'.")
            return False, "Palavra já existe no dicionário."

        if not (definition and part_of_speech and example):
            self.logger.info(f"Buscando definição para a palavra '{word}' via API.")
            fetched_data = self.fetch_definition_from_api(word, language)
            if fetched_data:
                definition = fetched_data['definition']
                part_of_speech = fetched_data['part_of_speech']
                example = fetched_data['example']
            else:
                self.logger.warning(f"Definição e exemplo não encontrados para '{word}'. Necessário adicionar manualmente.")
                return False, "Definição e exemplo não encontrados na API. Por favor, forneça manualmente."

        # Adiciona a palavra ao dicionário
        self.dictionary[language][word] = {
            'definition': definition.strip(),
            'part_of_speech': part_of_speech.strip(),
            'example': example.strip() if example and isinstance(example, str) else ""
        }
        self.logger.info(f"Palavra '{word}' adicionada ao idioma '{language}' com sucesso.")
        self.save_data()
        
        # Atualizar o arquivo de exportação
        self.export_dictionary_to_csv(language, self.export_csv_path)
        self.logger.info(f"Arquivo de exportação '{self.export_csv_path}' atualizado após adicionar '{word}'.")
        return True, "Palavra adicionada com sucesso."

    def manual_add_word(
        self,
        word: str,
        language: str,
        definition: str,
        part_of_speech: str,
        example: str
    ) -> Tuple[bool, str]:
        """
        Adiciona uma palavra manualmente sem usar a API.
        
        Parâmetros:
        - word (str): Palavra a ser adicionada.
        - language (str): Código do idioma.
        - definition (str): Definição da palavra.
        - part_of_speech (str): Classe gramatical da palavra.
        - example (str): Exemplo de uso da palavra.
        
        Retorna:
        - tuple: (bool, str) indicando sucesso e mensagem.
        """
        word = word.lower().strip()
        if not word:
            self.logger.warning("Tentativa de adicionar uma palavra vazia manualmente.")
            return False, "A palavra não pode estar vazia."

        if language not in self.dictionary:
            self.dictionary[language] = {}
            self.logger.info(f"Idioma '{language}' adicionado ao dicionário.")

        if word in self.dictionary[language]:
            self.logger.warning(f"A palavra '{word}' já existe no idioma '{language}'.")
            return False, "Palavra já existe no dicionário."

        if not (definition and part_of_speech and example):
            self.logger.warning("Definição, classe gramatical ou exemplo ausente durante a adição manual.")
            return False, "Definição, classe gramatical e exemplo são obrigatórios."

        # Adiciona a palavra ao dicionário
        self.dictionary[language][word] = {
            'definition': definition.strip(),
            'part_of_speech': part_of_speech.strip(),
            'example': example.strip()
        }
        self.logger.info(f"Palavra '{word}' adicionada manualmente ao idioma '{language}' com sucesso.")
        self.save_data()
        
        # Atualizar o arquivo de exportação
        self.export_dictionary_to_csv(language, self.export_csv_path)
        self.logger.info(f"Arquivo de exportação '{self.export_csv_path}' atualizado após adicionar '{word}' manualmente.")
        return True, "Palavra adicionada com sucesso."

    def get_definition(self, word: str, language: str) -> Optional[Dict[str, Any]]:
        """
        Obtém a definição de uma palavra para um idioma específico.
        
        Parâmetros:
        - word (str): Palavra a ser buscada.
        - language (str): Código do idioma.
        
        Retorna:
        - dict: Contendo 'definition', 'part_of_speech', 'example' se a palavra existir.
        - None: Se a palavra não existir no dicionário.
        """
        word = word.lower().strip()
        if language in self.dictionary and word in self.dictionary[language]:
            self.logger.info(f"Definição encontrada para a palavra '{word}' no idioma '{language}'.")
            return self.dictionary[language][word]
        else:
            self.logger.info(f"A palavra '{word}' não foi encontrada no idioma '{language}'.")
            return None

    def set_language(self, language: str) -> bool:
        """
        Altera o idioma principal do dicionário.
        
        Parâmetros:
        - language (str): Código do idioma.
        
        Retorna:
        - bool: True se o idioma foi alterado com sucesso, False caso contrário.
        """
        language = language.lower().strip()
        if language in self.language_data:
            self.logger.info(f"Idioma atual definido para '{language}'.")
            return True
        else:
            self.logger.warning(f"Tentativa de definir idioma inexistente '{language}'.")
            return False

    def remove_word(self, word: str, language: str) -> Tuple[bool, str]:
        """
        Remove uma palavra do dicionário.
        
        Parâmetros:
        - word (str): Palavra a ser removida.
        - language (str): Código do idioma.
        
        Retorna:
        - tuple: (bool, str) indicando sucesso e mensagem.
        """
        word = word.lower().strip()
        if language in self.dictionary and word in self.dictionary[language]:
            del self.dictionary[language][word]
            self.save_data()
            self.logger.info(f"Palavra '{word}' removida do idioma '{language}'.")
            
            # Atualizar o arquivo de exportação
            self.export_dictionary_to_csv(language, self.export_csv_path)
            self.logger.info(f"Arquivo de exportação '{self.export_csv_path}' atualizado após remover '{word}'.")
            return True, "Palavra removida com sucesso."
        else:
            self.logger.warning(f"Tentativa de remover palavra inexistente '{word}' no idioma '{language}'.")
            return False, "Palavra não encontrada no dicionário."

    def list_words(self, language: str) -> Optional[list]:
        """
        Lista todas as palavras disponíveis em um idioma específico.
        
        Parâmetros:
        - language (str): Código do idioma.
        
        Retorna:
        - list: Lista de palavras.
        - None: Se o idioma não existir.
        """
        language = language.lower().strip()
        if language in self.dictionary:
            words = sorted(list(self.dictionary[language].keys()))
            self.logger.info(f"Listando {len(words)} palavras no idioma '{language}'.")
            return words
        else:
            self.logger.warning(f"Tentativa de listar palavras para idioma inexistente '{language}'.")
            return None

    def export_dictionary_to_csv(self, language: str, csv_path: Optional[str] = None) -> bool:
        """
        Exporta o dicionário para um arquivo CSV.
        Atualiza o arquivo de exportação sempre que uma palavra é adicionada ou removida.
        
        Parâmetros:
        - language (str): Código do idioma.
        - csv_path (str, optional): Caminho para o arquivo CSV de saída. Se None, usa o caminho padrão.
        
        Retorna:
        - bool: True se exportado com sucesso, False caso contrário.
        """
        if not csv_path:
            csv_path = self.export_csv_path

        language = language.lower().strip()
        if language not in self.dictionary:
            self.logger.warning(f"Idioma '{language}' não encontrado. Exportação abortada.")
            return False

        try:
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['word', 'definition', 'part_of_speech', 'example']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for word, details in self.dictionary[language].items():
                    writer.writerow({
                        'word': word,
                        'definition': details.get('definition', ''),
                        'part_of_speech': details.get('part_of_speech', ''),
                        'example': details.get('example', '')
                    })
            self.logger.info(f"Dicionário exportado com sucesso para '{csv_path}'.")
            return True
        except Exception as e:
            self.logger.error(f"Erro ao exportar dicionário para CSV: {e}")
            return False

    def import_dictionary_from_csv(self, csv_path: str, language: str) -> Tuple[bool, str]:
        """
        Importa palavras de um arquivo CSV para o dicionário.
        Evita adicionar duplicatas e pode atualizar definições existentes conforme necessário.
        
        Parâmetros:
        - csv_path (str): Caminho para o arquivo CSV de entrada.
        - language (str): Código do idioma.
        
        Retorna:
        - tuple: (bool, str) indicando sucesso e mensagem.
        """
        if not os.path.exists(csv_path):
            self.logger.warning(f"Arquivo CSV '{csv_path}' não encontrado. Importação abortada.")
            return False, "Arquivo CSV não encontrado."
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                count_added = 0
                count_skipped = 0
                for row in reader:
                    word = row.get('word', '').lower().strip()
                    definition = row.get('definition', '').strip()
                    part_of_speech = row.get('part_of_speech', '').strip()
                    example = row.get('example', '').strip()
                    
                    if not word or not definition or not part_of_speech:
                        self.logger.warning(f"Entrada incompleta no CSV: {row}. Ignorando.")
                        count_skipped += 1
                        continue
                    
                    language_dict = self.dictionary.setdefault(language.lower(), {})
                    if word not in language_dict:
                        language_dict[word] = {
                            'definition': definition,
                            'part_of_speech': part_of_speech,
                            'example': example
                        }
                        count_added += 1
                        self.logger.debug(f"Palavra '{word}' adicionada ao dicionário.")
                    else:
                        # Opção: Atualizar definição existente ou ignorar
                        # Aqui, optamos por ignorar duplicatas
                        count_skipped += 1
                        self.logger.info(f"Palavra '{word}' já existe no idioma '{language}'. Ignorada durante a importação.")
            self.save_data()
            self.logger.info(f"Dicionário importado com sucesso a partir de '{csv_path}'. {count_added} palavras adicionadas, {count_skipped} palavras ignoradas.")
            # Atualizar o arquivo de exportação após importação
            self.export_dictionary_to_csv(language, self.export_csv_path)
            self.logger.info(f"Arquivo de exportação '{self.export_csv_path}' atualizado após importação.")
            return True, f"Dicionário importado com sucesso. {count_added} palavras adicionadas, {count_skipped} palavras ignoradas."
        except Exception as e:
            self.logger.error(f"Erro ao importar dicionário a partir de CSV: {e}")
            return False, f"Erro ao importar dicionário: {e}"
