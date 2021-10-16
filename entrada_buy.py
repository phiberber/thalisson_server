# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 16:30:00) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: C:\Users\Developer\proijects\bot-python\entrada_buy.py
# Compiled at: 2020-05-09 00:46:26
# Size of source mod 2**32: 12496 bytes
import _thread, time
from datetime import datetime
import datetime as dt
from datetime import date
from dateutil import tz

def primeiroNivelGale(threadName, id, inter, direcao, moeda, time_frame, valor_aposta, fator, gale, tipo, gale_atual, worker):
    if inter.API == False:
        return
        lucro = verificarResultado(inter.API, id, worker, tipo)
        worker.liberarProcessamento = True
        worker.movimentarSoro(lucro)
        if lucro > 0:
            worker.logs.append('Resultado Entrada: ' + moeda + ' LUCRO: ' + str(round(lucro, 2)) + ' id:' + str(id))
        else:
            worker.logs.append('Resultado Entrada: ' + moeda + ' PERDA: ' + str(round(lucro, 2)) + ' id:' + str(id))
        worker.balance = worker.balance + lucro
        if lucro <= 0 and fator > 0 and gale > 0 and gale_atual < gale:
            worker.balance = worker.balance - lucro
            gale_atual = gale_atual + 1
            investimento = worker.calcularGale(valor_aposta, fator, gale_atual)
            worker.logs.append('ENTRADA GALE = CICLO :' + str(gale_atual) + ' ATIVO: ' + moeda + ' VALOR: ' + str(round(investimento, 2)) + ' direcao: ' + direcao)
            check, id = entradaDireta(inter.API, direcao, moeda, time_frame, investimento, fator, gale, worker, tipo)
            sucesso = False
            if tipo == 'binary':
                sucesso = verificarStatusBinary(id, check, moeda, time_frame, worker)
            else:
                sucesso = verificarStatusDigital(id, check, moeda, time_frame, worker)
            if sucesso == True:
                primeiroNivelGale(threadName, id, inter, direcao, moeda, time_frame, valor_aposta, fator, gale, tipo, gale_atual, worker)
    else:
        worker.movimentarGaleSinal(lucro)
        worker.atualizarLimites(False)
    for par in worker.moedas_usadas:
        if par not in worker.moedas_live:
            inter.API.stop_candles_stream(par, 60)
            print('Close=>', par)


def verificarResultado(API, id, worker, tipo):
    lucro = 0
    if worker.gale_turbo:
        lucro = check_win_futuro(id, API, worker, tipo)
        if lucro < 0:
            return lucro
    try:
        if tipo == 'binary':
            lucro = API.check_win_v3(id)
        else:
            lucro = check_win_v3(id, API)
    except:
        print('>> erro em verificarResultado() ')

    return lucro


def buyDigital(inter, direcao, moeda, time_frame, valor_aposta, fator, gale, worker):
    worker.liberarProcessamento = True
    tipo = 'digital'
    check, id = entradaDireta(inter.API, direcao, moeda, time_frame, valor_aposta, fator, gale, worker, tipo)
    sucesso = verificarStatusDigital(id, check, moeda, time_frame, worker)
    if sucesso == True:
        primeiroNivelGale('Thread-1', id, inter, direcao, moeda, time_frame, valor_aposta, fator, gale, tipo, 0, worker)
    return sucesso


def buyBinary(inter, direcao, moeda, time_frame, valor_aposta, fator, gale, worker):
    worker.liberarProcessamento = True
    tipo = 'binary'
    check, id = entradaDireta(inter.API, direcao, moeda, time_frame, valor_aposta, fator, gale, worker, tipo)
    sucesso = verificarStatusBinary(id, check, moeda, time_frame, worker)
    if sucesso == True:
        primeiroNivelGale('Thread-1', id, inter, direcao, moeda, time_frame, valor_aposta, fator, gale, tipo, 0, worker)
    return sucesso


