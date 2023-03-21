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
    btc_url = 'https://api.binance.com/api/v3/klines'
    btc_params = {'symbol': 'BTCUSDT', 'interval': '1h', 'limit': 500}
    btc_response = requests.get(btc_url, params=btc_params)
    btc_data = btc_response.json()

    eth_url = 'https://api.binance.com/api/v3/klines'
    eth_params = {'symbol': 'ETHUSDT', 'interval': '1h', 'limit': 500}
    eth_response = requests.get(eth_url, params=eth_params)
    eth_data = eth_response.json()

    btc_df = pd.DataFrame(btc_data,
                          columns=['Open time', 'Open', 'High', 'Low', 'Close',
                                   'Volume', 'Close time',
                                   'Quote asset volume', 'Number of trades',
                                   'Taker buy base asset volume',
                                   'Taker buy quote asset volume', 'Ignore'])
    btc_df['Open time'] = pd.to_datetime(btc_df['Open time'], unit='ms')
    btc_df['Close'] = btc_df['Close'].astype(float)

    eth_df = pd.DataFrame(eth_data,
                          columns=['Open time', 'Open', 'High', 'Low', 'Close',
                                   'Volume', 'Close time',
                                   'Quote asset volume', 'Number of trades',
                                   'Taker buy base asset volume',
                                   'Taker buy quote asset volume', 'Ignore'])
    eth_df['Open time'] = pd.to_datetime(eth_df['Open time'], unit='ms')
    eth_df['Close'] = eth_df['Close'].astype(float)

    df = pd.merge(btc_df[['Open time', 'Close']],
                  eth_df[['Open time', 'Close']], on='Open time')
    corr = df['Close_x'].corr(df['Close_y'])

    return corr * 3


def calculate_eth_price(exclude_btc_influence: float, symbol1, symbol2,
                        window) -> float:
    """Функция для расчета цены ETHUSDT, исключив его движения, вызванные влиянием цены BTCUSDT"""
    eth_price = get_price('ETHUSDT')
    btc_price = get_price('BTCUSDT')
    eth_btc_influence = get_eth_btc_influence(symbol1, symbol2, window)
    eth_price -= (btc_price * eth_btc_influence * exclude_btc_influence)
    return eth_price


def monitor_price_change() -> None:
    """Функция для отслеживания изменения цены ETHUSDT и вывода сообщения в консоль"""
    exclude_btc_influence = 0  # Влияние на коэффициент влияния цены BTCUSDT на цену ETHUSDT
    while True:
        eth_price = calculate_eth_price(exclude_btc_influence, 'ETHUSDT',
                                        'BTCUSDT',
                                        600)  # Время выборки из которого исключаем влияние на коэффициент влияния цены BTCUSDT на цену ETHUSDT
        time.sleep(600)  # определяем время ожидания изменения цены
        eth_price_last_hour = calculate_eth_price(exclude_btc_influence,
                                                  'ETHUSDT', 'BTCUSDT', 600)
        eth_price_change = (eth_price_last_hour / eth_price) - 1
        if abs(eth_price_change) >= 0.001:
            print(
                f'Изменение цены в прошлом часовом промежутке: {eth_price_change * 100:.2f}%')
        exclude_btc_influence = eth_price_change


if __name__ == '__main__':
    t = threading.Thread(target=monitor_price_change)
    t.start()
    t.join()
