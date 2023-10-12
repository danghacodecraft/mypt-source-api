import json
import requests
from django.core.cache import cache
from celery import shared_task
from app.configs.service_api_config import get_api_info

@shared_task(retry_kwargs={'max_retries': 3, "default_retry_delay": 10})
def send_expiration_reminder(notification_payload, key):
    try:
        response = requests.request(
            **get_api_info("notification", "send_one_noti"),
            data=json.dumps(notification_payload),
            headers={
                "Content-Type": "application/json"
            },
            timeout=30
        )
        res = response.json()
        
        if key is not None:
            cache.delete(f"tools:reminder_task_ids:{key}")
        return res
    except Exception as e:
        raise Exception(str(e))
