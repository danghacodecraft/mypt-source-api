from datetime import datetime
from typing import List
import pycron
from threading import Thread    

class MYPTCron():
    def __init__(self):
        self._running = False
        self.task_thread = None
        self.tasks: List[str] = []
    
    def add_job(self, callback, execute_time):
        print(f"MYPTCron is adding new task ({datetime.now()})")
        try:
            is_exists = self.tasks.index(callback.__name__)
        except:
            self.tasks.append(callback.__name__)
            print(self.tasks)
            @pycron.cron(execute_time)
            async def new_job(self):
                return callback()
            
    def start(self):
        print(f"MYPTCron is running...({datetime.now()})")
        def job_cron_start():
            self._running = True
            pycron.start()
            print("Tasks done...")
        self.task_thread = Thread(target=job_cron_start, daemon=True)
        self.task_thread.start()
        
    def stop(self):
        print(f"MYPTCron stopped at {datetime.now()}")
        self._running = False
        pycron.stop()
    
    def is_running(self):
        return self._running
    
    def clear_all_tasks(self):
        print(f"MYPTCron clear all tasks at {datetime.now()}")
        pycron.stop()
        self.task_thread = None
        pycron.scheduled_functions.clear()
        pycron.running_functions.clear()
    
    def remove_job(self, job_name):
        try:
            idx = self.tasks.index(job_name)
            self.tasks.pop(idx)
            pycron.scheduled_functions.pop(idx)
            print("Job had been removed...")
        except:
            print("Job undefined...")