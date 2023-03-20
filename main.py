import requests
import time
import threading
import numpy as np


def get_eth_price() -> float:
    """Функция для получения текущей цены фьючерса ETHUSDT"""
    url = 'https://fapi.binance.com/fapi/v1/ticker/price'
    params = {'symbol': 'ETHUSDT'}
    response = requests.get(url, params=params)
    data = response.json()
    return float(data['price'])


def get_btc_price() -> float:
    """Функция для получения текущей цены BTCUSDT"""
    url = 'https://api.binance.com/api/v3/ticker/price'
    params = {'symbol': 'BTCUSDT'}
    response = requests.get(url, params=params)
    data = response.json()
    return float(data['price'])


def get_eth_btc_influence() -> float:
    """Функция для получения коэффициента влияния цены BTCUSDT на цену ETHUSDT"""
    url = 'https://fapi.binance.com/fapi/v1/premiumIndex'
    params = {'symbol': 'ETHUSDT'}
    response = requests.get(url, params=params)
    data = response.json()
    return float(data['lastFundingRate']) * 3


def calculate_eth_price(exclude_btc_influence: float) -> float:
    """Функция для расчета цены ETHUSDT, исключив его движения, вызванные влиянием цены BTCUSDT"""
    eth_price = get_eth_price()
    btc_price = get_btc_price()
    eth_btc_influence = get_eth_btc_influence()
    eth_price -= (btc_price * eth_btc_influence * exclude_btc_influence)
    return eth_price


def monitor_price_change() -> None:
    """Функция для отслеживания изменения цены ETHUSDT и вывода сообщения в консоль"""
    exclude_btc_influence = 0
    while True:
        eth_price = calculate_eth_price(exclude_btc_influence)
        time.sleep(600)
        eth_price_last_hour = calculate_eth_price(exclude_btc_influence)
        eth_price_change = (eth_price_last_hour / eth_price) - 1
        print(f'ETHUSDT price change: {eth_price_change * 100:.2f}%')
        if abs(eth_price_change) >= 0.001:
            print(f'Price change detected: {eth_price_change * 100:.2f}%')
        exclude_btc_influence = (eth_price_last_hour / eth_price) - 1


if __name__ == '__main__':
    t = threading.Thread(target=monitor_price_change) # Создаем поток для отслеживания изменения цены ETHUSDT
    t.start() # запускаем поток для отслеживания изменения цены ETHUSDT
    t.join() # Ожидание завершения выполнения последнего потока
