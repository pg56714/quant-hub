from base.discord import DiscordConnector

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime
import traceback
import asyncio
import nest_asyncio

nest_asyncio.apply()

executors = {"default": ThreadPoolExecutor(30)}

job_defaults = {"coalesce": True, "misfire_grace_time": None}

scheduler = BackgroundScheduler(job_defaults=job_defaults, executors=executors)


class BaseScheduler(object):
    def __init__(self):
        self.discord = DiscordConnector()

    # --------------------- fundamental methods ---------------------#
    def execute_sync_job(self, job_class):
        try:
            job_class().run()
        except Exception:
            message = (
                f"```"
                f"Error: {job_class.__name__} failed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"{traceback.format_exc()[-1900:]}\n"
            )
            self.discord.send_message("CRITICAL", message)

    def execute_async_job(self, job_class):
        try:
            asyncio.run(job_class().run())
        except Exception:
            message = (
                f"```"
                f"Error: {job_class.__name__} failed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"{traceback.format_exc()[-1900:]}\n"
            )
            self.discord.send_message("CRITICAL", message)
