from datetime import datetime, timedelta

from create_bot import scheduler, bot, config

admin_ids = config.tg_bot.admin_ids


class SchedulerAPI:

    @classmethod
    async def main_dispatcher(cls):
        pass


    @classmethod
    async def create_task(cls):
        dtime = datetime.utcnow() + timedelta(hours=3, minutes=30)
        scheduler.add_job(func=cls.main_dispatcher,
                          trigger="date",
                          run_date=dtime)
