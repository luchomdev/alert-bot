from flask import Flask
import threading
import time
import os
from binance.client import Client
import telebot

# Inicializar Flask
app = Flask(__name__)

# Ruta para el chequeo de salud
@app.route('/')
def health_check():
    return "El bot está funcionando", 200

# Función para ejecutar el bot
def run_bot():
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    binance_api_key = os.getenv('BINANCE_API_KEY')
    binance_api_secret = os.getenv('BINANCE_API_SECRET')

    variacion = 1
    variacion_100 = 1
    variacionfast = 3

    client = Client(binance_api_key, binance_api_secret, tld='com')

    def enviar_mensaje(mensaje):
        bot = telebot.TeleBot(bot_token)
        bot.send_message(chat_id, mensaje)

    def buscarticks():
        ticks = []
        lista_ticks = client.futures_symbol_ticker()
        print('Número de monedas encontradas #' + str(len(lista_ticks)))

        for tick in lista_ticks:
            if tick['symbol'][-4:] != 'USDT':
                continue
            ticks.append(tick['symbol'])

        print('Número de monedas encontradas en el par USDT: #' + str(len(ticks)))

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
                    print('LONG: ' + tick)
                    print('Variación: ' + str(result) + '%')
                    print('Volumen: ' + human_format(volumen))
                    print('Precio máx: ' + info['highPrice'])
                    print('Precio min: ' + info['lowPrice'])
                    print('')
                    mensaje = f'**🟢{tipo} - {tick}**\n\n'
                    mensaje += f'**Variación:** {str(result)}%\n'
                    mensaje += f'**Volumen:** {human_format(volumen)}%\n'
                    mensaje += f'**Precio máx:** {info["highPrice"]}\n'
                    mensaje += f'**Precio min:** {info["lowPrice"]}\n'
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
                    print('Variación: ' + str(result) + '%')
                    print('Volumen: ' + human_format(volumen))
                    print('Precio máx: ' + info['highPrice'])
                    print('Precio min: ' + info['lowPrice'])
                    print('')
                    mensaje = f'**🔴{tipo} - {tick}**\n\n'
                    mensaje += f'**Variación:** {str(result)}%\n'
                    mensaje += f'**Volumen:** {human_format(volumen)}%\n'
                    mensaje += f'**Precio máx:** {info["highPrice"]}\n'
                    mensaje += f'**Precio min:** {info["lowPrice"]}\n'
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
                    print('Variación: ' + str(result) + '%')
                    print('Volumen: ' + human_format(volumen))
                    print('Precio máx: ' + info['highPrice'])
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

# Iniciar el bot en un hilo separado
bot_thread = threading.Thread(target=run_bot)
bot_thread.start()

# Iniciar el servidor Flask
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
