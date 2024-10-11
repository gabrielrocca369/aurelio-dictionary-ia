# core/speech_module.py

import speech_recognition as sr
from gtts import gTTS
import os
import tempfile
from playsound import playsound
import logging

class SpeechModule:
    """Módulo de reconhecimento de fala e síntese de voz."""

    def __init__(self, language='en'):
        self.language = language
        self.recognizer = sr.Recognizer()
        self.logger = logging.getLogger(self.__class__.__name__)

    def set_language(self, language):
        """Define o idioma para reconhecimento de fala e síntese de voz."""
        self.language = language
        self.logger.info(f"Idioma de voz definido para {language}.")

    def recognize_speech(self):
        """Captura e converte a fala do usuário em texto."""
        with sr.Microphone() as source:
            self.logger.info("Aguardando fala do usuário...")
            print("Por favor, fale agora...")
            audio = self.recognizer.listen(source)

        try:
            if self.language == 'pt':
                text = self.recognizer.recognize_google(audio, language='pt-BR')
            elif self.language == 'es':
                text = self.recognizer.recognize_google(audio, language='es-ES')
            elif self.language == 'fr':
                text = self.recognizer.recognize_google(audio, language='fr-FR')
            else:
                text = self.recognizer.recognize_google(audio, language='en-US')
            self.logger.info(f"Fala reconhecida: {text}")
            print(f"Você disse: {text}")
            return text
        except sr.UnknownValueError:
            self.logger.warning("Não foi possível entender o áudio.")
            print("Desculpe, não entendi o que você disse.")
            return None
        except sr.RequestError as e:
            self.logger.error(f"Erro na API de reconhecimento de fala: {e}")
            print("Erro de rede. Verifique sua conexão com a internet.")
            return None

    def speak(self, text):
        """Converte texto em fala e reproduz o áudio."""
        try:
            tts = gTTS(text=text, lang=self.language)
            with tempfile.NamedTemporaryFile(delete=True, suffix='.mp3') as fp:
                tts.save(fp.name)
                playsound(fp.name)
            self.logger.info("Áudio reproduzido com sucesso.")
        except Exception as e:
            self.logger.error(f"Erro ao gerar ou reproduzir o áudio: {e}")
