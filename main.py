from pybit.unified_trading import HTTP
from time import sleep
import pandas_ta as ta

#TREADER
exchange = HTTP(api_key = "vY8a2Xenfp9ScqMuZb", api_secret = "45iApSvrUa2koR77kjm6PglnbgOZDbj5Yj2b")
def CollectLast():
    global df
    response = exchange.get_kline(symbol = "TONUSDT", category = "spot", interval="1", limit=100)["result"]["list"]
    openL, high, low, close = [], [], [], []

    for candle in response:
        openL.append(float(candle[1]))
        high.append(float(candle[2]))
        low.append(float(candle[3]))
        close.append(float(candle[4]))
    openL.reverse()
    high.reverse()
    low.reverse()
    close.reverse()
    print(openL[-1])
    df = ta.DataFrame({"by": openL, "sell": close, "high": high, "low": low})
# Big parameters
lookback = 100
trade_size = 1.7

history = [[]]
by_cost = 0
sell_cost = 0
cost = 0
min_cost = 0
max_cost = 0
dollars = 40
currency = 0
running = False

df = ta.DataFrame()
CollectLast()
start_cost = df["by"].iloc[-1]
start = dollars  + currency * df["by"].iloc[-1]

def By(count, i):
    global currency, dollars
    if count < 0:
        print(f"{count} < 0")
        return
    if dollars < count * by_cost:
        print(f"No succesed buy at {i}")
        return
    print(f"Buy {by_cost}  {sell_cost}, cost = {cost}")
    dollars -= count * by_cost
    currency += count
    # order = exchange.place_order(category="spot", symbol="TRUMPUSDT", side="Buy", orderType="Market", qty=traid_size)
    # print(order)

def Sell(count, i):
    global currency, dollars
    if count < 0:
        print(f"{count} < 0")
        return
    if currency < count:
        print(f"No succesed sell at {i}")
        return
    print(f"Sell  {by_cost}  {sell_cost}, cost = {cost}")
    dollars += count * sell_cost
    currency -= count
    # order = exchange.place_order(category="spot", symbol="TRUMPUSDT", side="Sell", orderType="Market", qty=trade_size)
    # print(order)

def Traid():
    global cost, by_cost, sell_cost, df, start, start_cost, trade_size, dollars, currency, running
    position = 1
    for i in range(300):
        if running:
            print("Wake UP!")
            CollectLast()
            cost = df["by"].iloc[-1]
            by_cost = df["by"].iloc[-1]
            sell_cost = df["sell"].iloc[-1]
            macd = ta.macd(df["sell"], fast=12, slow=26, signal=9)
            df["MACD"] = macd["MACD_12_26_9"]
            df["MACD_signal"] = macd["MACDs_12_26_9"]

            # Торговая логика
            offset = 0.0006
            if df["MACD"].iloc[-1] - df["MACD_signal"].iloc[-1] > offset and position == 1:
                By(trade_size, i)
                position = -1
            elif df["MACD"].iloc[-1] - df["MACD_signal"].iloc[-1] < -offset / 2.5 and position == -1:
                Sell(trade_size, i)
                position = 1
            print(df["MACD"].iloc[-1] - df["MACD_signal"].iloc[-1])
            now = dollars + currency * cost
            print(f"Start = {start}, now = {now}, {(now - start) / start * 100}% ba, {(cost - start_cost) / start_cost * 100}% cur")
            sleep(59)
        sleep(1)

    print(f"На старте: {start}")
    end = dollars + currency * float(cost)
    pend = dollars + currency * cost
    print(f"В конце с разницей в цене = {pend}, без = {end}")
    print(f"С разницей в цене {round((pend - start) / start * 100, 2)}%, без {round((end - start) / start * 100, 2)}%")

# START
Traid()
