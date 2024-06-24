import os
from flask import Flask
import threading
import time
from binance.client import Client
import telebot
from dotenv import load_dotenv

load_dotenv()

# Obtener variables de entorno
bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')
binance_api_key = os.getenv('BINANCE_API_KEY')
binance_api_secret = os.getenv('BINANCE_API_SECRET')

# Inicializar Flask
app = Flask(__name__)

# Ruta para el chequeo de salud
@app.route('/')
def health_check():
    return "El bot está funcionando", 200

# Función para enviar mensaje de prueba
def test_bot_token():
    bot = telebot.TeleBot(bot_token)
    try:
        bot.send_message(chat_id, "Prueba de mensaje")
        print("Mensaje de prueba enviado con éxito")
    except Exception as e:
        print(f"Error al enviar mensaje de prueba: {e}")

# Función para ejecutar el bot
def run_bot():
    client = Client(binance_api_key, binance_api_secret, tld='com')

    while True:
        try:
            ticks = client.futures_symbol_ticker()
            for tick in ticks:
                if tick['symbol'].endswith('USDT'):
                    symbol = tick['symbol']
                    klines = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=30)
                    if len(klines) > 0:
                        knumber = len(klines) - 1
                        initial = float(klines[0][4])
                        final = float(klines[knumber][4])
                        result = round(((final - initial) / initial) * 100, 2)
                        
                        if result >= 1:  # Ejemplo de condición para enviar mensaje
                            bot = telebot.TeleBot(bot_token)
                            mensaje = f'Variación detectada en {symbol}: {result}%'
                            bot.send_message(chat_id, mensaje)
                            print(f'Mensaje enviado correctamente: {mensaje}')
            
            time.sleep(30)  # Espera 30 segundos antes de la próxima ejecución

        except Exception as e:
            print(f'Error al ejecutar el bot: {e}')
            time.sleep(60)  # Espera 60 segundos antes de intentar nuevamente

# Iniciar el bot en un hilo separado
if __name__ == "__main__":
    test_bot_token()  # Envía mensaje de prueba al iniciar la aplicación
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    app.run(host='0.0.0.0', port=8080)  # Inicia el servidor Flask en el puerto 8080
