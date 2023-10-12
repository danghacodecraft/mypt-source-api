import datetime
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.cache import cache
from project.celery import app as celery_app, revoke_task

from app.http.models.tools import Tools
from app.http.serializers.tool_serializer import ToolSerializer
from app.http.tasks.tools_management import send_expiration_reminder as send_expiration_reminder_task

@receiver(post_save, sender=Tools)
def send_expiration_reminder(sender, **kwargs):
    if kwargs.get("created", False):
        _send_expiration_reminder__create(kwargs["instance"])
    else:
        print("update")
        _send_expiration_reminder__update(kwargs["instance"])
        
def _send_expiration_reminder__create(instance: Tools):
    expiration_date = instance.expire_date
    async_task_ids = []
    
    if expiration_date is None or expiration_date < datetime.datetime.now().date():
        return
    
    for v in [-1, 0, 10, 20, 30]:
        _send_date = expiration_date - datetime.timedelta(days=v)
        _send_datetime = datetime.datetime(_send_date.year, _send_date.month, _send_date.day, 6, 30, 0)
        _now = datetime.datetime.now()
        
        if _send_datetime >= _now:
            task = send_expiration_reminder_task.apply_async(
                countdown=(_send_datetime - _now).total_seconds(),
                kwargs={
                    "notification_payload": _generate_notification_payload(
                        instance,
                        {
                            -1: "expired",
                            0: "last_reminder",
                        }.get(v, "about_to_expire")
                    ),
                    "key": instance.id if v == -1 else None
                }
            )
            async_task_ids.append(task.id)
            
    cache.set(f"tools:reminder_task_ids:{instance.id}", async_task_ids, 90*24*60*60)
    

def _send_expiration_reminder__update(instance: Tools):
    task_ids = cache.get(f"tools:reminder_task_ids:{instance.id}", [])
    for id in task_ids:
        revoke_task(id)
    cache.delete(f"tools:reminder_task_ids:{instance.id}")
    _send_expiration_reminder__create(instance)

def _generate_notification_payload(instance: Tools, type):
    contents = {
        "about_to_expire": lambda instance : {
            "title": "Bạn có một công cụ dụng cụ sắp hết hạn",
            "body": f"[{instance.item_code}] - [{instance.item_name}] sẽ hết hạn vào ngày {instance.expire_date.strftime('%d/%m/%Y')}",
            "popupTitle": "Công cụ dụng cụ sắp hết hạn",
            "popupBody": f"[{instance.item_code}] - [{instance.item_name}] sẽ hết hạn vào ngày {instance.expire_date.strftime('%d/%m/%Y')}"
        },
        "last_reminder": lambda instance : {
            "title": "Bạn có một công cụ dụng cụ sẽ hết hạn vào hôm nay",
            "body": f"[{instance.item_code}] - [{instance.item_name}] sẽ hết hạn vào ngày hôm nay ({instance.expire_date.strftime('%d/%m/%Y')})",
            "popupTitle": "Công cụ dụng cụ sắp hết hạn",
            "popupBody": f"[{instance.item_code}] - [{instance.item_name}] sẽ hết hạn vào ngày hôm nay ({instance.expire_date.strftime('%d/%m/%Y')})"
        },
        "expired": lambda instance : {
            "title": "Công cụ dụng cụ của bạn đã hết hạn",
            "body": f"[{instance.item_code}] - [{instance.item_name}] đã hết hạn vào ngày {instance.expire_date.strftime('%d/%m/%Y')}",
            "popupTitle": "Công cụ dụng cụ sắp hết hạn",
            "popupBody": f"[{instance.item_code}] - [{instance.item_name}] đã hết hạn vào ngày {instance.expire_date.strftime('%d/%m/%Y')}"
        }
    }
    
    return {
        **contents.get(type, "about_to_expire")(instance),
        "email": instance.email,
        "topic_type": "tools",
        "notifyActionType": "go_to_screen",
        "notifyDataAction": f"list-working-equipment/detail",
        "popupButtons": [
            {
                "buttonLabel": "Đóng",
                "buttonActionType": "close",
                "buttonDataAction": ""
            },
            {
                "buttonLabel": "Xem chi tiết",
                "buttonActionType": "go_to_screen",
                "buttonDataAction": f"list-working-equipment/detail",
                "extraData": ToolSerializer(instance ,status_message=True).data
            }
        ],
        "extraData": ToolSerializer(instance ,status_message=True).data
    }
