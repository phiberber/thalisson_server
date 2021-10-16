# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 16:30:00) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: C:\Users\Developer\proijects\bot-python\update_ativos.py
# Compiled at: 2020-05-09 00:46:26
# Size of source mod 2**32: 7470 bytes
import _thread, time
from datetime import datetime, tzinfo, timezone
import datetime as dt
from datetime import date
from lista_sinais import *

def payout(API, profit_all, par, tipo, timeframe=1):
    try:
        if tipo == 'turbo' or tipo == 'binary':
            return int(100 * profit_all[par][tipo])
        if tipo == 'digital':
            API.subscribe_strike_list(par, timeframe)
            while True:
                d = API.get_digital_current_profit(par, timeframe)
                if d != False:
                    d = int(d)
                    break
                time.sleep(1)

            API.unsubscribe_strike_list(par, timeframe)
            return d
    except Exception as error:
        try:
            print('payout', error)
            return 0
        finally:
            error = None
            del error


def atualizarHorario(API, worker):
    if API == False:
        return
    x = API.get_server_timestamp() + 1
    if x:
        worker.diff_seg_servidor_local = (dt.datetime.utcnow() - datetime.utcfromtimestamp(x)).total_seconds()


def atualizarLista(API, interface, worker):
    if not worker.ativo == False:
        if interface.API == False:
            return
        if interface.API.check_connect() == False:
            return
        novo = dt.datetime.now().timestamp() + worker.diff_seg_servidor_local
        seg_ = int(datetime.fromtimestamp(novo).strftime('%S'))
        if seg_ > 40 or seg_ < 15:
            return
        if interface.API.check_connect() == False:
            return
    else:
        try:
            time_up_balance = (dt.datetime.utcnow() - worker.balance_update).total_seconds()
            atualizarHorario(API, worker)
            if time_up_balance > 30:
                worker.balance = API.get_balance()
                worker.balance_update = dt.datetime.utcnow()
        except Exception as error:
            try:
                print('erro atualizarLista()', error)
            finally:
                error = None
                del error

    atualiarAtivosListaDireto(API, interface, worker, False)


def atualiarAtivosListaDireto(API, interface, worker, direto):
    try:
        agora = dt.datetime.utcnow()
        tempo = 600
        total_ativos = len(interface.ativos)
        if worker.ultimo_update != 0:
            tempo = (dt.datetime.utcnow() - worker.ultimo_update).total_seconds()
        if worker.liberarProcessamento == True:
            if direto == False:
                return
        if tempo < 180:
            if total_ativos > 0:
                if direto == False:
                    return
        worker.ultimo_update = dt.datetime.utcnow()
        ALL_Asset = API.get_all_open_time()
        ativos = []
        for type_name, data in ALL_Asset.items():
            for Asset, value in data.items():
                if not value['open'] or type_name == 'digital' or type_name == 'turbo':
                    ativo_foco = getItemTipo(type_name, Asset, interface.ativos, True)
                    ativos.append(ativo_foco)

        print('FINAL ATIVOS', len(ativos))
        interface.ativos = ativos
    except Exception as error:
        try:
            print('erro lista ativos final', error)
        finally:
            error = None
            del error

    return True


def getItemTipo(tipo, moeda, lista, criar):
    for item in lista:
        if item['moeda'] == moeda or item['moeda'] == moeda + '-OTC':
            if tipo == item['tipo']:
                return item

    if criar:
        return {'moeda':moeda, 
         'tipo':tipo,  'payout':0,  'open':True}
    return False


def ativosNaMemoria(moeda, lista):
    digital = False
    turbo = False
    for item in lista:
        if not item['moeda'] == moeda:
            if item['moeda'] == moeda + '-OTC':
                if item['tipo'] == 'digital':
                    digital = True
            if item['moeda'] == moeda or item['moeda'] == moeda + '-OTC':
                if item['tipo'] == 'turbo':
                    turbo = True

    if digital:
        if turbo:
            return True
    return False


def pegarPayoutSinais(moeda, worker, interface):
    worker.liberarProcessamento = True
    if worker.ativo == False:
        return
    if interface.API == False:
        return
    if ativosNaMemoria(moeda, interface.ativos) == False:
        atualiarAtivosListaDireto(interface.API, interface, worker, True)
    profit_all = interface.API.get_all_profit()
    diff = 10000
    item_turbo = getItemTipo('turbo', moeda, interface.ativos, False)
    if item_turbo:
        if 'update' in item_turbo:
            diff = (dt.datetime.utcnow() - item_turbo['update']).total_seconds()
        if diff > 30 or item_turbo['payout']:
            item_turbo['payout'] = payout(interface.API, profit_all, item_turbo['moeda'], 'turbo', worker.time_frame)
            item_turbo['update'] = dt.datetime.utcnow()
    diff = 10000
    item_digital = getItemTipo('digital', moeda, interface.ativos, False)
    if item_digital:
        if 'update' in item_digital:
            diff = (dt.datetime.utcnow() - item_digital['update']).total_seconds()
        if diff > 30 or item_digital['payout'] == 0:
            item_digital['payout'] = payout(interface.API, profit_all, item_digital['moeda'], 'digital', worker.time_frame)
            item_digital['update'] = dt.datetime.utcnow()


def iniciarUpdateAtivos(nome, interface, worker):
    atualizarHorario(interface.API, worker)
    worker.ultimo_update = 0
    worker.balance_update = dt.datetime.utcnow()
    try:
        if interface.API != False:
            atualizarLista(interface.API, interface, worker)
    except Exception as error:
        try:
            print('erro iniciarUpdateAtivos()', error)
        finally:
            error = None
            del error

    while True:
        try:
            atualizarLista(interface.API, interface, worker)
        except Exception as error:
            try:
                print('erro iniciarUpdateAtivos()', error)
            finally:
                error = None
                del error

        time.sleep(10)