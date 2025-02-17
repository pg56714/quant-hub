import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import time
from base.scheduler import scheduler
from internal.notification.scheduler import NotificationScheduler
from internal.strategy.scheduler import StrategyScheduler

if __name__ == "__main__":
    NotificationScheduler().schedule()
    StrategyScheduler().schedule()

    scheduler.start()

    print("Scheduler is running...")

    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down scheduler...")
        scheduler.shutdown()