def verificarStatusDigital(id, check, moeda, time_frame, worker):
    momento = datetime.strptime(dt.datetime.now(tz.gettz(worker.time_zone)).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    try:
        if type(id) == int:
            if id > 0:
                worker.logs.append('Entrada digital: ' + moeda + ' timeframe: ' + str(time_frame) + 'min, H: ' + str(momento) + ' id:' + str(id))
                return True
        worker.logs.append('Erro na entrada digital: ' + moeda + ' timeframe: ' + str(time_frame) + 'min, Não foi possível abrir uma negociação' + ' H: ' + str(momento))
        return False
    except Exception as error:
        try:
            print('verificarStatusDigital erro digital ', id, check, str(momento), error)
            return False
        finally:
            error = None
            del error


def verificarStatusBinary(id, check, moeda, time_frame, worker):
    momento = datetime.strptime(dt.datetime.now(tz.gettz(worker.time_zone)).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    try:
        if check:
            worker.logs.append('Entrada binary: ' + moeda + ' timeframe: ' + str(time_frame) + 'min, H: ' + str(momento) + ' id:' + str(id))
            return True
        worker.logs.append('Erro na entrada binary: ' + moeda + ' timeframe: ' + str(time_frame) + 'min, Não foi possível abrir uma negociação' + ' H: ' + str(momento))
        return False
    except Exception as error:
        try:
            print('verificarStatusBinary erro binary ', id, check, str(momento), error)
            return False
        finally:
            error = None
            del error


def entradaDireta(API, direcao, moeda, time_frame, valor_aposta, fator, gale, worker, tipo):
    momento = datetime.strptime(dt.datetime.now(tz.gettz(worker.time_zone)).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    if worker.verificarLiberacaoDeEntrada(str(momento), moeda) == False:
        worker.liberarProcessamento = False
        return False
    if valor_aposta < 1:
        worker.liberarProcessamento = False
        worker.logs.append('Erro na entrada, valor abaixo do mínimo: valor= ' + str(round(valor_aposta, 2)))
        return (False, 0)
    print('>>>>>>>>>>> buy <<<<<<<  valor_aposta:', valor_aposta, 'moeda ', moeda, 'direcao ', direcao, 'time_frame ', time_frame, 'tipo', tipo)
    try:
        if tipo == 'binary':
            check, id = API.buy(round(valor_aposta, 2), moeda, direcao, time_frame)
            worker.ordens.append({'moeda':moeda,  'direcao':direcao,  'valor':round(valor_aposta, 2),  'tipo':tipo,  'gale':gale})
            worker.liberarProcessamento = False
            return (check, id)
        check, id = API.buy_digital_spot(moeda, round(valor_aposta, 2), direcao, time_frame)
        worker.ordens.append({'moeda':moeda,  'direcao':direcao,  'valor':round(valor_aposta, 2),  'tipo':tipo,  'gale':gale})
        worker.liberarProcessamento = False
        return (check, id)
    except Exception as error:
        try:
            print('An exception occurred ' + tipo, error)
            worker.liberarProcessamento = False
            return (False, 0)
        finally:
            error = None
            del error


def check_win_v3(id, API):
    if id != 'error':
        try:
            while 1:
                check, win = API.check_win_digital_v2(id)
                if check == True:
                    break

            return win
        except Exception as error:
            try:
                print('check_win_v3 ', error)
                return 0
            finally:
                error = None
                del error

    else:
        return 0


def check_win_futuro(position_id, API, worker, tipo):
    try:
        time.sleep(10)
        orden = API.get_async_order(position_id)
        par = 'moeda'
        preco_de_compra = 0
        time_final_compra = 0
        direcao = 'call'
        valor_investimento = 0
        if tipo == 'binary':
            par = orden['option-opened']['msg']['active']
            preco_de_compra = orden['option-opened']['msg']['value']
            time_final_compra = orden['option-opened']['msg']['expiration_time']
            direcao = orden['option-opened']['msg']['direction']
            valor_investimento = orden['option-opened']['msg']['amount']
        else:
            par = orden['position-changed']['msg']['raw_event']['instrument_underlying']
            preco_de_compra = orden['position-changed']['msg']['raw_event']['open_underlying_price']
            time_final_compra = orden['position-changed']['msg']['raw_event']['instrument_expiration']
            direcao = orden['position-changed']['msg']['raw_event']['instrument_dir']
            valor_investimento = orden['position-changed']['msg']['invest']
        worker.moedas_live.append(par)
        if par not in worker.moedas_usadas:
            worker.moedas_usadas.append(par)
        print('\n\n >> ', par, 'to', time_final_compra, direcao, 'valor_investimento', valor_investimento, 'preco_de_compra', preco_de_compra, '\n')
        API.start_candles_stream(par, 1, 1)
        time.sleep(5)
        varlor_abertura_proxima_vela = 0
        if len(str(time_final_compra)) > 10:
            time_final_compra = time_final_compra / 1000
            print('TESTE 1000 time')
        time_final_compra = time_final_compra - worker.delay_gale
        fim_compra = datetime.utcfromtimestamp(time_final_compra)
        fim_compra_limit = datetime.utcfromtimestamp(time_final_compra + 3)
        print('fim_compra', fim_compra, 'fim_compra_limit', fim_compra_limit, 'dalay', worker.delay_gale)
        while varlor_abertura_proxima_vela == 0:
            time.sleep(0.05)
            vela = API.get_realtime_candles(par, 1)
            for velas in vela:
                hora_inicio_vela = datetime.utcfromtimestamp(vela[velas]['from'])
                if hora_inicio_vela >= fim_compra:
                    print('hora >>>>', datetime.strptime(dt.datetime.now(tz.gettz(worker.time_zone)).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S'))
                    varlor_abertura_proxima_vela = vela[velas]['open']
                if worker.now() > fim_compra_limit:
                    print('Caiu fora time')
                    return 0

        lucro_apurado = valor_investimento * 0.8
        worker.moedas_live.remove(par)
        if varlor_abertura_proxima_vela == 0:
            return 0
        if varlor_abertura_proxima_vela > preco_de_compra:
            if direcao == 'call':
                print('lucro na operação', lucro_apurado)
                return lucro_apurado
        if varlor_abertura_proxima_vela < preco_de_compra:
            if direcao == 'put':
                print('lucro na operação', lucro_apurado)
                return lucro_apurado
        print('PREJUISO', valor_investimento * -1)
        return valor_investimento * -1
    except Exception as error:
        try:
            print('\n\n >>check_win_futuro ', error)
            return 0
        finally:
            error = None
            del error