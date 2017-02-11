from threading import Thread
from threading import Event
import datetime

class Scheduler:

    @staticmethod
    def threaded_function(scheduler, scheduler_on, device_manager, logger, stop_event):
        scheduler = sorted(scheduler, key=lambda k: k['hour'])
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        hours = [t['hour'] for t in scheduler]
        while not stop_event.is_set():
            now = datetime.datetime.now()
            curr_hour = "{}:{}".format(str(now.hour).zfill(2), str(now.minute).zfill(2))
            if scheduler_on.scheduler_on:
                for task in scheduler:
                    if task['hour'] == curr_hour and days[now.weekday()] in task['day']:
                        logger.info("[{}] - Executing Schedule task...{}".format(str(datetime.datetime.now()), task))
                        device_type=device_manager.devices[task['device_id']]['type']
                        if device_type == 'air_conditioner':
                            ac_on = device_manager.devices[task['device_id']]['last_config']['on_off']=='true'
                            if task['config']['on_off']!=ac_on:
                                task['config']['on_off-changed'] = unicode('true', "utf-8")
                            else:
                                task['config']['on_off-changed'] = unicode('false', "utf-8")
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
            stop_event.wait(sleep_period.total_seconds())

        logger.info("Scheduler Stopped...")

    def __init__(self, scheduler, scheduler_on, device_manager, logger):
        self.scheduler_on = scheduler_on
        self.device_manager = device_manager
        self.logger = logger
        self.thread = None
        self.stop_event = None
        self.set(scheduler)

    def set(self, scheduler):
        if self.stop_event:
            if not self.stop_event.is_set():
                self.logger.info("Stopping Scheduler...")
                self.stop_event.set()
            self.thread.join()

        scheduler = [t for t in scheduler if t['enabled']] # filter out disabled tasks
        if len(scheduler) > 0:
            self.logger.info("Starting Scheduler...")
            self.stop_event = Event()
            self.thread = Thread(target = Scheduler.threaded_function,
                                 args = [scheduler, self.scheduler_on, self.device_manager, self.logger, self.stop_event])
            self.thread.start()