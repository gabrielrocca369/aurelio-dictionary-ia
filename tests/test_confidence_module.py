# tests/test_confidence_module.py

import unittest
from core.confidence_module import ConfidenceModule

class TestConfidenceModule(unittest.TestCase):
    def setUp(self):
        """Configuração antes de cada teste."""
        self.conf_module = ConfidenceModule()

    def test_calculate_confidence_high(self):
        """Testa o cálculo de confiança alta quando definição e exemplo estão presentes."""
        definition = "A round fruit with red or green skin and a whitish interior."
        example = "I ate a delicious apple for breakfast."
        confidence = self.conf_module.calculate_confidence(definition, example)
        expected_confidence = min(100.0, (len(definition.split()) + len(example.split())) * 2)
        self.assertEqual(confidence, expected_confidence,
                         f"Esperado {expected_confidence}, obtido {confidence}")

    def test_calculate_confidence_low(self):
        """Testa o cálculo de confiança baixa quando definição e exemplo estão ausentes."""
        definition = ""
        example = ""
        confidence = self.conf_module.calculate_confidence(definition, example)
        self.assertEqual(confidence, 0.0, f"Esperado 0.0, obtido {confidence}")

    def test_calculate_confidence_partial_definition(self):
        """Testa o cálculo de confiança média quando apenas a definição está presente."""
        definition = "A round fruit."
        example = ""
        confidence = self.conf_module.calculate_confidence(definition, example)
        expected_confidence = min(100.0, len(definition.split()) * 1.5)
        self.assertAlmostEqual(confidence, expected_confidence, places=2,
                               msg=f"Esperado {expected_confidence}, obtido {confidence}")

    def test_calculate_confidence_partial_example(self):
        """Testa o cálculo de confiança média quando apenas o exemplo está presente."""
        definition = ""
        example = "I ate a delicious apple."
        confidence = self.conf_module.calculate_confidence(definition, example)
        expected_confidence = min(100.0, len(example.split()) * 1.5)
        self.assertAlmostEqual(confidence, expected_confidence, places=2,
                               msg=f"Esperado {expected_confidence}, obtido {confidence}")

    def test_calculate_confidence_max_cap(self):
        """Testa se o cálculo de confiança não excede 100."""
        definition = " ".join(["word"] * 60)  # 60 palavras
        example = " ".join(["example"] * 60)  # 60 palavras
        confidence = self.conf_module.calculate_confidence(definition, example)
        self.assertEqual(confidence, 100.0, f"Esperado 100.0, obtido {confidence}")

    def test_calculate_confidence_zero_length_strings(self):
        """Testa o cálculo de confiança com strings vazias ou apenas espaços."""
        test_cases = [
            {"definition": "", "example": ""},
            {"definition": "   ", "example": ""},
            {"definition": "", "example": "   "},
            {"definition": "   ", "example": "   "}
        ]
        for case in test_cases:
            with self.subTest(case=case):
                confidence = self.conf_module.calculate_confidence(case["definition"], case["example"])
                self.assertEqual(confidence, 0.0, f"Esperado 0.0, obtido {confidence}")

    def test_calculate_confidence_invalid_inputs(self):
        """Testa o cálculo de confiança com entradas inválidas."""
        test_cases = [
            {"definition": None, "example": None},
            {"definition": None, "example": "Valid example."},
            {"definition": "Valid definition.", "example": None},
            {"definition": 12345, "example": "Valid example."},
            {"definition": "Valid definition.", "example": 67890},
            {"definition": ["list", "of", "words"], "example": "Valid example."},
            {"definition": "Valid definition.", "example": {"key": "value"}},
        ]
        for case in test_cases:
            with self.subTest(case=case):
                confidence = self.conf_module.calculate_confidence(case["definition"], case["example"])
                self.assertEqual(confidence, 0.0,
                                 f"Esperado 0.0 para entradas inválidas, obtido {confidence}")

    def test_calculate_confidence_special_characters(self):
        """Testa o cálculo de confiança para palavras com caracteres especiais e Unicode."""
        definition = "Früchte sind gesund und lecker."
        example = "Ich habe einen Apfel gegessen."
        confidence = self.conf_module.calculate_confidence(definition, example)
        expected_confidence = min(100.0, (len(definition.split()) + len(example.split())) * 2)
        self.assertEqual(confidence, expected_confidence,
                         f"Esperado {expected_confidence}, obtido {confidence}")

    def test_calculate_confidence_case_insensitivity(self):
        """Testa se a confiança é calculada corretamente independentemente da capitalização."""
        definitions = [
            "A round fruit with red or green skin and a whitish interior.",
            "a Round Fruit with Red or Green skin and a Whitish Interior.",
            "A ROUND FRUIT WITH RED OR GREEN SKIN AND A WHITISH INTERIOR."
        ]
        example = "I ate a delicious apple for breakfast."
        for definition in definitions:
            with self.subTest(definition=definition):
                confidence = self.conf_module.calculate_confidence(definition, example)
                expected_confidence = min(100.0, (len(definition.split()) + len(example.split())) * 2)
                self.assertEqual(confidence, expected_confidence,
                                 f"Esperado {expected_confidence}, obtido {confidence}")

    def test_calculate_confidence_unicode_characters(self):
        """Testa o cálculo de confiança com caracteres Unicode."""
        definition = "フルーツは健康的でおいしいです。"
        example = "朝食に美味しいりんごを食べました。"
        confidence = self.conf_module.calculate_confidence(definition, example)
        expected_confidence = min(100.0, (len(definition.split()) + len(example.split())) * 2)
        self.assertEqual(confidence, expected_confidence,
                         f"Esperado {expected_confidence}, obtido {confidence}")

    def test_calculate_confidence_no_spaces(self):
        """Testa o cálculo de confiança com palavras sem espaços."""
        definition = "apple"
        example = "apple"
        confidence = self.conf_module.calculate_confidence(definition, example)
        expected_confidence = min(100.0, (1 + 1) * 2)  # 4.0
        self.assertEqual(confidence, expected_confidence,
                         f"Esperado {expected_confidence}, obtido {confidence}")

    def test_calculate_confidence_large_input(self):
        """Testa o cálculo de confiança com entradas muito grandes."""
        definition = "word " * 1000  # 1000 palavras
        example = "example " * 1000  # 1000 palavras
        confidence = self.conf_module.calculate_confidence(definition, example)
        self.assertEqual(confidence, 100.0, f"Esperado 100.0, obtido {confidence}")

if __name__ == '__main__':
    unittest.main()
