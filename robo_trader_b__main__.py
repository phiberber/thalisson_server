# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 16:30:00) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: robo_trader_b.py
# Compiled at: 2020-05-21 13:25:44
# Size of source mod 2**32: 9693 bytes
from bottle import route, run, response, request, post
import bottle
from datetime import datetime, tzinfo, timezone
import datetime as dt
from datetime import date
from sys import exit
from dateutil import tz
import time, json, sys, os
from worker import Worker
import jwt
secret = 'ass_app_1mk_5736'
robo = Worker()
import pandas as pd, numpy as np

def blockPrint():
    sys.stdout = open(os.devnull, 'w')


def validarToken(token):
    try:
        informacoes = jwt.decode(token, secret, algorithm='HS256')
        robo.venciemento = informacoes['vencimento']
        a = dt.datetime.now()
        b = datetime.strptime(informacoes['vencimento'], '%d-%m-%Y %H:%M')
        if a > b:
            return False
        return informacoes['email']
    except:
        print('Outro erro!', token)
        return False


@post('/status')
def status():
    response.content_type = 'application/json'
    postdata = request.body.read()
    config = json.loads(postdata)
    return json.dumps(robo.getStatus())


@post('/teste')
def statusTeste():
    response.content_type = 'application/json'
    postdata = request.body.read()
    config = json.loads(postdata)
    email = validarToken(config['token'])
    lista = []
    direcao = 'PUT'
    for i in range(8):
        x = time.time() + 3 + i * 60
        hora = datetime.strptime(datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
        hora = hora.replace(tzinfo=(tz.gettz('GMT')))
        hora = hora.astimezone(tz.gettz(robo.time_zone))
        hora = hora.strftime('%d-%m-%Y %H:%M')
        if direcao == 'CALL':
            direcao = 'PUT'
        else:
            direcao = 'CALL'
        lista.append(json.loads('{"time": "' + hora + '" , "moeda":"EURUSD" , "direcao":"' + direcao + '"}'))

    if email == False:
        return json.dumps({'error': 'Token não válido'})
    robo.addListaSinal(lista, True)
    return json.dumps(robo.getStatus())


@post('/ordem')
def ordemDireta():
    response.content_type = 'application/json'
    postdata = request.body.read()
    data = json.loads(postdata)
    try:
        print(data)
        email = validarToken(data['token'])
        if email == False:
            return json.dumps({'error': 'Token não válido'})
        else:
            ordem = data['ordem']
            if ordem['time'] == 'agora':
                robo.processarSinal(ordem, True)
            else:
                robo.addListaSinal([ordem], True)
    except Exception as error:
        try:
            print('ADD_ORDEM:', error)
        finally:
            error = None
            del error

    return json.dumps(robo.getStatus())


@post('/config')
def status():
    response.content_type = 'application/json'
    postdata = request.body.read()
    config = json.loads(postdata)
    robo.setConfig(config)
    print('----Dentro', config)
    atula_config = {'valor_aposta':robo.valor_aposta, 
     'time_zone':robo.time_zone, 
     'horario_servidor':robo.horario_servidor, 
     'time_frame':robo.time_frame, 
     'limit_de_perda':robo.limit_de_perda, 
     'gale_proximo_sinal':robo.gale_proximo_sinal, 
     'limit_de_ganho':robo.limit_de_ganho, 
     'pocentagem_banca_para_entrada':robo.pocentagem_banca_para_entrada, 
     'pocentagem_banca_para_gestao_perda':robo.pocentagem_banca_para_gestao_perda, 
     'pocentagem_banca_para_gestao_ganho':robo.pocentagem_banca_para_gestao_ganho, 
     'fator_gale':robo.fator_gale, 
     'delay':robo.delay, 
     'payout_minimo':robo.payout_minimo, 
     'otc':robo.otc, 
     'gale':robo.gale, 
     'limit_de_ganho':robo.limit_de_ganho, 
     'limit_de_perda':robo.limit_de_perda}
    return json.dumps({'status':robo.getStatus(),  'config':atula_config})


@post('/sinais')
def lista():
    response.content_type = 'application/json'
    return json.dumps(robo.getStatus())


@post('/remover')
def remover():
    postdata = request.body.read()
    item = json.loads(postdata)
    robo.removerItem(item)
    response.content_type = 'application/json'
    return json.dumps(robo.getStatus())


@post('/carregar_lista')
def lista():
    response.content_type = 'application/json'
    postdata = request.body.read()
    dados = json.loads(postdata)
    print('----Dentro', dados['lista'])
    email = validarToken(dados['token'])
    if email == False:
        return json.dumps({'error': 'Token não válido'})
    lista = []
    for item in dados['lista']:
        lista.append(item)

    liberar_repeticao = False
    if 'liberar_repeticao' in dados:
        liberar_repeticao = dados['liberar_repeticao']
    robo.addListaSinal(lista, liberar_repeticao)
    return json.dumps(robo.getStatus())


@post('/logout')
def logout():
    robo.desconecarApi()
    response.content_type = 'application/json'
    return json.dumps(robo.getStatus())


@post('/login')
def analise():
    response.content_type = 'application/json'
    postdata = request.body.read()
    user = json.loads(postdata)
    email = validarToken(user['token'])
    if email == False:
        return json.dumps({'error': 'Token não válido, Verifique a validade de sua licença'})
    print('----Dentro', user, email)
    robo.setUser(email, user['senha'], user['tipo'])
    resposta = robo.conectar()
    if robo.ativo == False:
        return json.dumps({'error': 'Login falhou'})
    return json.dumps(robo.getStatus())


@post('/exit')
def sairDoApp():
    print('on close()')
    try:
        robo.desconecarApi()
        sys.stderr.close()
    except Exception as error:
        try:
            print('FECHAR:', error)
        finally:
            error = None
            del error

    response.content_type = 'application/json'
    return json.dumps({'close': True})


app = bottle.app()
porta = 7000
if len(sys.argv[1]) > 1:
    porta = int(sys.argv[1])
print(sys.argv, 'localhost:' + str(porta))
bottle.run(app=app, host='127.0.0.1', port=porta)