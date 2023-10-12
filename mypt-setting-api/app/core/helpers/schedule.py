import schedule
import time
import threading

class CronBase():
    def __init__(self):
        print("cron init!")
        self.stop_run = None
        self.schedule = schedule.Schedule()
        
    def init_start(self, interval=1):
        cease_continuous_run = threading.Event()
        class ScheduleThread(threading.Thread):
            @classmethod
            def run(cls):
                while not cease_continuous_run.is_set():
                    try:
                        self.schedule.run_pending()
                        time.sleep(interval)
                    except Exception as e:
                        print(f"cron base init_start: {e}")    

        continuous_thread = ScheduleThread(daemon=True)
        continuous_thread.start()
        return cease_continuous_run
        
    def start(self):
        print("cron starting...")
        self.stop_run = self.init_start()
        return self
    
    def add_task(self, callback, cron, task_id=None, **kwargs):
        try:
            self.schedule.add_job(callback, cron, task_id, **kwargs)
            return True, "success"
        except Exception as e:
            return False, str(e)
   
    def clear_task(self, task_id=None):
        try:
            self.schedule.job_store.remove_job(task_id)
            return True
        except Exception as e:
            print(e)
    
    def clear_all(self):
        self.schedule.job_store.remove_all_jobs()
        return True

        self.schedule.clear()