import ccxt.async_support as ccxt
import asyncio
import pandas as pd
import os

from base.discord import DiscordConnector
from base.config_reader import Config

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG_DIR = os.path.join(ROOT, "config")
CONFIG_PATH = os.path.join(CONFIG_DIR, "notification.json")


class VolumeBomb(object):
    def __init__(self):
        self.discord = DiscordConnector()
        self.exchange = ccxt.binanceusdm()
        self.config = Config(CONFIG_PATH)["VolumeBomb"]

    async def run(self):
        """執行爆量檢查

        步驟：
        1. 取得K線資料
        2. 清理數據並生成平均成交量
        3. 檢查是否有爆量訊號
        """
        ohlcv_dict = await self.getKline()
        for symbol, ohlcv_df in ohlcv_dict.items():
            mean_volume = self.cleanData2GenerateMeanVolume(ohlcv_df)
            self.checkSignal(symbol, mean_volume, ohlcv_df)
        await self.exchange.close()

    async def getKline(self) -> dict:
        """取得K線資料（用async的方法取得多筆數據會較快）

        步驟：
        1. 取得K線資料
        2. 轉換成DataFrame以及對應的格式
        """
        ohlcv_dict = {}
        tasks = []

        async def get_ohlcv(symbol, timeframe):
            return await self.exchange.fetch_ohlcv(symbol, timeframe, limit=100)

        for symbol in self.config["valid_symbol"]:
            task = asyncio.create_task(get_ohlcv(symbol, "5m"))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        for i, response in enumerate(responses):
            symbol = self.config["valid_symbol"][i]

            df = pd.DataFrame(response, columns=["time", "open", "high", "low", "close", "volume"])
            df["time"] = df["time"].astype(int)
            df["open"] = df["open"].astype(float)
            df["high"] = df["high"].astype(float)
            df["low"] = df["low"].astype(float)
            df["close"] = df["close"].astype(float)
            df["volume"] = df["volume"].astype(float)

            if symbol not in ohlcv_dict:
                ohlcv_dict[symbol] = {}
            ohlcv_dict[symbol] = df.iloc[:-1]  # 不取最後一筆資料，因為我們是每五分鐘的0秒開始偵測，最後一根K線才剛開始
        return ohlcv_dict

    def cleanData2GenerateMeanVolume(self, ohlcv_df):
        """清理數據並生成平均成交量

        步驟：
        1. 將成交量中的極端值去除
        2. 計算平均成交量
        """
        volume = ohlcv_df["volume"]
        Q1 = volume.quantile(0.25)
        Q3 = volume.quantile(0.75)
        IQR = Q3 - Q1
        mean_volume = volume[(volume >= Q1 - 1.5 * IQR) & (volume <= Q3 + 1.5 * IQR)].mean()
        return mean_volume

    def checkSignal(self, symbol, mean_volume, ohlcv_df):
        """檢查是否有爆量訊號

        步驟：
        1. 判斷趨勢
        2. 判斷成交量是否大於平均成交量的10倍
        3. 發送Discord訊息
        """
        slope = ohlcv_df["close"].iloc[-1] - ohlcv_df["close"].iloc[-10]

        if slope <= 0:
            trend = "下跌"
        else:
            trend = "上漲"

        if ohlcv_df["volume"].iloc[-1] >= mean_volume * 10:
            message = (
                f"```"
                f"[🔥｜Volume Bomb] {symbol}爆量{trend}\n"
                f"現價：{ohlcv_df['close'].iloc[-1]}\n"
                f"成交量：{ohlcv_df['volume'].iloc[-1]}"
                f"```"
            )
            self.discord.send_message("VOLUMEBOMB", message)
