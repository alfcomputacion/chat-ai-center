import os
from openai import OpenAI
from  pathlib import Path
import speech_recognition as sr
import numpy
import pygame



def grabar_audio():
    pass


def recognize_speech(audio_file_path):
    # Create a Recognizer instance
    recognizer = sr.Recognizer()

    # Load audio file
    with sr.AudioFile(audio_file_path) as source:
        # Adjust for ambient noise
        recognizer.adjust_for_ambient_noise(source)
        
        # Listen to the audio and recognize speech
        audio = recognizer.record(source)

        try:
            # Recognize speech using Google Web Speech API
            text = recognizer.recognize_google(audio)
            print("Recognized text: {}".format(text))
        except sr.UnknownValueError:
            print("Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Web Speech API; {0}".format(e))

# Example usage:
audio_file_path = "your_audio_file.wav"  # replace with the path to your audio file
recognize_speech(audio_file_path)


def texto_a_voz(prompt_text):
    speech_file_path = Path().parent /"speech.mp3"
    response = client.audio.speech.create(
        model = "tts-1",
        voice = "shimmer",
        input = prompt_text
    )
    response.stream_to_file(speech_file_path)

def play_mp3(file_path):
    pygame
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    

    while True:
        datos_hoja = obtener_datos_hoja_calculo()
        datos_formateados = formatear_datos_para _gpt(datos_hoja)

        audio_grabado = grabar_audio()
        texto_extraido = 

        user = "system"
        pregunta = "pregunta"