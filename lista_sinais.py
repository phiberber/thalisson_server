# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 16:30:00) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: C:\Users\Developer\proijects\bot-python\lista_sinais.py
# Compiled at: 2020-05-21 13:25:44
# Size of source mod 2**32: 4684 bytes
import time
from datetime import datetime
import datetime as dt
from datetime import date
from dateutil import tz
import json

def oproximoSinal(lista, worker):
    foco = {}
    menor_temp = 0
    for item in lista:
        try:
            a = datetime.strptime(dt.datetime.now(tz.gettz(worker.time_zone)).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            b = datetime.strptime(item['time'], '%d-%m-%Y %H:%M')
            diff = (b - a).total_seconds() + worker.diff_seg_servidor_local
            if worker.horario_servidor:
                diff = (b - a).total_seconds()
            if diff > 0:
                if diff < menor_temp or menor_temp == 0:
                    menor_temp = diff
                    foco = item
            if diff < -100:
                lista.remove(item)
                worker.logs.append('Sinal removido por tempo ultrapassado!')
        except Exception as error:
            try:
                print('An exception occurred', item['time'], error)
            finally:
                error = None
                del error

    copy = json.dumps(foco)
    dados = json.loads(copy)
    return dados


def oproximoSinalTime(lista, worker, seg):
    resultados = []
    for item in lista:
        try:
            a = datetime.strptime(dt.datetime.now(tz.gettz(worker.time_zone)).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            b = datetime.strptime(item['time'], '%d-%m-%Y %H:%M')
            diff = (b - a).total_seconds() + worker.diff_seg_servidor_local
            if worker.horario_servidor:
                diff = (b - a).total_seconds()
            if diff < seg:
                resultados.append(item)
        except Exception as error:
            try:
                print('An exception occurred', error)
            finally:
                error = None
                del error

    return resultados


def tratarLista(worker, lista, liberar_repeticao):
    for item in lista:
        try:
            if verificarSeExiste(worker.lista_sinais, item, liberar_repeticao):
                continue
            a = datetime.strptime(dt.datetime.now(tz.gettz(worker.time_zone)).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
            b = datetime.strptime(item['time'], '%d-%m-%Y %H:%M')
            diff = (b - a).total_seconds() + worker.diff_seg_servidor_local
            if worker.horario_servidor:
                diff = (b - a).total_seconds()
            if diff < -30:
                worker.logs.append('Sinal com horário ultrapassado: ' + item['time'] + ' ' + item['moeda'])
                continue
            worker.lista_sinais.append(item)
        except Exception as error:
            try:
                print('An exception occurred', error)
                worker.logs.append('Erro ao carregar horáiro do sinal: ' + item['time'] + ' ' + item['moeda'])
            finally:
                error = None
                del error

    worker.lista_sinais = sorted((worker.lista_sinais), key=(lambda k: k['time']))


def verificarSeExiste(lista, foco, liberar_repeticao):
    for item in lista:
        if liberar_repeticao == True:
            if item['time'] == foco['time']:
                if item['moeda'] == foco['moeda']:
                    return True
        if item['time'] == foco['time'] and liberar_repeticao == False:
            return True

    return False


def removerDaLista(lista, foco):
    for item in lista:
        if item['moeda'] == foco['moeda'] and item['time'] == foco['time'] and item['direcao'] == foco['direcao']:
            lista.remove(item)
            print('removeu', item)
            return True

    return False


def moedasNaLista(lista):
    lista_ativos = []
    for item in lista:
        moeda = item['moeda']
        if moeda in lista_ativos:
            continue
        else:
            lista_ativos.append(moeda)

    return lista_ativos