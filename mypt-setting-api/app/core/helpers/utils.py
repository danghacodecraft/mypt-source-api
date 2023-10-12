from Cryptodome.Cipher import AES
import time
import string
import random
import base64
from Crypto.Util.Padding import pad
import json
import requests
from datetime import *
from ...configs.variable import *

def aes256():
    try:
        # 16s bit
        BS = 16
        # SECRET KEY of API SCM in Document
        # Staging
        # key =   b'8840240ce0ecbb703a9425b40a121d99'
        # Production
        key = b'33b8ddca078f4bbc85d90fb7d3b4fde4'
        # Key IV of API SCM in Document
        iv =  b'bscKHn8REOJ2aikS'
        return BS,key,iv
    except Exception as e:
        print(e)


def randomSecretKey(stringLength=16, fname=""):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(stringLength))


def encrypt_aes(iv, raw, fname=""):
    # BS = aes256()[0]
    key = aes256()[1]
    _iv = iv.encode()
    # pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
    # raw = pad(raw)
    raw = pad(raw.encode(), 16)
    cipher = AES.new(key, AES.MODE_CBC, _iv)
    return base64.b64encode(cipher.encrypt(raw)).decode("utf-8")


def decrypt_aes(iv, enc, fname=""):
    key = aes256()[1]
    # iv = aes256()[2]
    unpad = lambda s : s[:-ord(s[len(s)-1:])]
    enc = base64.b64decode(enc)
    cipher = AES.new(key, AES.MODE_CBC, iv.encode() )
    return unpad(cipher.decrypt( enc )).decode("utf-8")

def call_api(**kwargs):
    try:
        host = kwargs.pop("host")
        func = kwargs.pop("func")
        method = kwargs.pop("method")
        data = kwargs.pop("data", None)
        headers = kwargs.pop("headers", {'Content-Type': 'application/json'})
        payload = json.dumps(data)
        response = requests.request(method, host+func, headers=headers, data=payload)
        return response.text
    except:
        None

def date_from_now(d=0):
    data_time = datetime.now()
    data_time += timedelta(days=d)
    return data_time.date()


def month_from_now(m=0):
    if m == 0:
        return datetime.now().replace(day=1).strftime(DATE_FORMAT_QUERY), datetime.now().strftime(DATE_FORMAT_QUERY)
    lastMonth = datetime.now()
    for item in range(m):
        lastMonth = lastMonth.replace(day=1)
        lastMonth = lastMonth - timedelta(days=1)
    lastMonth = lastMonth.replace(day=1)
    return lastMonth.strftime(DATE_FORMAT_QUERY), datetime.now().strftime(DATE_FORMAT_QUERY)

def to_str_fr_list(_list):
    if isinstance(_list, list):
        return ';'.join([str(item) for item in _list])