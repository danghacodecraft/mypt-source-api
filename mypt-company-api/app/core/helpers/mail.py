from email.mime.image import MIMEImage
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from ...core.helpers import *
import base64
import requests
import os

def send_email_fpt(subject="", message="", recipient_list=""):
    email_from = settings.EMAIL_HOST_USER
    send_mail( subject=subject, message=message, html_message=message, from_email=email_from, recipient_list=recipient_list)

def mail_reply_improved_car(data = {}):
    print('mail_reply_improved_car in')
    to = data.pop("recipient_list", [""])
    message = EmailMultiAlternatives(
        data.pop('subject', ''), 
        "", 
        to=to, 
        from_email=settings.EMAIL_HOST_USER,
        reply_to=to
    )
    message.content_subtype = 'html'
    message.mixed_subtype = 'related'
    icon_not_star = attach_img(url="https://apis.fpt.vn/mypt-ho-media-api/view-file?path=0242629635130290", name='not_star')
    icon_star = attach_img(url="https://apis.fpt.vn/mypt-ho-media-api/view-file?path=0034947842185023", name='star')
    message.attach(icon_star)
    message.attach(icon_not_star)
    message.attach_alternative(data.pop('message', ''), "text/html")
    message.send()

# def attach_img(url, name):
#     icon_star = base64.b64encode(requests.get(url).content)
#     base64_message = icon_star.decode()
#     base64_bytes = base64_message.encode('ascii')
#     message_bytes = base64.b64decode(base64_bytes)
#     image_attach = MIMEImage(message_bytes)
#     cid_name = f'<{name}>'
#     image_attach.add_header('Content-ID', cid_name)
#     return image_attach
    
def attach_img(url, name):
    print('attach_img in')
    proxies = { 
        "http"  : "http://proxy.hcm.fpt.vn:80", 
        "https" : "http://proxy.hcm.fpt.vn:80"
    }
    icon_star = base64.b64encode(requests.get(url, proxies=proxies).content)
    base64_message = icon_star.decode()
    base64_bytes = base64_message.encode('ascii')
    message_bytes = base64.b64decode(base64_bytes)
    image_attach = MIMEImage(message_bytes)
    cid_name = f'<{name}>'
    image_attach.add_header('Content-ID', cid_name)
    return image_attach

def mail_improved_car(data = {}):
    to = data.pop("recipient_list", [""])
    print("----------mail_improved_car in-----------------")
    try:
        message = EmailMultiAlternatives(
            data.pop('subject', ''),
            "",
            to=to,
            from_email=settings.EMAIL_HOST_USER,
            reply_to=to
        )
        message.content_subtype = 'html'
        message.mixed_subtype = 'related'
        icon_img = {
            "icon1": "https://apis.fpt.vn/mypt-ho-media-api/view-file?path=0136469917305209",
            "icon2": "https://apis.fpt.vn/mypt-ho-media-api/view-file?path=0202714323264277",
            "icon3": "https://apis.fpt.vn/mypt-ho-media-api/view-file?path=0162047078839229"
        }
        icon_img_key = list(icon_img.keys())
        print(icon_img_key)
        for item in icon_img_key:
            icon = attach_img(url=icon_img[item], name=item)
            message.attach(icon)
        list_img = data["list_img"]["list_img"]
        sum_img = data["list_img"]["len_img"]
        for i in range(1, sum_img+1):
            name = "img" + str(i)
            icon = attach_img(url=list_img[i-1], name=name)
            message.attach(icon)
        message.attach_alternative(data.pop('message', ''), "text/html")
        message.send()
    except Exception as ex:
        print("Error send email multi alternatives", ex)
    print("----------mail_improved_car out-----------------")