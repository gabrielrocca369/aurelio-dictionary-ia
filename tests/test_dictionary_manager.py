# tests/test_dictionary_manager.py 

import unittest
from unittest.mock import patch
from core.dictionary_manager import DictionaryManager
import os
import json
import csv

class TestDictionaryManager(unittest.TestCase):
    def setUp(self):
        """Configuração antes de cada teste."""
        # Caminhos para os arquivos de teste
        self.test_dict_path = os.path.join('data', 'test_dictionary_data.json')
        self.test_lang_path = os.path.join('data', 'test_language_data.json')
        self.test_export_path = os.path.join('data', 'test_export', 'test_dictionary_export.csv')
        self.test_import_path = os.path.join('data', 'test_import', 'test_import.csv')
        
        # Criar os diretórios 'data/', 'data/test_export/', e 'data/test_import/' se não existirem
        os.makedirs('data/test_export/', exist_ok=True)
        os.makedirs('data/test_import/', exist_ok=True)
        
        # Inicializa o DictionaryManager com caminhos de teste
        self.manager = DictionaryManager(
            dictionary_path=self.test_dict_path, 
            language_data_path=self.test_lang_path,
            export_csv_path=self.test_export_path
        )
        
        # Inicializa com dados vazios e configurações de idioma
        self.manager.dictionary = {}
        self.manager.language_data = {
            "en": {
                "name": "English",
                "code": "en-US",
                "gtts_code": "en"
            }
        }
        self.manager.save_data()

    def tearDown(self):
        """Limpa os arquivos de teste após cada teste."""
        # Remover arquivos de dicionário e idiomas de teste
        if os.path.exists(self.test_dict_path):
            os.remove(self.test_dict_path)
        if os.path.exists(self.test_lang_path):
            os.remove(self.test_lang_path)
        
        # Remover arquivos de exportação de teste
        if os.path.exists(self.test_export_path):
            os.remove(self.test_export_path)
        export_dir = os.path.dirname(self.test_export_path)
        if os.path.exists(export_dir) and not os.listdir(export_dir):
            os.rmdir(export_dir)
        
        # Remover arquivos de importação de teste
        if os.path.exists(self.test_import_path):
            os.remove(self.test_import_path)
        import_dir = os.path.dirname(self.test_import_path)
        if os.path.exists(import_dir) and not os.listdir(import_dir):
            os.rmdir(import_dir)
        
        # Remove backups criados durante os testes
        for file in os.listdir('data'):
            if file.startswith('test_dictionary_data.json.backup'):
                os.remove(os.path.join('data', file))
            if file.startswith('test_language_data.json.backup'):
                os.remove(os.path.join('data', file))
        
        # Remover diretórios de exportação e importação se vazios
        if os.path.exists('data/test_export/') and not os.listdir('data/test_export/'):
            os.rmdir('data/test_export/')
        if os.path.exists('data/test_import/') and not os.listdir('data/test_import/'):
            os.rmdir('data/test_import/')

    @patch('core.dictionary_manager.requests.get')
    def test_add_word_success_api(self, mock_get):
        """Testa a adição de uma palavra com sucesso via API."""
        # Define o comportamento do mock para a resposta da API
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{
            "word": "apple",
            "meanings": [{
                "partOfSpeech": "noun",
                "definitions": [{
                    "definition": "A round fruit with red or green skin and a whitish interior.",
                    "example": "I ate a delicious apple for breakfast."
                }]
            }]
        }]
        mock_get.return_value = mock_response

        success, message = self.manager.add_word("apple", "en")
        self.assertTrue(success)
        self.assertEqual(message, "Palavra adicionada com sucesso.")
        
        # Verifica se a palavra foi adicionada ao dicionário
        with open(self.test_dict_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.assertIn("apple", data["en"])
            self.assertIn("definition", data["en"]["apple"])
            self.assertIn("part_of_speech", data["en"]["apple"])
            self.assertIn("example", data["en"]["apple"])
            self.assertEqual(data["en"]["apple"]["definition"], "A round fruit with red or green skin and a whitish interior.")
            self.assertEqual(data["en"]["apple"]["part_of_speech"], "noun")
            self.assertEqual(data["en"]["apple"]["example"], "I ate a delicious apple for breakfast.")
        
        # Verifica se o arquivo de exportação foi atualizado corretamente
        self.assertTrue(os.path.exists(self.test_export_path))
        with open(self.test_export_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['word'], "apple")
            self.assertEqual(rows[0]['definition'], "A round fruit with red or green skin and a whitish interior.")
            self.assertEqual(rows[0]['part_of_speech'], "noun")
            self.assertEqual(rows[0]['example'], "I ate a delicious apple for breakfast.")

    def test_add_word_existing(self):
        """Testa a adição de uma palavra que já existe."""
        # Adiciona uma palavra manualmente
        self.manager.dictionary = {
            "en": {
                "apple": {
                    "definition": "A fruit",
                    "part_of_speech": "noun",
                    "example": "An apple a day keeps the doctor away."
                }
            }
        }
        self.manager.save_data()
        
        # Tenta adicionar a mesma palavra novamente
        success, message = self.manager.add_word("apple", "en")
        self.assertFalse(success)
        self.assertEqual(message.strip(), "Palavra já existe no dicionário.")
        
        # Verifica que o arquivo de exportação não foi alterado
        self.assertTrue(os.path.exists(self.test_export_path))
        with open(self.test_export_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            # Nenhuma palavra deveria estar exportada ainda, já que nenhuma operação de exportação foi realizada
            self.assertEqual(len(rows), 0)

    @patch('core.dictionary_manager.requests.get')
    def test_add_word_api_failure(self, mock_get):
        """Testa a adição de uma palavra quando a API não retorna dados."""
        # Define o comportamento do mock para a resposta da API
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 404  # Simula uma resposta não encontrada
        mock_get.return_value = mock_response

        success, message = self.manager.add_word("qwerty", "en")
        self.assertFalse(success)
        self.assertEqual(message, "Definição e exemplo não encontrados na API. Por favor, forneça manualmente.")
        
        # Verifica que a palavra não foi adicionada ao dicionário
        with open(self.test_dict_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.assertNotIn("qwerty", data.get("en", {}))
        
        # Verifica que o arquivo de exportação não foi alterado
        self.assertFalse(os.path.exists(self.test_export_path))

    def test_add_word_manual(self):
        """Testa a adição manual de uma palavra sem usar a API."""
        success, message = self.manager.manual_add_word(
            word="book",
            language="en",
            definition="A written or printed work consisting of pages glued or sewn together along one side and bound in covers.",
            part_of_speech="noun",
            example="She read a fascinating book about space exploration."
        )
        self.assertTrue(success)
        self.assertEqual(message, "Palavra adicionada com sucesso.")
        
        # Verifica se a palavra foi adicionada ao dicionário
        with open(self.test_dict_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.assertIn("book", data["en"])
            self.assertEqual(data["en"]["book"]["definition"], "A written or printed work consisting of pages glued or sewn together along one side and bound in covers.")
            self.assertEqual(data["en"]["book"]["part_of_speech"], "noun")
            self.assertEqual(data["en"]["book"]["example"], "She read a fascinating book about space exploration.")
        
        # Verifica se o arquivo de exportação foi atualizado corretamente
        self.assertTrue(os.path.exists(self.test_export_path))
        with open(self.test_export_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['word'], "book")
            self.assertEqual(rows[0]['definition'], "A written or printed work consisting of pages glued or sewn together along one side and bound in covers.")
            self.assertEqual(rows[0]['part_of_speech'], "noun")
            self.assertEqual(rows[0]['example'], "She read a fascinating book about space exploration.")

    def test_remove_word(self):
        """Testa a remoção de uma palavra e atualização do arquivo de exportação."""
        # Adiciona uma palavra manualmente
        self.manager.dictionary = {
            "en": {
                "apple": {
                    "definition": "A fruit",
                    "part_of_speech": "noun",
                    "example": "An apple a day keeps the doctor away."
                },
                "book": {
                    "definition": "A written work",
                    "part_of_speech": "noun",
                    "example": "She read a book."
                }
            }
        }
        self.manager.save_data()
        
        # Exporta o dicionário
        self.manager.export_dictionary_to_csv("en", self.test_export_path)
        self.assertTrue(os.path.exists(self.test_export_path))
        with open(self.test_export_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            self.assertEqual(len(rows), 2)
        
        # Remove uma palavra
        success, message = self.manager.remove_word("apple", "en")
        self.assertTrue(success)
        self.assertEqual(message, "Palavra removida com sucesso.")
        
        # Verifica que a palavra foi removida do dicionário
        with open(self.test_dict_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.assertNotIn("apple", data["en"])
            self.assertIn("book", data["en"])
        
        # Verifica que o arquivo de exportação foi atualizado
        with open(self.test_export_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['word'], "book")

    def test_export_dictionary_to_csv(self):
        """Testa a exportação do dicionário para um arquivo CSV."""
        # Adiciona duas palavras manualmente
        self.manager.dictionary = {
            "en": {
                "apple": {
                    "definition": "A fruit",
                    "part_of_speech": "noun",
                    "example": "An apple a day keeps the doctor away."
                },
                "book": {
                    "definition": "A written work",
                    "part_of_speech": "noun",
                    "example": "She read a book."
                }
            }
        }
        self.manager.save_data()
        
        # Exporta o dicionário
        success = self.manager.export_dictionary_to_csv("en", self.test_export_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.test_export_path))
        
        # Verifica o conteúdo do CSV
        with open(self.test_export_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            self.assertEqual(len(rows), 2)
            expected_words = {"apple", "book"}
            exported_words = {row['word'] for row in rows}
            self.assertEqual(exported_words, expected_words)
            for row in rows:
                if row['word'] == "apple":
                    self.assertEqual(row['definition'], "A fruit")
                    self.assertEqual(row['part_of_speech'], "noun")
                    self.assertEqual(row['example'], "An apple a day keeps the doctor away.")
                elif row['word'] == "book":
                    self.assertEqual(row['definition'], "A written work")
                    self.assertEqual(row['part_of_speech'], "noun")
                    self.assertEqual(row['example'], "She read a book.")

    @patch('core.dictionary_manager.requests.get')
    def test_import_dictionary_from_csv(self, mock_get):
        """Testa a importação de palavras a partir de um arquivo CSV e atualização do export CSV."""
        # Cria um arquivo CSV de importação com duas novas palavras
        import_dir = os.path.dirname(self.test_import_path)
        os.makedirs(import_dir, exist_ok=True)
        with open(self.test_import_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['word', 'definition', 'part_of_speech', 'example']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerow({
                'word': 'banana',
                'definition': 'A long curved fruit with a yellow skin.',
                'part_of_speech': 'noun',
                'example': 'I ate a ripe banana.'
            })
            writer.writerow({
                'word': 'cat',
                'definition': 'A small domesticated carnivorous mammal.',
                'part_of_speech': 'noun',
                'example': 'The cat sat on the mat.'
            })
        
        # Mock a resposta da API para garantir que nenhuma palavra será duplicada
        mock_get.return_value = unittest.mock.Mock(status_code=404)
        
        # Adiciona uma palavra existente para testar duplicatas
        self.manager.dictionary = {
            "en": {
                "apple": {
                    "definition": "A fruit",
                    "part_of_speech": "noun",
                    "example": "An apple a day keeps the doctor away."
                }
            }
        }
        self.manager.save_data()
        
        # Exporta o dicionário antes da importação
        self.manager.export_dictionary_to_csv("en", self.test_export_path)
        
        # Importa o dicionário a partir do CSV
        success, message = self.manager.import_dictionary_from_csv(self.test_import_path, "en")
        self.assertTrue(success)
        self.assertEqual(message, "Dicionário importado com sucesso. 2 palavras adicionadas, 0 palavras ignoradas.")
        
        # Verifica se as novas palavras foram adicionadas
        with open(self.test_dict_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.assertIn("banana", data["en"])
            self.assertIn("cat", data["en"])
            self.assertIn("apple", data["en"])  # Palavra existente deve permanecer
            self.assertEqual(data["en"]["banana"]["definition"], "A long curved fruit with a yellow skin.")
            self.assertEqual(data["en"]["banana"]["part_of_speech"], "noun")
            self.assertEqual(data["en"]["banana"]["example"], "I ate a ripe banana.")
            self.assertEqual(data["en"]["cat"]["definition"], "A small domesticated carnivorous mammal.")
            self.assertEqual(data["en"]["cat"]["part_of_speech"], "noun")
            self.assertEqual(data["en"]["cat"]["example"], "The cat sat on the mat.")
        
        # Verifica se o arquivo de exportação foi atualizado corretamente
        with open(self.test_export_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            self.assertEqual(len(rows), 3)  # apple, banana, cat
            exported_words = {row['word'] for row in rows}
            expected_words = {"apple", "banana", "cat"}
            self.assertEqual(exported_words, expected_words)
        
        # Testa a importação com palavras já existentes
        # Adiciona 'apple' novamente no CSV
        with open(self.test_import_path, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['word', 'definition', 'part_of_speech', 'example'])
            writer.writerow({
                'word': 'apple',
                'definition': 'A common, round fruit produced by the tree Malus domestica.',
                'part_of_speech': 'noun',
                'example': 'He picked an apple from the tree.'
            })
        
        # Importa novamente
        success, message = self.manager.import_dictionary_from_csv(self.test_import_path, "en")
        self.assertTrue(success)
        self.assertEqual(message, "Dicionário importado com sucesso. 2 palavras adicionadas, 1 palavras ignoradas.")
        
        # Verifica que 'apple' não foi duplicada ou alterada
        with open(self.test_dict_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.assertIn("apple", data["en"])
            self.assertEqual(data["en"]["apple"]["definition"], "A fruit")
            self.assertEqual(data["en"]["apple"]["part_of_speech"], "noun")
            self.assertEqual(data["en"]["apple"]["example"], "An apple a day keeps the doctor away.")
        
        # Verifica que o arquivo de exportação não contém duplicatas
        with open(self.test_export_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            self.assertEqual(len(rows), 3)  # apple, banana, cat (apple não duplicado)
            exported_words = {row['word'] for row in rows}
            self.assertEqual(exported_words, {"apple", "banana", "cat"})

    def test_export_dictionary_without_words(self):
        """Testa a exportação do dicionário quando não há palavras."""
        # Dicionário vazio
        self.manager.dictionary = {}
        self.manager.save_data()
        
        # Tenta exportar o dicionário para o idioma 'en' que não existe
        success = self.manager.export_dictionary_to_csv("en", self.test_export_path)
        self.assertFalse(success)
        self.assertFalse(os.path.exists(self.test_export_path))
        
        # Adiciona um idioma sem palavras e tenta exportar
        self.manager.dictionary = {
            "en": {}
        }
        self.manager.save_data()
        success = self.manager.export_dictionary_to_csv("en", self.test_export_path)
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.test_export_path))
        with open(self.test_export_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            self.assertEqual(len(rows), 0)  # Nenhuma palavra para exportar

    def test_validate_json(self):
        """Testa a validação de arquivos JSON."""
        # Cria um JSON válido
        with open(self.test_dict_path, 'w', encoding='utf-8') as file:
            json.dump({"en": {"apple": {"definition": "A fruit", "part_of_speech": "noun", "example": "An apple a day."}}}, file)
        
        is_valid = self.manager.validate_json(self.test_dict_path)
        self.assertTrue(is_valid)
        
        # Cria um JSON inválido
        with open(self.test_dict_path, 'w', encoding='utf-8') as file:
            file.write("{invalid json")
        
        is_valid = self.manager.validate_json(self.test_dict_path)
        self.assertFalse(is_valid)

    def test_export_dictionary_without_specifying_csv_path(self):
        """Testa a exportação do dicionário usando o caminho padrão do export_csv_path."""
        # Adiciona uma palavra manualmente
        self.manager.manual_add_word(
            word="dog",
            language="en",
            definition="A domesticated carnivorous mammal.",
            part_of_speech="noun",
            example="The dog barked loudly."
        )
        
        # Exporta sem especificar o caminho CSV
        success = self.manager.export_dictionary_to_csv("en")
        self.assertTrue(success)
        self.assertTrue(os.path.exists(self.test_export_path))
        
        # Verifica o conteúdo do CSV
        with open(self.test_export_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['word'], "dog")
            self.assertEqual(rows[0]['definition'], "A domesticated carnivorous mammal.")
            self.assertEqual(rows[0]['part_of_speech'], "noun")
            self.assertEqual(rows[0]['example'], "The dog barked loudly.")

    def test_import_dictionary_with_missing_fields(self):
        """Testa a importação de um CSV com campos ausentes ou vazios."""
        # Cria um arquivo CSV de importação com campos ausentes
        import_dir = os.path.dirname(self.test_import_path)
        os.makedirs(import_dir, exist_ok=True)
        with open(self.test_import_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['word', 'definition', 'part_of_speech', 'example']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            # Palavra com definição faltando
            writer.writerow({
                'word': 'tree',
                'definition': '',
                'part_of_speech': 'noun',
                'example': 'The tree is tall.'
            })
            # Palavra completa
            writer.writerow({
                'word': 'flower',
                'definition': 'The seed-bearing part of a plant.',
                'part_of_speech': 'noun',
                'example': 'The flower is blooming.'
            })
            # Palavra com exemplo faltando
            writer.writerow({
                'word': 'river',
                'definition': 'A large natural stream of water.',
                'part_of_speech': 'noun',
                'example': ''
            })
        
        # Importa o dicionário a partir do CSV
        success, message = self.manager.import_dictionary_from_csv(self.test_import_path, "en")
        self.assertTrue(success)
        self.assertEqual(message, "Dicionário importado com sucesso. 1 palavras adicionadas, 2 palavras ignoradas.")
        
        # Verifica que apenas 'flower' foi adicionada
        with open(self.test_dict_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.assertIn("flower", data["en"])
            self.assertNotIn("tree", data["en"])
            self.assertNotIn("river", data["en"])
        
        # Verifica que o arquivo de exportação foi atualizado corretamente
        self.assertTrue(os.path.exists(self.test_export_path))
        with open(self.test_export_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]['word'], "flower")
            self.assertEqual(rows[0]['definition'], "The seed-bearing part of a plant.")
            self.assertEqual(rows[0]['part_of_speech'], "noun")
            self.assertEqual(rows[0]['example'], "The flower is blooming.")

    def test_import_dictionary_invalid_csv(self):
        """Testa a importação de um arquivo CSV inválido."""
        # Cria um arquivo CSV inválido (faltando cabeçalho)
        with open(self.test_import_path, 'w', encoding='utf-8') as csvfile:
            csvfile.write("invalid, csv, content")
        
        # Importa o dicionário a partir do CSV
        success, message = self.manager.import_dictionary_from_csv(self.test_import_path, "en")
        self.assertFalse(success)
        self.assertIn("Erro ao importar dicionário", message)
        
        # Verifica que nenhuma palavra foi adicionada
        with open(self.test_dict_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            self.assertEqual(data["en"], {})
        
        # Verifica que o arquivo de exportação não foi criado
        self.assertFalse(os.path.exists(self.test_export_path))

if __name__ == '__main__':
    unittest.main()
