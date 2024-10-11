# core/confidence_module.py

import logging
from typing import Optional

class ConfidenceModule:
    """Módulo para calcular a confiança das respostas."""

    def __init__(self, high_multiplier: float = 2.0, partial_multiplier: float = 1.5, max_confidence: float = 100.0):
        """
        Inicializa o ConfidenceModule com multiplicadores configuráveis.

        Parâmetros:
        - high_multiplier (float): Multiplicador para definição e exemplo presentes.
        - partial_multiplier (float): Multiplicador para apenas definição ou exemplo presente.
        - max_confidence (float): Valor máximo de confiança.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.high_multiplier = high_multiplier
        self.partial_multiplier = partial_multiplier
        self.max_confidence = max_confidence

    def calculate_confidence(self, definition: Optional[str], example: Optional[str]) -> float:
        """
        Calcula a confiança com base na presença e no comprimento da definição e do exemplo.

        Regras de confiança:
        - Ambos definição e exemplo presentes: confiança alta.
        - Apenas um presente: confiança média.
        - Nenhum presente: confiança baixa.

        Parâmetros:
        - definition (Optional[str]): Definição da palavra.
        - example (Optional[str]): Exemplo de uso da palavra.

        Retorna:
        - float: Valor de confiança calculado, limitado por max_confidence.
        """
        try:
            # Validar e tratar inputs
            if not isinstance(definition, str):
                if definition is not None:
                    self.logger.warning(f"Definição não é uma string: {definition}. Tratando como vazio.")
                definition = "" if definition is None else str(definition)
            if not isinstance(example, str):
                if example is not None:
                    self.logger.warning(f"Exemplo não é uma string: {example}. Tratando como vazio.")
                example = "" if example is None else str(example)
            
            # Contar palavras
            definition_word_count = len(definition.split())
            example_word_count = len(example.split())
            total_word_count = definition_word_count + example_word_count

            if definition and example:
                confidence = min(self.max_confidence, total_word_count * self.high_multiplier)
                self.logger.info(f"Confiança calculada: {confidence:.2f}% (Definição: {definition_word_count} palavras, Exemplo: {example_word_count} palavras).")
            elif definition or example:
                single_word_count = definition_word_count if definition else example_word_count
                confidence = min(self.max_confidence, single_word_count * self.partial_multiplier)
                source = "definição" if definition else "exemplo"
                self.logger.info(f"Confiança calculada: {confidence:.2f}% (Apenas {source}: {single_word_count} palavras).")
            else:
                confidence = 0.0
                self.logger.warning("Definição e exemplo ausentes para calcular confiança.")

            return confidence

        except Exception as e:
            self.logger.error(f"Erro ao calcular confiança: {e}")
            return 0.0
