import time
import random
import requests
from datetime import datetime, timedelta
import pytz
from flask import Flask

app = Flask(__name__)

BOT_TOKEN = 'YOUR_BOT_TOKEN'
CHANNEL_ID = 'YOUR_CHANNEL_ID'
OWNER_ID = YOUR_OWNER_ID
OFFSET = None
AUTO_POSTING = False

CURRENCY_PAIRS = [
    'EURUSD', 'AUDCHF', 'AUDUSD', 'CADCHF', 'EURGBP', 'GBPAUD', 'GBPJPY', 'GBPUSD',
    'USDJPY', 'USDCHF', 'EURCHF', 'AUDCAD', 'NZDUSD', 'EURJPY', 'CHFJPY', 'AUDJPY',
    'CADJPY', 'EURAUD', 'EURCAD', 'USDCNH', 'USDCAD', 'USDSGD',
    'USDTRY', 'USDMYR', 'USDTHB', 'USDEGP', 'USDARS', 'USDBRL', 'USDMXN',
    'USDPKR', 'USDIDR', 'USDBDT', 'YERUSD', 'LBPUSD', 'AEDCNY',
    'SARCNY', 'QARCNY', 'NGNUSD', 'USDPHP', 'USDVND', 'UAHUSD', 'USDCOP'
]

emoji_map = {
    'AUD': '🇦🇺', 'CHF': '🇨🇭', 'EUR': '🇪🇺', 'USD': '🇺🇸', 'GBP': '🇬🇧',
    'JPY': '🇯🇵', 'CAD': '🇨🇦', 'NZD': '🇳🇿', 'CNH': '🇨🇳', 'TRY': '🇹🇷',
    'MYR': '🇲🇾', 'THB': '🇹🇭', 'EGP': '🇪🇬', 'ARS': '🇦🇷', 'BRL': '🇧🇷',
    'MXN': '🇲🇽', 'PKR': '🇵🇰', 'IDR': '🇮🇩', 'BDT': '🇧🇩', 'YER': '🇾🇪',
    'LBP': '🇱🇧', 'AED': '🇦🇪', 'SAR': '🇸🇦', 'QAR': '🇶🇦', 'NGN': '🇳🇬',
    'PHP': '🇵🇭', 'VND': '🇻🇳', 'UAH': '🇺🇦', 'COP': '🇨🇴'
}

PHOTO_BUY = 'https://i.imgur.com/sNdCYu9.jpeg'
PHOTO_SELL = 'https://i.imgur.com/nfhSHDG.jpeg'

BG_TZ = pytz.timezone('Europe/Sofia')

def send_photo_with_caption(chat_id, photo_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    data = {
        'chat_id': chat_id,
        'photo': photo_url,
        'caption': caption,
        'parse_mode': 'HTML'
    }
    requests.post(url, data=data)

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    requests.post(url, data=data)

def get_updates(offset):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {'timeout': 10, 'offset': offset}
    response = requests.get(url, params=params)
    return response.json()

def generate_signal():
    pair = random.choice(CURRENCY_PAIRS)
    signal = random.choice(['BUY', 'SELL'])
    price = round(random.uniform(0.5, 1.5), 5)
    signal_icon = "📈" if signal == 'BUY' else "📉"
    text = (
        f"Валутна двойка: {pair}\n"
        f"Сигнал: {signal} {signal_icon}\n"
        f"Цена: {price}"
    )
    return signal, text

def process_commands(updates):
    global AUTO_POSTING, OFFSET
    for update in updates.get('result', []):
        OFFSET = update['update_id'] + 1
        message = update.get('message', {})
        text = message.get('text', '')
        chat_id = message.get('chat', {}).get('id')
        user_id = message.get('from', {}).get('id')
        if user_id != OWNER_ID:
            continue
        if text == '/start':
            AUTO_POSTING = True
            send_message(chat_id, "✅ Автоматичното публикуване е активирано.")
        elif text == '/stop':
            AUTO_POSTING = False
            send_message(chat_id, "⏹ Автоматичното публикуване е спряно.")
        elif text == '/status':
            status = "✅ ВКЛ" if AUTO_POSTING else "❌ ВЫКЛ"
            send_message(chat_id, f"Статус: {status}")
        elif text == '/testpost':
            signal, signal_text = generate_signal()
            photo_url = PHOTO_BUY if signal == 'BUY' else PHOTO_SELL
            send_photo_with_caption(CHANNEL_ID, photo_url, signal_text)
            send_message(chat_id, "Тестовият сигнал е изпратен.")

@app.route('/')
def home():
    return "Bot is alive!"

if __name__ == "__main__":
    import threading

    def run_bot():
        global OFFSET
        while True:
            try:
                updates = get_updates(OFFSET)
                process_commands(updates)
                time.sleep(3)
            except Exception as e:
                print("Error:", e)
                time.sleep(5)

    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=8080)