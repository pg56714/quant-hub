from base.scheduler import scheduler
from base.scheduler import BaseScheduler

from internal.notification.VolumeBomb import VolumeBomb


class NotificationScheduler(BaseScheduler):
    def __init__(self):
        super().__init__()

    def schedule(self):
        scheduler.add_job(self.execute_async_job, "cron", minute="*/5", second=0, args=[VolumeBomb])
