# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 16:30:00) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: C:\Users\Developer\proijects\bot-python\interface.py
# Compiled at: 2020-05-08 17:42:52
# Size of source mod 2**32: 6419 bytes
from iqoptionapi.stable_api import IQ_Option
import _thread, time
from update_ativos import *
from entrada_buy import *

class Interface(object):

    def __init__(self):
        self.debug = False
        self.API = False
        self.ativos = []
        self.upAtivos = False

    def conectado(self):
        if self.API == False:
            return False
        return self.API.check_connect()

    def desconectar(self):
        self.API = False

    def getHorario(self):
        if self.API == False:
            return 0
        return self.API.get_server_timestamp()

    def config(self):
        if self.API == False:
            return (0, 'USD')
        balance = self.API.get_balance()
        currency = self.API.get_currency()
        return (
         balance, currency)

    def closePricePar(serf, par):
        if self.conectado() == False:
            return 0
        while 1:
            vela = self.API.get_realtime_candles(par, 60)
            for velas in vela:
                print(vela[velas]['close'], 'total', len(vela))

        time.sleep(1)
        self.API.stop_candles_stream(par, 60)

    def getVelas(self, par, time_frame, total):
        if self.conectado() == False:
            return False
        vela = self.API.get_candles(par, time_frame * 60, total, time.time())
        return vela

    def getMercado(self, moeda, worker, direcao, logs):
        maior_payout = 0
        foco = {'open': False}
        payout_mercado = ''
        for item in self.ativos:
            payout_foco = int(item['payout'])
            if item['moeda'] == moeda:
                payout_mercado += ' ' + item['tipo'] + ': ' + str(payout_foco)
                if payout_foco > maior_payout:
                    maior_payout = payout_foco
                    foco = item
            if item['moeda'] == moeda + '-OTC' and worker.otc:
                payout_mercado += ' ' + item['tipo'] + '-OTC: ' + str(payout_foco)
                if payout_foco > maior_payout:
                    maior_payout = payout_foco
                    foco = item

        if payout_mercado != '':
            if foco['open'] == True:
                if logs == True:
                    worker.logs.append('Análise ativos abertos para ' + moeda + payout_mercado + ' direcao: ' + direcao)
        return foco

    def entrada(self, worker, direcao, moeda, time_frame, valor_aposta, fator, gale):
        try:
            if self.API == False or self.API.check_connect() == False:
                return False
            else:
                ativo = self.getMercado(moeda, worker, direcao, True)
                if ativo['open'] == False:
                    worker.logs.append('Ordem cancelada, mercado fechado! ' + moeda)
                    return False
                    if ativo['payout'] < worker.payout_minimo:
                        worker.logs.append('Ordem cancelada, payout abaixo do mínimo! ' + moeda + ' paytou atual: ' + str(ativo['payout']))
                        return False
                    moeda = ativo['moeda']
                    if ativo['tipo'] == 'digital':
                        _thread.start_new_thread(buyDigital, (self, direcao.lower(), moeda, time_frame, int(valor_aposta), fator, gale, worker))
                else:
                    _thread.start_new_thread(buyBinary, (self, direcao.lower(), moeda, time_frame, int(valor_aposta), fator, gale, worker))
        except Exception as error:
            try:
                print('Erro entrada interface', error)
                worker.logs.append('Erro entrada corretora: ' + moeda)
            finally:
                error = None
                del error

    def conectar(self, email, senha, tipo, worker):
        try:
            self.API = IQ_Option(email, senha)
            self.API.connect()
            if self.API.check_connect() == False:
                print('Erro ao se conectar')
                worker.logs.append('Erro ao conectar! Remova os dois fatores da IqOption se tiver ativo e verifique seu email e senha! Tentativa atual com email = ' + email)
            else:
                self.API.change_balance(tipo)
                worker.onStart()
                worker.logs.append('Conectado! ' + email)
            if self.API.check_connect():
                if self.upAtivos == False:
                    self.upAtivos = True
                    _thread.start_new_thread(iniciarUpdateAtivos, ('Thread-1', self, worker))
            time.sleep(1)
        except Exception as error:
            try:
                print('Erro entrada interface', error)
                worker.logs.append('Falha no login')
            finally:
                error = None
                del error