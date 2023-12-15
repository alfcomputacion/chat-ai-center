#### Librerias y API KEY ####

import os
from openai import OpenAI
from decouple import config

import requests  # Libreria para peticiones HTML
import json  # Libreria para manejar archivos JSON
from pathlib import Path  # Libreria para trabajar con rutas de archivos y directorios
import speech_recognition as sr
import sounddevice as sd
import numpy as np
import pygame


client = OpenAI(
    api_key=config("OPENAI_API_KEY"),
)
#############################################

#### Funciones ####

# Definición de la nueva función para usar el chat GPT #gpt-3.5-turbo  gpt-4


def get_completion(user, prompt, model="gpt-3.5-turbo", temperature=0):
    completion = client.chat.completions.create(
        messages=[
            {
                "role": user, "content": prompt
            }
        ],
        model=model,
        temperature=temperature,
    )
    return completion.choices[0].message.content


# Definción de una función para convertir voz del microfono a texto
def grabar_audio():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Habla ahora...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    print("Grabación completa.")
    return audio

# Definicion de una funcion para extraer el texto de la voz


def extraer_texto(audio):
    recognizer = sr.Recognizer()

    try:
        print("Reconociendo voz...")
        # Puedes ajustar el idioma según tus necesidades
        texto = recognizer.recognize_google(audio, language="es-ES")
        return texto
    except sr.UnknownValueError:
        print("No se pudo entender el audio")
        return None
    except sr.RequestError as e:
        print(f"Error al hacer la solicitud a Google Speech Recognition: {e}")
        return None

# Definicion de una funcion para traer en formato JSON los resultados de una encuentas de forms


def obtener_datos_hoja_calculo():
    # URL de la hoja de cálculo de Google Sheets en formato JSON
    # El archivo debe ser publico para no tener que usar la API de Google
    # Un ejemplo de una URL original es: https://docs.google.com/spreadsheets/d/12kjS5SW9iS9Bem-kQuANnut65q7Wq8aLYNvGQubgaGg/edit?resourcekey#gid=611254568
    # El formato para tener un archivo JSON de la hoja de calculo es: https://docs.google.com/spreadsheets/d/ID_HOJA/gviz/tq?tqx=out:json&gid=NUMERO_HOJA
    # url = "https://docs.google.com/spreadsheets/d/12kjS5SW9iS9Bem-kQuANnut65q7Wq8aLYNvGQubgaGg/gviz/tq?tqx=out:json&gid=0"

    # https://docs.google.com/spreadsheets/d/1SPtGHwPPt5rwhUixF4K_NcIOXwAlJRI1zA0eWSHPzyw/edit?resourcekey#gid=1405253811
    # https://docs.google.com/spreadsheets/d/19KnQ5MOoEvx_n1u3S7qo9jhsdDgFWEo4KjO9qykmsGQ/edit?usp=sharing
    # url = "https://docs.google.com/spreadsheets/d/19KnQ5MOoEvx_n1u3S7qo9jhsdDgFWEo4KjO9qykmsGQ/gviz/tq?tqx=out:json&gid=0"
    url = "https://docs.google.com/spreadsheets/d/12kjS5SW9iS9Bem-kQuANnut65q7Wq8aLYNvGQubgaGg/gviz/tq?tqx=out:json&gid=0"

    # Realizar la solicitud HTTP GET a la hoja de cálculo
    try:

        response = requests.get(url)
        # Verifica que la solicitud fue exitosa
        if response.status_code == 200:
            try:
                # Google incluye caracteres adicionales al inicio y al final de la respuesta que debemos eliminar
                # para obtener un JSON válido. Aquí eliminamos "google.visualization.Query.setResponse(" al inicio
                # y ");" al final.
                json_raw = response.text.split('(', 1)[1].rsplit(')', 1)[0]

                # Convertir la cadena de respuesta en un diccionario JSON
                data = json.loads(json_raw)

                # La variable 'data' ahora contiene el objeto JSON que puedes utilizar
                return data
            except (IndexError, json.JSONDecodeError) as e:
                print("No se pudo parsear la respuesta JSON: ", e)
        else:
            print("Error al realizar la solicitud HTTP: Código de estado",
                  response.status_code)
    except TypeError as e:
        print(e)
# Definicion de una funcion para preparar los datos y ser enviados al chat GPT


