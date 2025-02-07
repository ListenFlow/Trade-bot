Listen Flow, [07.02.2025 14:03]
import ccxt
import time
import numpy as np
import pandas as pd
import os
from datetime import datetime

# Íàñòðîéêè API
api_key = os.getenv('BYBIT_API_KEY')  # êëþ÷ Bybit
api_secret = os.getenv('BYBIT_API_SECRET')  # ñåêðåòíûé êëþ÷

# Èíèöèàëèçàöèÿ Bybit
exchange = ccxt.bybit({
    'apiKey': api_key,
    'secret': api_secret,
    'options': {'defaultType': 'future'}
})

# Íàñòðîéêè
symbol = 'PEPEUSDT'  # Òðåéäîâàÿ ïàðà
leverage = 50  # Ïëå÷î
trade_amount = 1  # Ñóììà äëÿ òîðãîâëè
take_profit_percentage = 0.5  # Òåéê-ïðîôèò â %
stop_loss_percentage = 0.5  # Ñòîï-ëîññ â %

# Ïîëó÷àåì áàëàíñ
def get_balance():
    balance = exchange.fetch_balance()
    return balance['total']['USDT']

# Ïîëó÷àåì ñâå÷è äëÿ àíàëèçà
def get_ohlcv(symbol, timeframe='1m'):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

# Îòêðûòèå ïîçèöèè
def open_position(symbol, side, amount):
    print(f"Îòêðûòèå {side} ïîçèöèè íà {symbol}...")
    order = exchange.create_market_order(symbol, side, amount)
    return order

# Çàêðûòèå ïîçèöèè
def close_position(symbol):
    print(f"Çàêðûòèå ïîçèöèè íà {symbol}...")
    position = exchange.fetch_positions(symbol)
    if position:
        for pos in position:
            if pos['side'] == 'long':
                exchange.create_market_order(symbol, 'sell', abs(pos['contracts']))
            elif pos['side'] == 'short':
                exchange.create_market_order(symbol, 'buy', abs(pos['contracts']))
                
# Òîðãîâàÿ ëîãèêà
def trade():
    balance = get_balance()
    print(f"Áàëàíñ: {balance} USDT")
    
    # Óñòàíîâêà ïëå÷à
    exchange.futures_set_leverage(symbol, leverage)
    
    # Ïîëó÷àåì äàííûå äëÿ àíàëèçà
    df = get_ohlcv(symbol)
    
    # Ðàñ÷åò ñèãíàëîâ äëÿ òîðãîâëè íà îñíîâå ñâå÷íûõ ïàòòåðíîâ + îáúåìà
    # Èñïîëüçóåì ïðîñòóþ ñòðàòåãèþ íà îñíîâå 2 ïîñëåäíèõ ñâå÷åé è èõ îáúåìà
    if len(df) < 2:
        return  # Íåäîñòàòî÷íî äàííûõ äëÿ òîðãîâëè
    
    # Ïîñëåäíÿÿ ñâå÷à
    last_candle = df.iloc[-1]
    prev_candle = df.iloc[-2]
    
    if last_candle['close'] > last_candle['open'] and prev_candle['close'] < prev_candle['open']:  # Áûêîâàÿ ñâå÷à
        side = 'buy'
    elif last_candle['close'] < last_candle['open'] and prev_candle['close'] > prev_candle['open']:  # Ìåäâåæüÿ ñâå÷à
        side = 'sell'
    else:
        return  # Íåò ñèãíàëà
    
    # Îòêðûòèå ïîçèöèè
    open_position(symbol, side, trade_amount)

    # Îæèäàåì ïðèáûëè èëè ñòîï-ëîññà
    while True:
        # Ïðîâåðÿåì òåêóùóþ öåíó
        current_price = exchange.fetch_ticker(symbol)['last']
        
        # Ðàññ÷èòûâàåì öåëåâûå öåíû äëÿ òåéê-ïðîôèòà è ñòîï-ëîññà
        take_profit_price = current_price * (1 + take_profit_percentage / 100) if side == 'buy' else current_price * (1 - take_profit_percentage / 100)
        stop_loss_price = current_price * (1 - stop_loss_percentage / 100) if side == 'buy' else current_price * (1 + stop_loss_percentage / 100)
        
        # Ïðîâåðêà íà òåéê-ïðîôèò èëè ñòîï-ëîññ
        if side == 'buy':
            if current_price >= take_profit_price:
                close_position(symbol)
                print(f"Òåéê-ïðîôèò äîñòèãíóò íà {symbol}, ïðèáûëü: {take_profit_percentage}%")
                break
            elif current_price <= stop_loss_price:
                close_position(symbol)
                print(f"Ñòîï-ëîññ ñðàáîòàë íà {symbol}, óáûòîê: {stop_loss_percentage}%")
                break
        elif side == 'sell':
            if current_price <= take_profit_price:
                close_position(symbol)
                print(f"Òåéê-ïðîôèò äîñòèãíóò íà {symbol}, ïðèáûëü: {take_profit_percentage}%")
                break
            elif current_price >= stop_loss_price:
                close_position(symbol)
                print(f"Ñòîï-ëîññ ñðàáîòàë íà {symbol}, óáûòîê: {stop_loss_percentage}%")
                break
        
        # Ïàóçà ìåæäó ïðîâåðêàìè
        time.sleep(5)

Listen Flow, [07.02.2025 14:03]
# Îñíîâíîé öèêë
while True:
    trade()
    time.sleep(10)
