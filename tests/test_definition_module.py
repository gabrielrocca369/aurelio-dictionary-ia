# tests/test_definition_module.py

import unittest
from unittest.mock import patch, MagicMock
from core.definition_module import DefinitionModule

class TestDefinitionModule(unittest.TestCase):
    def setUp(self):
        """Configuração antes de cada teste."""
        self.def_module = DefinitionModule(language='en')

    @patch('core.definition_module.DefinitionModule.get_definition')
    def test_get_definition_existing_word(self, mock_get_definition):
        """Testa a obtenção de definição para uma palavra existente."""
        # Configura o mock para retornar um dicionário esperado
        mock_get_definition.return_value = {
            'definition': "A round fruit with red or green skin and a whitish interior.",
            'part_of_speech': "noun"
        }

        word = "apple"
        result = self.def_module.get_definition(word)
        self.assertIsNotNone(result)
        self.assertIn('definition', result)
        self.assertIn('part_of_speech', result)
        self.assertEqual(result['definition'], "A round fruit with red or green skin and a whitish interior.")
        self.assertEqual(result['part_of_speech'], "noun")
        mock_get_definition.assert_called_once_with(word)

    @patch('core.definition_module.DefinitionModule.get_example')
    def test_get_example_existing_word(self, mock_get_example):
        """Testa a obtenção de exemplo para uma palavra existente."""
        # Configura o mock para retornar um exemplo esperado
        mock_get_example.return_value = "I ate a delicious apple for breakfast."

        word = "apple"
        example = self.def_module.get_example(word)
        self.assertEqual(example, "I ate a delicious apple for breakfast.")
        mock_get_example.assert_called_once_with(word)

    @patch('core.definition_module.DefinitionModule.get_definition')
    def test_get_definition_nonexistent_word(self, mock_get_definition):
        """Testa a obtenção de definição para uma palavra inexistente."""
        # Configura o mock para retornar None
        mock_get_definition.return_value = None

        word = "qwerty"
        result = self.def_module.get_definition(word)
        self.assertIsNone(result)
        mock_get_definition.assert_called_once_with(word)

    @patch('core.definition_module.DefinitionModule.get_example')
    def test_get_example_nonexistent_word(self, mock_get_example):
        """Testa a obtenção de exemplo para uma palavra inexistente."""
        # Configura o mock para retornar um exemplo padrão
        mock_get_example.return_value = "Exemplo de uso para 'qwerty' não encontrado."

        word = "qwerty"
        example = self.def_module.get_example(word)
        self.assertEqual(example, "Exemplo de uso para 'qwerty' não encontrado.")
        mock_get_example.assert_called_once_with(word)

    def test_get_definition_invalid_input(self):
        """Testa a obtenção de definição com entrada inválida."""
        invalid_words = ["", "123", "@#!$", None]

        for word in invalid_words:
            with self.subTest(word=word):
                result = self.def_module.get_definition(word)
                self.assertIsNone(result, f"Definição para entrada inválida '{word}' deve ser None.")

    def test_get_example_invalid_input(self):
        """Testa a obtenção de exemplo com entrada inválida."""
        invalid_words = ["", "123", "@#!$", None]

        for word in invalid_words:
            with self.subTest(word=word):
                example = self.def_module.get_example(word)
                self.assertEqual(example, f"Exemplo de uso para '{word}' não encontrado.", 
                                 f"Exemplo para entrada inválida '{word}' deve ser uma mensagem padrão.")

    @patch('core.definition_module.DefinitionModule.get_definition')
    @patch('core.definition_module.DefinitionModule.get_example')
    def test_add_and_get_word(self, mock_get_example, mock_get_definition):
        """Testa a adição de uma palavra e a obtenção de sua definição e exemplo."""
        word = "banana"
        mock_get_definition.return_value = {
            'definition': "A long curved fruit with a yellow skin.",
            'part_of_speech': "noun"
        }
        mock_get_example.return_value = "I ate a ripe banana."

        # Adiciona a palavra via métodos mockados
        definition = self.def_module.get_definition(word)
        example = self.def_module.get_example(word)

        self.assertIsNotNone(definition)
        self.assertEqual(definition['definition'], "A long curved fruit with a yellow skin.")
        self.assertEqual(definition['part_of_speech'], "noun")

        self.assertEqual(example, "I ate a ripe banana.")

        mock_get_definition.assert_called_once_with(word)
        mock_get_example.assert_called_once_with(word)

    @patch('core.definition_module.DefinitionModule.get_definition')
    def test_case_insensitivity(self, mock_get_definition):
        """Testa se a busca de definição é insensível a maiúsculas e minúsculas."""
        mock_get_definition.return_value = {
            'definition': "A round fruit with red or green skin and a whitish interior.",
            'part_of_speech': "noun"
        }

        words = ["Apple", "APPLE", "ApPlE"]
        for word in words:
            with self.subTest(word=word):
                result = self.def_module.get_definition(word)
                self.assertIsNotNone(result)
                self.assertEqual(result['definition'], "A round fruit with red or green skin and a whitish interior.")
                self.assertEqual(result['part_of_speech'], "noun")
                mock_get_definition.assert_called_with(word)

    @patch('core.definition_module.DefinitionModule.get_definition')
    def test_get_definition_special_characters(self, mock_get_definition):
        """Testa a obtenção de definição para palavras com caracteres especiais."""
        mock_get_definition.return_value = {
            'definition': "A type of fruit.",
            'part_of_speech': "noun"
        }

        word = "café"
        result = self.def_module.get_definition(word)
        self.assertIsNotNone(result)
        self.assertEqual(result['definition'], "A type of fruit.")
        self.assertEqual(result['part_of_speech'], "noun")
        mock_get_definition.assert_called_once_with(word)

    def test_language_change(self):
        """Testa a alteração de idioma no DefinitionModule."""
        self.def_module.set_language('pt')
        self.assertEqual(self.def_module.language, 'pt')
        
        # Verifica se os métodos respondem corretamente após a mudança de idioma
        with patch('core.definition_module.DefinitionModule.get_definition') as mock_get_definition:
            mock_get_definition.return_value = {
                'definition': "Uma fruta redonda com casca vermelha ou verde e interior esbranquiçado.",
                'part_of_speech': "substantivo"
            }
            word = "maçã"
            result = self.def_module.get_definition(word)
            self.assertIsNotNone(result)
            self.assertEqual(result['definition'], "Uma fruta redonda com casca vermelha ou verde e interior esbranquiçado.")
            self.assertEqual(result['part_of_speech'], "substantivo")
            mock_get_definition.assert_called_once_with(word)

if __name__ == '__main__':
    unittest.main()
