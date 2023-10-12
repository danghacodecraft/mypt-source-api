import copy
import schedule
import time
import datetime
import threading


class EmailCron():
    def __init__(self):
        print("cron init!")
        self.stop_run = None

    def start(self):
        print("cron starting...")
        self.stop_run = self.init_start()
        return self

    def init_start(self, interval=1):
        cease_continuous_run = threading.Event()

        class ScheduleThread(threading.Thread):
            @classmethod
            def run(cls):
                while not cease_continuous_run.is_set():
                    schedule.run_pending()
                    time.sleep(interval)

        continuous_thread = ScheduleThread(daemon=True)
        continuous_thread.start()
        return cease_continuous_run

    def restart(self):
        self.stop_run.clear()

    def stop(self):
        self.stop_run.set()

    def add_task(self, callback, task_schedule, task_id=None, **kwargs):
        try:
            run_type = task_schedule.get("run_type", "")
            task = schedule.every(task_schedule.get("interval", 1))
            until = task_schedule.get("until", None)
            at = task_schedule.get("at", None)
            time_frame = task_schedule.pop("time_frame", False)

            if time_frame:
                return self.add_task_run_with_time_frame(callback, task_schedule, task_id, **kwargs)

            if "every_second" == run_type:
                task = task.seconds
            elif "daily" == run_type:
                task = task.days
            elif "hourly" == run_type:
                task = task.hour
            elif "every_minute" == run_type:
                task = task.minutes
            else:
                task = task.day

            if at is not None:
                task = task.at(at)

            if until is not None:
                task = task.until(until)

            task = task.do(callback, **kwargs)

            if task_id is not None:
                if isinstance(task_id, str):
                    task = task.tag(task_id)
                elif isinstance(task_id, list):
                    for tag in task_id:
                        task = task.tag(tag)

            return True, "success"
        except Exception as e:
            print(e)
            return False, str(e)

    def add_task_run_with_time_frame(self, callback, task_schedule, task_id=None, **kwargs):
        try:
            def add_task_run_with_time_frame_run_time(callback, task_schedule, task_id=None, **kwargs):
                try:
                    _task_schedule = copy.copy(task_schedule)
                    start_time = datetime.datetime.strptime(_task_schedule["start_at"], "%H:%M:%S").time()
                    until_time = datetime.datetime.strptime(_task_schedule["until"], "%H:%M:%S").time()
                    _now_exe = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S_%f")

                    if start_time > until_time:
                        until_date = datetime.datetime.now().date() + datetime.timedelta(days=1)
                    else:
                        until_date = datetime.datetime.now().date()

                    until_date = until_date.strftime("%Y-%m-%d")
                    _task_schedule['until'] = f"{until_date} {_task_schedule['until']}"

                    return self.add_task(
                        callback,
                        _task_schedule,
                        task_id=[
                            task_id,
                            f"add_task_run_with_time_frame_run_time_{_now_exe}"
                        ],
                        **kwargs
                    )
                except Exception as e:
                    print(e)
                    return False, str(e)

            start_at = task_schedule.get("start_at", None)
            until = task_schedule.get("until", None)

            if start_at is None:
                return False, "'start_at' is required"

            if until is None:
                return False, "'until' is required"

            task = schedule.every(1).days.at(start_at).do(
                add_task_run_with_time_frame_run_time,
                callback=callback,
                task_schedule=task_schedule,
                task_id=task_id,
                **kwargs
            )

            _now_exec = datetime.datetime.now().strftime("%d_%m_%Y_%H_%M_%S_%f")
            task = task.tag(task_id, f"add_task_run_with_time_frame_{_now_exec}")
            return True, "success"
        except Exception as e:
            print(e)
            return False, str(e)

    def get_task(self, task_id):
        return schedule.get_jobs(task_id)

    def get_all(self):
        return schedule.get_jobs()

    def clear_task(self, task_id):
        schedule.clear(task_id)

    def clear_all(self):
        schedule.clear()


mypt_schedule = EmailCron()
mypt_schedule.start()