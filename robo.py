# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 16:30:00) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: C:\Users\Developer\proijects\bot-python\robo.py
# Compiled at: 2020-05-21 13:25:44
# Size of source mod 2**32: 4458 bytes
import time
from datetime import datetime
import datetime as dt
from datetime import date
from dateutil import tz
from lista_sinais import *
from update_ativos import *

def iniciarRobo(nome, worker, inteface, analise):
    tempo_para_proxima_vela_horario = 0
    print('\n\n>>>> iniciarRobo()')
    if worker.delay < 0:
        worker.delay = 0
    worker.logs.append('Robo Iniciado!')
    while True:
        try:
            lista_proxima = oproximoSinalTime(worker.lista_sinais, worker, 15)
            moedas_proximas = moedasNaLista(lista_proxima)
            for moeda in moedas_proximas:
                pegarPayoutSinais(moeda, worker, inteface)

            tempo_para_proxima_vela = 0
            for item in worker.lista_sinais:
                a = datetime.strptime(dt.datetime.now(tz.gettz(worker.time_zone)).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                b = datetime.strptime(item['time'], '%d-%m-%Y %H:%M')
                diff = (b - a).total_seconds() + worker.diff_seg_servidor_local
                if worker.horario_servidor:
                    diff = (b - a).total_seconds()
                if not (tempo_para_proxima_vela > diff and diff > 0):
                    if diff > 0:
                        if tempo_para_proxima_vela == 0:
                            tempo_para_proxima_vela = diff
                            tempo_para_proxima_vela_horario = diff
                    if diff < worker.delay + 1:
                        if diff > -20:
                            tipo_entrada = item['direcao'].lower()
                            entrada_aprovada = False
                            if worker.ativar_analise_medias == True:
                                valor_atual, media_rapida, media_lenta = analise.mediaMovel(item['moeda'], worker, inteface)
                                if valor_atual > 0:
                                    if tipo_entrada == 'call':
                                        if valor_atual > media_lenta:
                                            if media_rapida > media_lenta:
                                                entrada_aprovada = True
                                if valor_atual > 0 and tipo_entrada == 'put' and valor_atual < media_lenta:
                                    if media_rapida < media_lenta:
                                        entrada_aprovada = True
                                    print(item['moeda'], 'call', valor_atual, media_rapida, media_lenta, tipo_entrada, valor_atual > media_lenta, media_rapida > media_lenta)
                                    print(item['moeda'], 'put', valor_atual, media_rapida, media_lenta, tipo_entrada, valor_atual < media_lenta, media_rapida < media_lenta)
                                else:
                                    pass
                            entrada_aprovada = True
                        tempo_para_proxima_vela_horario = 0
                        worker.lista_sinais.remove(item)
                        if entrada_aprovada == True:
                            worker.processarSinal(item)
                    else:
                        worker.logs.append('Cancelado pela análise de tendência: ' + item['moeda'] + ' , ' + item['time'] + ', ' + tipo_entrada)

            if tempo_para_proxima_vela < 120 and tempo_para_proxima_vela > 0:
                worker.liberado_de_trabalho = True
            else:
                worker.liberado_de_trabalho = False
        except Exception as error:
            try:
                print('robo', error)
            finally:
                error = None
                del error

        time.sleep(0.5)