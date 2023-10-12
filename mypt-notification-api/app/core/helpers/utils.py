from Cryptodome.Cipher import AES
import time
import string
import random
import base64
from Crypto.Util.Padding import pad
from dateutil.parser import parse
from ..entities.centralized_session import CentralizedSession

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


# '2021-06-02T09:14:43Z'
def get_date(date_time=None):
    if date_time is None:
        print('dữ liệu ngày tháng null')
        return ""
    try:
        datatime = parse(date_time)
        return datatime.date()
    except:
        print('ngày tháng không đúng định dạng')
        return ""
    
def get_time(date_time=None):
    if date_time is None:
        print('dữ liệu ngày tháng null')
        return ""
    try:
        datatime = parse(date_time)
        return datatime.time()
    except:
        print('ngày tháng không đúng định dạng')
        return ""

def get_email_from_token(request):
    try:
        headerAuthToken = request.headers.get("Authorization")
        newHeaderAuthToken = headerAuthToken.replace("Bearer ", "")
        redisObj = CentralizedSession()
        dataRedis = redisObj.validateSession(newHeaderAuthToken)
        return dataRedis['sessionData']['email']
    except:
        return None
    
def get_info_from_request(request):
    try:
        headerAuthToken = request.headers.get("Authorization")
        newHeaderAuthToken = headerAuthToken.replace("Bearer ", "")
        redisObj = CentralizedSession()
        dataRedis = redisObj.validateSession(newHeaderAuthToken)
        return dataRedis
    except:
        return None
