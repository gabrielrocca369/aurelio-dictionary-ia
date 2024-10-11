# core/task_manager.py

import logging
from typing import Tuple
from .definition_module import DefinitionModule
from .confidence_module import ConfidenceModule
from .speech_module import SpeechModule
from .dictionary_manager import DictionaryManager

class TaskManager:
    """
    Gerenciador de tarefas que coordena os módulos principais.
    
    Responsabilidades:
    - Gerenciar a importação e exportação de palavras.
    - Processar perguntas do usuário e fornecer respostas estruturadas.
    - Integrar funcionalidades de reconhecimento e síntese de voz.
    """

    def __init__(
        self,
        language: str = 'en',
        dictionary_path: str = 'data/dictionary_data.json',
        language_data_path: str = 'data/language_data.json',
        export_csv_path: str = 'data/export/dictionary_export.csv'
    ):
        """
        Inicializa o TaskManager com os módulos necessários.

        Parâmetros:
        - language (str): Código do idioma inicial (ex: 'en', 'pt').
        - dictionary_path (str): Caminho para o arquivo JSON do dicionário.
        - language_data_path (str): Caminho para o arquivo JSON dos dados de idiomas.
        - export_csv_path (str): Caminho para o arquivo CSV de exportação.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("Inicializando TaskManager.")

        # Inicialização dos módulos
        self.dictionary_manager = DictionaryManager(
            dictionary_path=dictionary_path,
            language_data_path=language_data_path,
            export_csv_path=export_csv_path
        )
        self.definition_module = DefinitionModule(
            language=language,
            dictionary_path=dictionary_path,
            language_data_path=language_data_path
        )
        self.confidence_module = ConfidenceModule()
        self.speech_module = SpeechModule(language=language)
        
        self.language = language
        self.logger.info("TaskManager inicializado com sucesso.")

    def set_language(self, language: str) -> bool:
        """
        Define o idioma para todos os módulos e recarrega os dados necessários.

        Parâmetros:
        - language (str): Código do idioma (ex: 'en', 'pt').

        Retorna:
        - bool: True se o idioma foi definido com sucesso, False caso contrário.
        """
        self.logger.info(f"Tentando definir o idioma para '{language}'.")
        success = self.dictionary_manager.set_language(language)
        if not success:
            self.logger.error(f"Falha ao definir o idioma para '{language}'.")
            return False

        self.language = language
        self.definition_module.set_language(language)
        self.speech_module.set_language(language)
        self.logger.info(f"Idioma definido para '{language}' com sucesso.")
        return True

    def process_question(self, word: str) -> dict:
        """
        Processa a palavra consultada e retorna resposta estruturada.

        Parâmetros:
        - word (str): Palavra a ser processada.

        Retorna:
        - dict: Contendo 'definition', 'part_of_speech', 'example' e 'confidence' se a palavra existir.
        - dict: Contendo 'error' se a palavra não for encontrada.
        """
        self.logger.info(f"Processando a palavra: '{word}' no idioma '{self.language}'.")
        definition_data = self.dictionary_manager.get_definition(word, self.language)
        
        if not definition_data:
            self.logger.warning(f"Palavra '{word}' não encontrada no dicionário.")
            return {"error": f"Palavra '{word}' não encontrada no dicionário."}
        
        definition = definition_data.get('definition', 'Definição não disponível.')
        part_of_speech = definition_data.get('part_of_speech', 'N/A')
        example = definition_data.get('example', 'Exemplo não disponível.')
        confidence = self.confidence_module.calculate_confidence(definition, example)
        
        self.logger.debug(f"Confiança calculada para '{word}': {confidence:.2f}%.")
        
        return {
            "definition": definition,
            "part_of_speech": part_of_speech,
            "example": example,
            "confidence": confidence
        }

    def listen_and_respond(self):
        """
        Captura a fala do usuário, processa e responde com áudio.
        """
        self.logger.info("Iniciando reconhecimento de fala.")
        word = self.speech_module.recognize_speech()
        if word:
            self.logger.info(f"Palavra reconhecida: '{word}'. Processando...")
            result = self.process_question(word)
            if 'error' in result:
                self.logger.info(f"Respondendo com erro: {result['error']}")
                self.speech_module.speak(result['error'])
            else:
                response_text = (
                    f"Definição: {result['definition']}. "
                    f"Exemplo: {result['example']}. "
                    f"Confiança: {result['confidence']:.2f} por cento."
                )
                self.logger.info(f"Respondendo: {response_text}")
                self.speech_module.speak(response_text)
        else:
            self.logger.warning("Nenhuma palavra foi reconhecida.")

    def export_dictionary(self, language: str, csv_path: str = None) -> Tuple[bool, str]:
        """
        Exporta o dicionário para um arquivo CSV.

        Parâmetros:
        - language (str): Código do idioma (ex: 'en', 'pt').
        - csv_path (str, optional): Caminho para o arquivo CSV de saída. Se None, usa o caminho padrão.

        Retorna:
        - tuple: (bool, str) indicando sucesso e mensagem.
        """
        self.logger.info(f"Exportando dicionário para CSV. Idioma: '{language}'.")
        success = self.dictionary_manager.export_dictionary_to_csv(language, csv_path)
        if success:
            export_path = csv_path if csv_path else self.dictionary_manager.export_csv_path
            self.logger.info(f"Dicionário exportado com sucesso para '{export_path}'.")
            return True, f"Dicionário exportado com sucesso para '{export_path}'."
        else:
            self.logger.error("Falha na exportação do dicionário para CSV.")
            return False, "Falha na exportação do dicionário para CSV."

    def import_dictionary(self, csv_path: str, language: str) -> Tuple[bool, str]:
        """
        Importa palavras de um arquivo CSV para o dicionário.

        Parâmetros:
        - csv_path (str): Caminho para o arquivo CSV de entrada.
        - language (str): Código do idioma (ex: 'en', 'pt').

        Retorna:
        - tuple: (bool, str) indicando sucesso e mensagem.
        """
        self.logger.info(f"Importando dicionário a partir de '{csv_path}'. Idioma: '{language}'.")
        success, message = self.dictionary_manager.import_dictionary_from_csv(csv_path, language)
        if success:
            self.logger.info(f"Dicionário importado com sucesso a partir de '{csv_path}'.")
        else:
            self.logger.error(f"Falha ao importar dicionário a partir de '{csv_path}': {message}")
        return success, message
