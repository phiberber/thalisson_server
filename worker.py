# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 16:30:00) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: C:\Users\Developer\proijects\bot-python\worker.py
# Compiled at: 2020-05-21 13:25:44
# Size of source mod 2**32: 15861 bytes
from datetime import datetime
import datetime as dt
from datetime import date
import pandas as pd, _thread, json
from dateutil import tz
from interface import Interface
from robo import *
from lista_sinais import *
from indicador_grafico import IndicadorGrafico
inteface = Interface()
analise = IndicadorGrafico(inteface)

def loopIndicadores(nome, worker, interface):
    analise.atualizar(worker, interface)


class Worker(object):

    def __init__(self):
        self.versao = '1.3.5'
        self.debug = False
        self.horario_servidor = False
        self.liberarProcessamento = False
        self.liberado_de_trabalho = False
        self.venciemento = 'aguardando'
        self.ultimo_status_verificado = dt.datetime.utcnow()
        self.ultimo_reconectar = dt.datetime.utcnow()
        self.diff_seg_servidor_local = 0
        self.email = ''
        self.senha = ''
        self.ativo = False
        self.status = 'Desconectado'
        self.tipo = 'PRACTICE'
        self.lista_sinais = []
        self.logs = []
        self.ordens = []
        self.alertas = []
        self.moedas_live = []
        self.moedas_usadas = []
        self.valor_aposta = 10
        self.time_frame = 1
        self.pocentagem_banca_para_entrada = False
        self.fator_gale = 1.2
        self.delay = 2
        self.delay_gale = 1
        self.gale_turbo = True
        self.otc = True
        self.gale = 2
        self.limit_de_ganho = 5
        self.limit_de_perda = 3
        self.payout_minimo = 70
        self.time_zone = 'America/Sao Paulo'
        self.currency = 'USD'
        self.balance = 0
        self.valor_inical = 0
        self.startRobo = False
        self.limit_perda_balance = 0
        self.limit_ganho_balance = 0
        self.pocentagem_banca_para_gestao_ganho = True
        self.pocentagem_banca_para_gestao_perda = True
        self.limit_de_perda_balance = 0
        self.limit_de_ganho_balance = 0
        self.gale_proximo_sinal = True
        self.gale_atual = 0
        self.ativar_analise_medias = False
        self.periodo_media_lenta = 14
        self.tipo_media_lenta = 'sma'
        self.periodo_media_rapida = 4
        self.tipo_media_rapida = 'ema'
        self.tendencia_time_frame = 5
        self.soro_perda_maxima = 200
        self.soro_porc_do_lucro = 0.7
        self.soro_qnt_de_ciclos = 4
        self.soro_ciclo_atual = 0
        self.soro_lucro_atual = 0

    def zerarCiclosSoro(self):
        self.soro_lucro_atual = 0
        self.soro_ciclo_atual = 0

    def now(self):
        agora = datetime.utcfromtimestamp(time.time() - self.diff_seg_servidor_local)
        return agora

    def movimentarGaleSinal(self, lucro):
        if self.gale_proximo_sinal:
            if lucro <= 0:
                self.gale_atual = self.gale_atual + 1
                if self.gale_atual > self.gale:
                    self.gale_atual = 0
        if lucro > 0:
            self.gale_atual = 0

    def movimentarSoro(self, resultado):
        res_temp = self.soro_lucro_atual + resultado
        perda_maxima = self.soro_perda_maxima * -1
        if self.soro_qnt_de_ciclos > 0:
            if self.soro_ciclo_atual > self.soro_qnt_de_ciclos:
                self.zerarCiclosSoro()
            else:
                if res_temp < perda_maxima:
                    self.zerarCiclosSoro()
                else:
                    self.soro_ciclo_atual = self.soro_ciclo_atual + 1
                    self.soro_lucro_atual = res_temp
            self.logs.append('PARCIAL SOROS = LUCRO ATUAL: ' + str(res_temp) + ' CICLO: ' + str(self.soro_ciclo_atual))

    def calcularValorEntrada(self):
        valor = self.calcularValorEntradaGeral()
        if self.soro_qnt_de_ciclos > 0:
            perda_maxima = self.soro_perda_maxima * -1
            if self.soro_ciclo_atual == 0 or self.soro_ciclo_atual > self.soro_qnt_de_ciclos:
                return valor
            if self.soro_lucro_atual <= perda_maxima:
                return valor
            if self.soro_lucro_atual > 0:
                valor = valor + self.soro_lucro_atual * self.soro_porc_do_lucro
                self.logs.append('ENTRADA SOROS = VALOR: ' + str(valor) + ' CICLO ' + str(self.soro_ciclo_atual) + ' LUCRO ATUAL: ' + str(self.soro_lucro_atual))
                return valor
            if self.soro_lucro_atual < 0:
                return valor
            return valor
        return valor

    def calcularValorEntradaGeral(self):
        if self.pocentagem_banca_para_entrada:
            return int(self.balance * (self.valor_aposta / 100))
        return self.valor_aposta

    def calcularGale(self, investimento, fator, gale_atual):
        for i in range(gale_atual):
            investimento = investimento * fator
            print('gale: ', i, investimento)

        return investimento

    def processarSinalDireto(self, item, atualizar):
        if atualizar:
            pegarPayoutSinais(item['moeda'], self, inteface)
        try:
            if self.verificarLiberacaoDeEntrada(item['time'], item['moeda']) == False:
                return False
            else:
                valor_aposta = self.calcularValorEntrada()
                if self.gale_proximo_sinal:
                    if self.gale_atual > 0:
                        valor_aposta = self.calcularGale(valor_aposta, self.fator_gale, self.gale_atual)
                        self.logs.append('ENTRADA GALE = CICLO: ' + str(self.gale_atual) + ' ATIVO: ' + item['moeda'] + ' VALOR: ' + str(valor_aposta))
                    self.abrirOrdem(item['direcao'], item['moeda'], valor_aposta, 0)
                else:
                    self.abrirOrdem(item['direcao'], item['moeda'], valor_aposta, self.gale)
        except Exception as error:
            try:
                print('Erro processar sinal', error)
                self.logs.append('Erro processar sinal: ' + item['time'] + ' ' + item['moeda'])
            finally:
                error = None
                del error

    def processarSinal(self, item, atualizar=False):
        _thread.start_new_thread(self.processarSinalDireto, (item, atualizar))

    def abrirOrdem(self, direcao, moeda, valor_aposta, gale):
        self.alertas.append('abrir orderm ' + dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        print('abrirOrdem', moeda, direcao, valor_aposta)
        inteface.entrada(self, direcao, moeda, self.time_frame, valor_aposta, self.fator_gale, gale)

    def setConfig(self, config):
        self.time_zone = str(config['time_zone'])
        self.valor_aposta = float(config['valor_aposta'])
        self.time_frame = int(config['time_frame'])
        self.fator_gale = float(config['fator_gale'])
        self.delay = int(config['delay'])
        self.delay_gale = int(config['delay_gale'])
        self.gale_turbo = bool(config['gale_turbo'])
        self.gale = int(config['gale'])
        self.limit_de_ganho = float(config['limit_de_ganho'])
        self.limit_de_perda = float(config['limit_de_perda'])
        self.payout_minimo = float(config['payout_minimo'])
        self.pocentagem_banca_para_entrada = bool(config['pocentagem_banca_para_entrada'])
        self.pocentagem_banca_para_gestao_perda = bool(config['pocentagem_banca_para_gestao_perda'])
        self.pocentagem_banca_para_gestao_ganho = bool(config['pocentagem_banca_para_gestao_ganho'])
        self.otc = bool(config['otc'])
        self.gale_proximo_sinal = bool(config['gale_proximo_sinal'])
        if bool(config['horario_servidor']):
            self.horario_servidor = False
        else:
            self.horario_servidor = True
        self.ativar_analise_medias = bool(config['ativar_analise_medias'])
        self.periodo_media_lenta = int(config['periodo_media_lenta'])
        self.tipo_media_lenta = str(config['tipo_media_lenta'])
        self.periodo_media_rapida = int(config['periodo_media_rapida'])
        self.tipo_media_rapida = str(config['tipo_media_rapida'])
        self.tendencia_time_frame = int(config['tendencia_time_frame'])
        self.soro_perda_maxima = float(config['soro_perda_maxima'])
        self.soro_porc_do_lucro = float(config['soro_porc_do_lucro'])
        self.soro_qnt_de_ciclos = int(config['soro_qnt_de_ciclos'])

    def addListaSinal(self, lista, liberar_repeticao):
        tratarLista(self, lista, liberar_repeticao)
        return self.lista_sinais

    def removerItem(self, item):
        removerDaLista(self.lista_sinais, item)

    def atualizarLimitesConfig(self, balance):
        self.valor_inical = balance
        if self.pocentagem_banca_para_gestao_ganho == True:
            self.limit_de_ganho_balance = balance + balance * (self.limit_de_ganho / 100)
        else:
            self.limit_de_ganho_balance = balance + self.limit_de_ganho
        if self.pocentagem_banca_para_gestao_perda == True:
            self.limit_de_perda_balance = balance - balance * (self.limit_de_perda / 100)
        else:
            self.limit_de_perda_balance = balance - self.limit_de_perda

    def atualizarLimites(self, inicial):
        balance, currency = inteface.config()
        self.currency = currency
        self.balance = balance
        if inicial:
            self.atualizarLimitesConfig(balance)

    def timestamp_converter(self, x):
        hora = datetime.strptime(datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        hora = hora.replace(tzinfo=(tz.gettz('GMT')))
        hora = hora.astimezone(tz.gettz(self.time_zone))
        return (
         str(hora)[:-6], (dt.datetime.utcnow() - datetime.utcfromtimestamp(x)).total_seconds())

    def getStatus(self):
        self.ultimo_status_verificado = dt.datetime.utcnow()
        return {'versao':self.versao, 
         'ordens':self.ordens, 
         'gale_proximo_sinal':self.gale_proximo_sinal, 
         'ultimo_status_verificado':str(self.ultimo_status_verificado), 
         'venciemento':self.venciemento, 
         'time_zone':self.time_zone, 
         'tipo':self.tipo, 
         'dif_em_seg':self.diff_seg_servidor_local, 
         'email':self.email, 
         'status':self.status, 
         'ativo':inteface.conectado(), 
         'valor':self.balance, 
         'proximo_sinal':oproximoSinal(self.lista_sinais, self), 
         'sinais':self.lista_sinais, 
         'logs':self.logs, 
         'alertas':self.alertas, 
         'stop_loss':self.limit_de_perda_balance, 
         'stop_gain':self.limit_de_ganho_balance, 
         'valor_inicial':self.valor_inical}

    def podeContinuarRisco(self):
        if self.limit_de_ganho > 0:
            if self.balance > self.limit_de_ganho_balance:
                return False
        if self.limit_de_perda > 0:
            if self.balance < self.limit_de_perda_balance:
                return False
        return True

    def verificarLiberacaoDeEntrada(self, time, moeda):
        diff_seg = (dt.datetime.utcnow() - self.ultimo_status_verificado).total_seconds()
        if diff_seg > 1800:
            self.logs.append('Cancelado, robô com problema de sincronização (STATUS): ' + time + ' ' + moeda)
            return False
        if self.diff_seg_servidor_local > 240:
            self.logs.append('Cancelado, horárido do computador distante do horário da corretora: ' + time + ' ' + moeda)
            return False
        if self.podeContinuarRisco() == False:
            self.logs.append('Cancelado pelo Gerenciamento de Banca: ' + time + ' ' + moeda)
            return False
        if inteface.conectado() == False:
            self.logs.append('Robo desconectado: ' + time + ' ' + moeda)
            return False
        return True

    def setDebug(self, status):
        self.debug = status

    def setUser(self, email, senha, tipo):
        self.email = email
        self.senha = senha
        self.tipo = tipo

    def desconecarApi(self):
        self.email = ''
        self.ativo = False
        self.gale_proximo_sinal = 0
        self.status = 'Desconectado'
        inteface.desconectar()

    def onStart(self):
        print('onStart')
        if inteface.conectado() == True:
            self.status = 'Conectado'
        self.atualizarLimites(True)
        self.ativo = inteface.conectado()
        if self.startRobo == False:
            self.startRobo = True
            _thread.start_new_thread(iniciarRobo, ('job', self, inteface, analise))
            _thread.start_new_thread(loopIndicadores, ('analise', self, inteface))

    def reconectar(self):
        print('\n>>> Reconectar ', self.email, self.ativo)
        diff_seg = (dt.datetime.utcnow() - self.ultimo_reconectar).total_seconds()
        print('\n >>> Reconectar diff:', diff_seg, self.email, self.ativo)
        if self.email != '':
            if diff_seg > 60:
                if self.ativo:
                    self.ultimo_reconectar = dt.datetime.utcnow()
                    self.logs.append('Tentativa de reconecatar... diff_seg: ' + str(diff_seg))
                    inteface.conectar(self.email, self.senha, self.tipo, self)

    def conectar(self):
        self.ativo = False
        self.gale_proximo_sinal = 0
        inteface.conectar(self.email, self.senha, self.tipo, self)