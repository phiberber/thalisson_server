# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 16:30:00) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: C:\Users\Developer\proijects\bot-python\indicador_grafico.py
# Compiled at: 2020-05-21 13:25:44
# Size of source mod 2**32: 5729 bytes
from indicadores import *
from datetime import datetime, tzinfo, timezone
import datetime as dt
from datetime import date
from dateutil import tz
import pandas as pd, time

class IndicadorGrafico(object):

    def __init__(self, interface):
        self.ema_forte = 50
        self.velas = []
        self.interface = interface
        self.ativosMetrica = []

    def mediaMovel(self, moeda, worker, interface):
        try:
            par = interface.getMercado(moeda, worker, 'analise', False)
            if par['open'] == False:
                return (0, 0, 0)
            moeda = par['moeda']
            ativo = self.getAtivo(moeda)
            ativo['velas'] = interface.getVelas(moeda, worker.tendencia_time_frame, 200)
            velas = ativo['velas']
            vela = velas[(-1)]
            df = pd.DataFrame(data=velas)
            lista_close = df['close']
            media_lenta = self.calcularMedia(lista_close, worker.periodo_media_lenta, worker.tipo_media_lenta)
            media_rapida = self.calcularMedia(lista_close, worker.periodo_media_rapida, worker.tipo_media_rapida)
            print('TENDENCIA TIMEFREME', worker.tendencia_time_frame, moeda)
            return (
             vela['close'], media_rapida[(-1)], media_lenta[(-1)])
        except Exception as error:
            try:
                print('getmediaMovel', error)
                worker.logs.append('Erro ao carregar gráfico de tendência.')
            finally:
                error = None
                del error

        return (0, 0, 0)

    def Bolliger(self, velas, periodo):
        lista = []
        for vela in velas:
            lista.append(vela['close'])

        return bollingerBands(lista, periodo, 2.5)

    def calcularMedia(self, lista, periodo, tipo):
        if tipo == 'ema':
            return ExpMovingAverage(lista, periodo)
        return movingaverage(lista, periodo)

    def mediaMovelCash(self, moeda):
        print('mediaMovel', moeda)
        ativo = self.getAtivo(moeda)
        velas = ativo['velas']
        if len(velas) == 0:
            return
        vela = velas[0]
        vela = velas[(-1)]
        print('Hora inicio: ' + str(timestamp_converter(vela['to'])) + ' abertura: ' + str(vela['close']))

    def verificarEntradaEstrategai():
        print('ok')

    def getAtivosAbertos(self, interface):
        lista = []
        try:
            for item in interface.ativos:
                moeda = item['moeda']
                if moeda in lista:
                    continue
                else:
                    lista.append(moeda)

        except Exception as error:
            try:
                print('get ativos metricas', error)
            finally:
                error = None
                del error

        return lista

    def getAtivo(self, moeda):
        for item in self.ativosMetrica:
            if moeda == item['moeda']:
                return item

        novo = {'moeda':moeda, 
         'velas':[]}
        self.ativosMetrica.append(novo)
        return novo

    def atualizar(self, worker, interface):
        return False


def timestamp_converter(x):
    hora = datetime.strptime(datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    hora = hora.replace(tzinfo=(tz.gettz('GMT')))
    return str(hora.astimezone(tz.gettz('America/Sao Paulo')))[:-6]