import ccxt
import datetime
import time

exchange = ccxt.binance()  # Создаем объект биржи binance

ticker = exchange.fetch_ticker('ETH/USDT')  # Получаем текущую цену ETHUSDT
current_price = ticker['last']

while True:  # Основной цикл программы

    time.sleep(1)  # Ждем 1 секунду, чтобы не перегружать биржу запросами

    ticker = exchange.fetch_ticker('ETH/USDT')  # Получаем текущую цену ETHUSDT
    current_price = ticker['last']

    past_time = datetime.datetime.now() - datetime.timedelta(
        minutes=60)  # Получаем время 60 минут назад

    past_ticker = exchange.fetch_ohlcv('ETH/USDT', '1m',
                                       since=int(past_time.timestamp() * 1000),
                                       limit=1)  # Получаем цену ETHUSDT 60 минут назад
    past_price = past_ticker[0][4]

    price_change = (
                    current_price / past_price - 1) * 100  # Определяем процентное изменение цены

    if abs(price_change) > 1:  # Если процентное изменение больше 1%, выводим сообщение в консоль
        if price_change > 0:
            print("Цена ETHUSDT выросла на", round(price_change, 2),
                  "% за последний час")
        else:
            print("Цена ETHUSDT упала на", round(price_change, 2),
                  "% за последний час")
