from threading import Thread
import datetime
import time

class Scheduler:

    @staticmethod
    def threaded_function(scheduler, device_manager, logger):
        scheduler = sorted(scheduler, key=lambda k: k['hour'])

        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        hours = [t['hour'] for t in scheduler]
        device_manager.load_devices();
        while True:
            now = datetime.datetime.now()
            curr_hour = "{}:{}".format(str(now.hour).zfill(2), str(now.minute).zfill(2))
            for task in scheduler:
                if 1:
                    logger.info("[{}] - Executing Schedule task...{}".format(str(datetime.datetime.now()), task))
                    device_manager.update_device(task['device_id'], task['config'])
            next_tasks_hours = [h for h in hours if h > curr_hour]
            next_loop_time = next_tasks_hours[0] if len(next_tasks_hours) > 0 else hours[0]
            sleep_period = (datetime.datetime(2000, 1, 1, int(next_loop_time[:2]), int(next_loop_time[-2:]), 1) -
                            datetime.datetime(2000, 1, 1, now.hour, now.minute, now.second))
            if sleep_period.total_seconds() <= 0: # handle case where next task hour is smaller than now (due date tomorrow)
                sleep_period = datetime.timedelta(seconds=(sleep_period.total_seconds() + 86400))
            if sleep_period.total_seconds() > 3600: # sleep no more than 1 hour
                sleep_period = datetime.timedelta(seconds=3600)
            logger.info("[{}] - Next schedule task in on: {}. Sleeping for {}.".format(datetime.datetime.now(), next_loop_time, sleep_period))
            time.sleep(sleep_period.total_seconds())

    def __init__(self, scheduler, device_manager, logger):
        if len(scheduler) > 0:
            logger.info("Starting Scheduler...")
            thread = Thread(target = Scheduler.threaded_function, args = [scheduler, device_manager, logger])
            thread.start()