import logging
import redis
import betterlogging as bl

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tgbot.config import load_config
from tgbot.middlewares.config import ConfigMiddleware

config = load_config(".env")
r = redis.Redis(host=config.rds.host, port=config.rds.port, db=config.rds.db)
storage = RedisStorage(redis=r) if config.tg_bot.use_redis else MemoryStorage()
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
dp = Dispatcher()
scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
# scheduler.add_jobstore(jobstore="redis", jobs_key="stocks_jobs", run_times_key="stocks_times")

logger = logging.getLogger(__name__)
log_level = logging.INFO
bl.basic_colorized_config(level=log_level)


def register_global_middlewares(dp: Dispatcher, config):
    dp.message.outer_middleware(ConfigMiddleware(config))
    dp.callback_query.outer_middleware(ConfigMiddleware(config))