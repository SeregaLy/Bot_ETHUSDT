import requests
import time
import threading
import pandas as pd
from binance.client import Client

client = Client()

def get_price(symbol: str) -> float:
    """Функция для получения текущей цены валюты"""
    url = 'https://api.binance.com/api/v3/ticker/price'
    params = {'symbol': symbol}
    response = requests.get(url, params=params)
    data = response.json()
    return float(data['price'])

def get_eth_btc_influence(symbol1, symbol2, window) -> float:
    """Функция для получения коэффициента влияния цены BTCUSDT на цену ETHUSDT"""
    prices1 = client.futures_klines(symbol=symbol1,
                                    interval=Client.KLINE_INTERVAL_1MINUTE,
                                    limit=window)
    prices2 = client.futures_klines(symbol=symbol2,
                                    interval=Client.KLINE_INTERVAL_1MINUTE,
                                    limit=window)

    # Создаем временные ряды из цен
    df1 = pd.DataFrame(prices1,
                       columns=['time', 'open', 'high', 'low', 'close',
                                'volume', 'close_time', 'quote_asset_volume',
                                'number_of_trades',
                                'taker_buy_base_asset_volume',
                                'taker_buy_quote_asset_volume', 'ignore'])
    df2 = pd.DataFrame(prices2,
                       columns=['time', 'open', 'high', 'low', 'close',
                                'volume', 'close_time', 'quote_asset_volume',
                                'number_of_trades',
                                'taker_buy_base_asset_volume',
                                'taker_buy_quote_asset_volume', 'ignore'])

    # Преобразуем цены в числовой формат и устанавливаем время как индекс
    df1['close'] = pd.to_numeric(df1['close'])
    df2['close'] = pd.to_numeric(df2['close'])
    df1['time'] = pd.to_datetime(df1['time'], unit='ms')
    df2['time'] = pd.to_datetime(df2['time'], unit='ms')
    df1.set_index('time', inplace=True)
    df2.set_index('time', inplace=True)

    # Вычисляем корреляцию между временными рядами
    corr = df1['close'].corr(df2['close'])
    return corr


def calculate_eth_price(exclude_btc_influence: float, symbol1, symbol2, window) -> float:
    """Функция для расчета цены ETHUSDT, исключив его движения, вызванные влиянием цены BTCUSDT"""
    eth_price = get_price('ETHUSDT')
    btc_price = get_price('BTCUSDT')
    eth_btc_influence = get_eth_btc_influence(symbol1, symbol2, window)
    eth_price -= (btc_price * eth_btc_influence * exclude_btc_influence)
    return eth_price


def monitor_price_change() -> None:
    """Функция для отслеживания изменения цены ETHUSDT и вывода сообщения в консоль"""
    exclude_btc_influence = 0 # Влияние на коэффициент влияния цены BTCUSDT на цену ETHUSDT
    while True:
        eth_price = calculate_eth_price(exclude_btc_influence, 'ETHUSDT', 'BTCUSDT', 600) # Время выборки из которого исключаем влияние на коэффициент влияния цены BTCUSDT на цену ETHUSDT
        time.sleep(600)  # определяем время ожидания изменения цены
        eth_price_last_hour = calculate_eth_price(exclude_btc_influence, 'ETHUSDT', 'BTCUSDT', 600)
        eth_price_change = (eth_price_last_hour / eth_price) - 1
        if abs(eth_price_change) >= 0.001:
            print(f'Изменение цены в прошлом часовом промежутке: {eth_price_change * 100:.2f}%')
        exclude_btc_influence = eth_price_change


if __name__ == '__main__':
    t = threading.Thread(target=monitor_price_change)
    t.start()
    t.join()
