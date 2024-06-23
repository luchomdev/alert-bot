from binance.client import Client
import time
import telebot

bot_token = '6464200383:AAGyetO2qnEe6J-f0_kfwCbJC8iDxhH1pYo'
chat_id = '1269436309'

variacion = 5  # Variacion en los ultimos 30 minutos en porcentaje
variacion_100 = 8  # Variacion en los ultimos 30 minutos en porcentaje si tiene menos de 100k de volumen
variacionfast = 3  # Variacion en los ultimos 2 minutos en porcentaje

client = Client('','', tld='com')

def enviar_mensaje(mensaje):
  bot = telebot.TeleBot(bot_token)
  bot.send_message(chat_id, mensaje)

def buscarticks():
    ticks = []
    lista_ticks = client.futures_symbol_ticker() # traer todas las monedas de futuros de binace
    print('Numero de monedas encontradas #' + str(len(lista_ticks)))

    for tick in lista_ticks:
        if tick['symbol'][-4:] != 'USDT': # seleccionar todas las monedas en el par USDT
            continue
        ticks.append(tick['symbol'])

    print('Numero de monedas encontradas en el par USDT: #' + str(len(ticks)))

    return ticks

def get_klines(tick):
    klines = client.futures_klines(symbol=tick, interval=Client.KLINE_INTERVAL_1MINUTE, limit=30)
    return klines

def infoticks(tick):
    info = client.futures_ticker(symbol=tick)
    return info

def human_format(volumen):
    magnitude = 0
    while abs(volumen) >= 1000:
        magnitude += 1
        volumen /= 1000.0
    return '%.2f%s' % (volumen, ['', 'K', 'M', 'G', 'T', 'P'][magnitude])

def porcentaje_klines(tick, klines, knumber):
    inicial = float(klines[0][4])
    final = float(klines[knumber][4])

    # LONG
    if inicial > final:
        result = round(((inicial - final) / inicial) * 100, 2)
        if result >= variacion:
            info = infoticks(tick)
            tipo = "LONG"
            volumen = float(info['quoteVolume'])
            if volumen > 100000000 or result >= variacion_100:
                print('LONG: '+tick)
                print('Variacion: ' + str(result) + '%')
                print('Volumen: ' + human_format(volumen))
                print('Precio max: ' + info['highPrice'])
                print('Precio min: ' + info['lowPrice'])
                print('')
                mensaje = f'**🟢{tipo} - {tick}**\n\n'
                mensaje += f'**Variación:** {str(result)}%\n'
                mensaje += f'**Volumen:** {human_format(volumen)}\n'
                mensaje += f'**Precio máximo:** {info["highPrice"]}\n'
                mensaje += f'**Precio mínimo:** {info["lowPrice"]}\n'
                enviar_mensaje(mensaje)

    # SHORT
    if final > inicial:
        result = round(((final - inicial) / inicial) * 100, 2)
        if result >= variacion:
            info = infoticks(tick)
            tipo = "SHORT"
            volumen = float(info['quoteVolume'])
            if volumen > 100000000 or result >= variacion_100:
                print('SHORT: ' + tick)
                print('Variacion: ' + str(result) + '%')
                print('Volumen: ' + human_format(volumen))
                print('Precio max: ' + info['highPrice'])
                print('Precio min: ' + info['lowPrice'])
                print('')
                mensaje = f'**🔴{tipo} - {tick}**\n\n'
                mensaje += f'**Variación:** {str(result)}%\n'
                mensaje += f'**Volumen:** {human_format(volumen)}\n'
                mensaje += f'**Precio máximo:** {info["highPrice"]}\n'
                mensaje += f'**Precio mínimo:** {info["lowPrice"]}\n'
                enviar_mensaje(mensaje)

    # FAST
    if knumber >= 3:
        inicial = float(klines[knumber-2][4])
        final = float(klines[knumber][4])
        if inicial < final:
            result = round(((final - inicial) / inicial) * 100, 2)
            if result >= variacionfast:
                info = infoticks(tick)
                volumen = float(info['quoteVolume'])
                print('FAST SHORT!: ' + tick)
                print('Variacion: ' + str(result) + '%')
                print('Volumen: ' + human_format(volumen))
                print('Precio max: ' + info['highPrice'])
                print('Precio min: ' + info['lowPrice'])
                print('')




while True:
    ticks = buscarticks()
    print('Escaneando monedas...')
    print('')
    for tick in ticks:
        klines = get_klines(tick)
        knumber = len(klines)
        if knumber > 0:
            knumber = knumber - 1
            porcentaje_klines(tick, klines, knumber)
    print('Esperando 30 segundos...')
    print('')
    time.sleep(30)
