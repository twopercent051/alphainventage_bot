import os
from datetime import datetime, timedelta
from typing import Optional

from aiogram.types import FSInputFile

from create_bot import scheduler, bot, config
from tgbot.models.redis_connector import TickersRedis, StocksRedis
from tgbot.services.api import AlphaAPI
from tgbot.services.excel import ExcelFile

admin_ids = config.tg_bot.admin_ids

api = AlphaAPI()
excel = ExcelFile()


class SchedulerAPI:

    @staticmethod
    def __get_next_ticker() -> Optional[str]:
        tickers = TickersRedis.get_all()
        stocks = StocksRedis.get_all()
        stocks_tickers = [i["ticker"] for i in stocks]
        for ticker in tickers:
            if ticker not in stocks_tickers:
                return ticker
        return

    @staticmethod
    async def __end_of_process():
        stocks = StocksRedis.get_all()
        file_name = excel.result_path
        excel.create_stocks_file(stocks=stocks)
        file = FSInputFile(path=file_name, filename=file_name)
        text = f"Спарсили {len(stocks)} тикеров"
        for user in admin_ids:
            await bot.send_document(chat_id=user, document=file, caption=text)
        os.remove(path=file_name)
        StocksRedis.clear()

    @classmethod
    async def main_dispatcher(cls):
        unprocessed_ticker = cls.__get_next_ticker()
        if unprocessed_ticker:
            ticker = unprocessed_ticker.upper()
            overview = await api.get_overview(symbol=ticker)
            total_revenue_ttm = await api.get_revenue_five_ttm(symbol=ticker)
            if overview and total_revenue_ttm:
                price_to_sales = overview[0]
                name_company = overview[1]
                tr_div_ps = round(total_revenue_ttm["ttm"] / price_to_sales, 6)
                data = dict(ticker=ticker,
                            name=name_company,
                            price_to_sales=price_to_sales,
                            total_revenue_ttm={total_revenue_ttm['ttm']},
                            tr_div_ps={tr_div_ps},
                            years=total_revenue_ttm["years"])
                text = [
                    f"<u>{ticker}</u>\n",
                    name_company,
                    f"P/S: {price_to_sales}",
                    f'TR TTM: {total_revenue_ttm["ttm"]} %',
                    f"TR / PS: {tr_div_ps} %",
                    f"Years: {total_revenue_ttm['years']}"
                ]
            else:
                data = dict(ticker=ticker,
                            name="---",
                            price_to_sales="---",
                            total_revenue_ttm="---",
                            tr_div_ps="---",
                            years="---")
                text = [f"Ticker {ticker} 404 🤷"]
            for user in admin_ids:
                await bot.send_message(chat_id=user, text="\n".join(text))
            StocksRedis.create(data=data)
            unprocessed_ticker = cls.__get_next_ticker()
            if not unprocessed_ticker:
                await cls.__end_of_process()
        else:
            await cls.__end_of_process()
        await cls.__create_task()

    @classmethod
    async def __create_task(cls):
        dtime = datetime.utcnow() + timedelta(hours=3, minutes=30)
        scheduler.add_job(func=cls.main_dispatcher,
                          trigger="date",
                          run_date=dtime,
                          misfire_grace_time=None)
