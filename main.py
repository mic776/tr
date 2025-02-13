from pybit.unified_trading import HTTP
from time import sleep
import pandas_ta as ta
import threading

#TREADER
exchange = HTTP(api_key = "vY8a2Xenfp9ScqMuZb", api_secret = "45iApSvrUa2koR77kjm6PglnbgOZDbj5Yj2b")
def CollectLast():
    global df
    response = exchange.get_kline(symbol = "TRUMPUSDT", category = "spot", interval="1", limit=100)["result"]["list"]
    openL, high, low, close = [], [], [], []

    for candle in response:
        openL.append(float(candle[1]))
        high.append(float(candle[2]))
        low.append(float(candle[3]))
        close.append(float(candle[4]))
    print(openL[-1])
    df = ta.DataFrame({"by": openL, "sell": close, "high": high, "low": low})
# Big parameters
lookback = 100
traid_size = 0.2

history = [[]]
by_cost = 0
sell_cost = 0
cost = 0
min_cost = 0
max_cost = 0
dollars = 20
currency = 1
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
    print(f"Buy {cost}")
    dollars -= count * by_cost
    currency += count

def Sell(count, i):
    global currency, dollars
    if count < 0:
        print(f"{count} < 0")
        return
    if currency < count:
        print(f"No succesed sell at {i}")
        return
    print(f"Sell {cost}")
    dollars += count * sell_cost
    currency -= count

def Traid():
    global cost, by_cost, sell_cost, df, start, start_cost, traid_size, dollars, currency, running
    for i in range(300):
        if running:
            print("Wake UP!")
            CollectLast()
            cost = df["by"].iloc[-1]
            by_cost = df["by"].iloc[-1]
            sell_cost = df["sell"].iloc[-1]

            df["closeM"] = [(j - min(df["sell"])) * 100 for j in df["sell"]]
            macd = ta.macd(df["closeM"], fast=12, slow=26, signal=9)
            rsi = ta.rsi(df["sell"], length=9)
            atr = ta.atr(df['high'], df['low'], df['sell'], length=14) * 100
            df["ATR"] = atr
            df["RSI"] = rsi
            df["MACD"] = macd["MACD_12_26_9"]
            df["signal"] = macd["MACDs_12_26_9"]
            df["histogram"] = macd["MACDh_12_26_9"]

            if rsi.iloc[-1] > 50:
                By(traid_size, i)
            elif rsi.iloc[-1] < 50:
                Sell(traid_size, i)
            if df["histogram"].iloc[-1] > 0.83:
                Sell(traid_size, i)
            elif df["histogram"].iloc[-1] < -0.83:
                By(traid_size, i)
            print(f"Start = {start}, now = {dollars + currency * cost}")

        sleep(60)

    print(f"На старте: {start}")
    end = dollars + currency * float(cost)
    pend = dollars + currency * cost
    print(f"В конце с разницей в цене = {pend}, без = {end}")
    print(f"С разницей в цене {round((pend - start) / start * 100, 2)}%, без {round((end - start) / start * 100, 2)}%")

# BOT
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = "7905272377:AAFPwhDWSRQajcE5UPdGgYj91jxBque_Nc0"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("stop, bal, run?")

@dp.message(Command("stop"))
async def start_command(message: types.Message):
    global running
    running = False
    await message.answer("Остановлен!")
@dp.message(Command("run"))
async def start_command(message: types.Message):
    global running
    running = True
    await message.answer("Запущен!")
@dp.message(Command("bal"))
async def start_command(message: types.Message):
    global dollars, currency, cost, start, start_cost
    await message.answer(f"Баланс: {dollars}$, {currency} крипты, суммарно {dollars + currency * cost} "
                         f", на старте = {start}, цена на старте = {start_cost}, цена = {cost}")

async def bot_main():
    await dp.start_polling(bot)

def start_bot():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(bot_main())

# START
bot_thread = threading.Thread(target=start_bot, daemon=True)
bot_thread.start()
tread_process = threading.Thread(target=Traid)
tread_process.start()
print("Бот запущен!")