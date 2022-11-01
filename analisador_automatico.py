# Importação das bibliotecas
import os
import subprocess
import sys

from vosk import Model, KaldiRecognizer, SetLogLevel

import json
import pandas as pd

# Ler vários formatos de arquivo de áudio de uma pasta.

caminho_origem = os.getcwd() + r'/Audio' + r'/'
caminho_destino = 'Saida/audio_transcrito2.csv'

lista_arquivos = os.listdir(caminho_origem)
print(f"Quantidade de aquivos na pasta {caminho_origem}: ", len(lista_arquivos))
print(lista_arquivos)

# Inicializar variáveis e modelo

SAMPLE_RATE = 16000
SetLogLevel(0)

model = Model('models/modelos/vosk-model-small-pt-0.3')
rec = KaldiRecognizer(model, SAMPLE_RATE)
lista_transcricoes = []

# Ler cada arquivo e transcrever

for arquivo in lista_arquivos:    
    with subprocess.Popen(["ffmpeg", "-loglevel", "quiet", "-i",
                            caminho_origem + arquivo,
                            "-ar", str(SAMPLE_RATE) , "-ac", "1", "-f", "s16le", "-"],
                            stdout=subprocess.PIPE) as process:
        transcricao = ' '
        dic_transcricao = {}
  

        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                dic_transcricao = json.loads(rec.Result())
                transcricao = transcricao + ' ' + dic_transcricao['text']

        dic_transcricao = json.loads(rec.FinalResult())
        transcricao = transcricao + ' ' + dic_transcricao['text']
        lista_transcricoes.append(transcricao)

# Cria um DataFrame com as transcrições
# O nome do arquivo é o índice do Dataframe
df_audio_transcricoes =  pd.DataFrame(lista_transcricoes, index=lista_arquivos, columns=['transcricao'])

# Ler arquivo com as palavras-chaves
# ....

# Realiar filtro por palavras-chaves em todos as transcrições

lista_palavras_chaves = ['jesus abençoado', 'família']
palavra_chave = '|'.join(lista_palavras_chaves)

serie_resultado = df_audio_transcricoes['transcricao'].str.contains(palavra_chave)

# Filtra as colunas que APARECEM as palavras chave (True). Para False colocar ~ antes

df_filtrado =  df_audio_transcricoes[serie_resultado]
df_filtrado = df_filtrado.rename_axis('arquivo').reset_index() # transformma indice em coluna do dataframe

# Exporta o resultado filtrado para um arquivo csv

df_filtrado.to_csv(caminho_destino, sep=';', encoding='latin-1')

