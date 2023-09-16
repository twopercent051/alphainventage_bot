from datetime import datetime
from typing import List, Optional

import redis
import json

from create_bot import config, logger

r = redis.Redis(host=config.rds.host, port=config.rds.port, db=config.rds.db)


class RedisConnector:
    r = redis.Redis(host=config.rds.host, port=config.rds.port, db=config.rds.db)
    db = None

    db_list = ["stocks_alpha", "tickers"]

    @classmethod
    def redis_start(cls):
        for db in cls.db_list:
            response = cls.r.get(db)
            if not response:
                cls.r.set(db, json.dumps(list()))
        logger.info('Redis connected OKK')

    @classmethod
    def create(cls, data: dict):
        response: list = cls.get_all()
        response.append(data)
        cls.r.set(cls.db, json.dumps(response))

    @classmethod
    def get_all(cls) -> List[dict | str]:
        response = cls.r.get(cls.db)
        if not response:
            return
        response = response.decode("utf-8")
        return json.loads(response)

    @classmethod
    def clear(cls):
        cls.r.set(cls.db, json.dumps(list()))


class StocksRedis(RedisConnector):
    db = "stocks_alpha"


class TickersRedis(RedisConnector):
    db = "tickers"

    @classmethod
    def create(cls, tickers: list):
        cls.r.set(cls.db, json.dumps(tickers))
