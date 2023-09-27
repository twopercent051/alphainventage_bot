import asyncio
from typing import Literal, Optional

import aiohttp as aiohttp

from create_bot import config


class AlphaAPI:
    def __init__(self):
        self.token = config.misc.alpha_api_token
        self.url = "https://www.alphavantage.co/query"

    async def __request(self, function: Literal["OVERVIEW", "INCOME_STATEMENT"], symbol: str) -> dict:
        params = dict(function=function, symbol=symbol, apikey=self.token)
        async with aiohttp.ClientSession() as session:
            async with session.get(url=self.url, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()

    async def get_overview(self, symbol: str) -> Optional[tuple]:
        """Метод получения P/S и полное название компании"""
        result = await self.__request(function="OVERVIEW", symbol=symbol)
        try:
            return float(result["PriceToSalesRatioTTM"]), result["Name"]
        except KeyError:
            return

    async def get_revenue_five_ttm(self, symbol: str) -> Optional[dict]:
        """Метод получения Total Revenue 5TTM в виде десятичной дроби с округлением 6зн"""
        result = await self.__request(function="INCOME_STATEMENT", symbol=symbol)
        try:
            quarters = result["quarterlyReports"]
        except KeyError:
            return
        first_total_revenue = 0
        last_total_revenue = 0
        quarters = quarters[:20]
        years = len(quarters) / 4
        try:
            for quarter in quarters[-4:]:
                first_total_revenue += int(float(quarter["totalRevenue"]))
            for quarter in quarters[:4]:
                last_total_revenue += int(float(quarter["totalRevenue"]))
            ttm = round(((last_total_revenue - first_total_revenue) * 100 / first_total_revenue) / years, 6)
        except:
            return
        return dict(ttm=ttm, years=years)


async def main():
    api = AlphaAPI()
    result = await api.get_overview(symbol="CLSK")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