def formatear_datos_para_gpt(data):
    # Inicializamos una cadena vacía para almacenar el texto formateado
    texto_para_gpt = ""

    # Iteramos sobre las filas de la tabla en los datos proporcionados
    for row in data['table']['rows']:
        # Obtenemos las celdas de la fila actual
        celdas = row['c']

        # Creamos una lista con los valores de las celdas, o cadena vacía si la celda está vacía
        fila = [celda['v'] if celda else "" for celda in celdas]

        # Concatenamos los valores de la fila separados por comas y añadimos un salto de línea
        texto_para_gpt += ", ".join(fila) + "\n"

    # Devolvemos el texto formateado para GPT-3
    return texto_para_gpt

# Definicion de una función para construir el prompt de texto


def enviar_pregunta_a_gpt(pregunta, datos):
    prompt_interno = f"{datos}\n\n{pregunta}"
    return prompt_interno

# Defincion de una funcion para limitar el texto a 200 palabras


def obtener_primeras_palabras(texto, limite=4000):
    # Dividir el texto en palabras
    palabras = texto.split()

    # Verificar si el número de palabras es menor que el límite
    if len(palabras) <= limite:
        return texto
    else:
        # Devolver las primeras 4000 palabras
        return ' '.join(palabras[:limite])

# Definicion de la función para convertir texto a voz con el modelo tts-1


def texto_a_voz(prompt_text):
    speech_file_path = Path().parent / "speech.mp3"
    # speech_file_path = "c:/Users/lalo/OneDrive - IA.Center - Center for Artificial Intelligence/CursoOpenAI/openai-env/audios/speech.mp3"
    response = client.audio.speech.create(
        model="tts-1",
        voice="shimmer",
        input=prompt_text
    )
    response.stream_to_file(speech_file_path)

# Definicion para reproducir un sonido mp3


def play_mp3(file_path):
    # Inicializa pygame
    pygame.mixer.init()
    # Carga el archivo de música
    pygame.mixer.music.load(file_path)
    # Reproduce la música
    pygame.mixer.music.play()

    # Espera a que la música termine de reproducirse
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

#############################################


#### Programa principal ####

# Obtener los datos de la hoja de cálculo
datos_hoja = obtener_datos_hoja_calculo()

# Formatear los datos para GPT
datos_formateados = formatear_datos_para_gpt(datos_hoja)

# se genera el prompt a partir de la voz
if __name__ == "__main__":
    audio_grabado = grabar_audio()

    # Extraer texto del audio grabado
    try:
        texto_extraido = extraer_texto(audio_grabado)
    except TypeError as e:
        print(e)

    if texto_extraido:
        # print("Texto extraído del audio:", texto_extraido)
        prompt_voz = texto_extraido
        print("Prompt: ", prompt_voz)
    else:
        print("No se pudo extraer texto del audio.")

# Ejemplo de cómo enviar una pregunta y obtener una respuesta mediante voz
user = "system"

pregunta = f"""
Tu eres un asistente virtual del centro de inteligencia artificial, llamado IA SKILLS. Se te proporcionará información de una encuesta realizada a una audiencia, la cual se te proporcionará el formato JSON, que representa una tabla con información consultada.
Tu trabajo consiste en realizar una acción o consulta sobre el archivo JSON. La acción o consulta que debes realizar se encuentra delimitada por corchetes angulares

Consulta o acción: < {prompt_voz} >  

Por favor, si debes realizar el calculo de algo sobre la información, como por ejemplo la edad promedio de las personas u otras acciones como contar las personas mayores a una determinada edad, por favor realiza los cálculos y verifica tu respuesta y solo infórmame del cálculo solicitado. Si no te fue posible realizar el cálculo solicitado, dime algo como: “No pude realizar el cálculo, por favor repite la pregunta”
El formato de tus respuestas debe tener la siguiente estructura:
<Frase corta cordial antes de responder que varie de respuesta en respuesta>
<Respuesta: acción o calculo solicitado.>

"""

prompt = enviar_pregunta_a_gpt(pregunta, datos_formateados)

response = get_completion(user, prompt)
print(response)


# Vamos a generar un sonido de la respuesta en mp3
prompt_text = obtener_primeras_palabras(response, 200)
texto_a_voz(prompt_text)

# vamos a reproducir un sonido en mp3. Llama a la función y pasa la ruta al archivo mp3
play_mp3(Path().parent / "speech.mp3")

#############################################
