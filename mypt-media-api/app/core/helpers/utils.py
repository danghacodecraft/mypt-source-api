from Cryptodome.Cipher import AES
import time
import string
import random
import base64
from Crypto.Util.Padding import pad
from app.core.helpers.global_variables import *
from app.http.serializers.storage_uuid_serializer import *

from datetime import datetime, timedelta, date

import os

import uuid
import re
import pillow_heif
from PIL import Image

from ...core.helpers.global_variables import MESSAGE_UPLOAD_TYPE


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
        iv = b'bscKHn8REOJ2aikS'
        return BS, key, iv
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
    unpad = lambda s: s[:-ord(s[len(s) - 1:])]
    enc = base64.b64decode(enc)
    cipher = AES.new(key, AES.MODE_CBC, iv.encode())
    return unpad(cipher.decrypt(enc)).decode("utf-8")


def is_null_or_empty(_str):
    if is_none(_str):
        return True
    if isinstance(_str, str):
        if is_empty(_str):
            return True
        if len(_str.strip()) > 0:
            return _str.strip().isspace()
        return True
    return False


def is_none(v):
    if v is None:
        return True
    return False


def is_empty(_str):
    if isinstance(_str, str):
        return is_none(_str) or len(_str.strip()) == 0
    return False


def get_current_datetime():
    return datetime.utcnow() + timedelta(hours=7)


def save_file(file_input, full_path):
    with open(full_path, 'wb+') as f:
        for chunk in file_input.chunks():
            f.write(chunk)


def upload_file(request, user_email, folder_name, child_folder="", fname="", upload_type="DEFAULT"):
    ok = False
    list_link_public = []
    list_file_name = []
    msg = ''
    try:
        data_input = request.data
        number_file_init = data_input.get("numberFile", 0)
        str_datetime = get_current_datetime().strftime(DATETIME_FORMAT3)
        number_file = int(number_file_init)
        # print(request.FILES)
        # for i_file in range(number_file):
        if len(request.FILES.getlist('file')) > 0:

            for file_obj in request.FILES.getlist('file'):
                if file_obj.size > 5242880:
                    msg = MESSAGE_UPLOAD_TYPE[upload_type]["error_messages"]["file_size"]
                    break

                if file_obj.content_type not in ['image/heic', 'image/png', 'image/jpeg']:
                    msg = MESSAGE_UPLOAD_TYPE[upload_type]["error_messages"]["file_type"]
                    break

                name_file = file_obj.name
                name_file_split = name_file.split(".")
                if len(name_file_split) > 2:
                    msg = MESSAGE_UPLOAD_TYPE[upload_type]["error_messages"]["tail_file"]
                    break
                final_file = name_file_split[-1]

                if final_file.lower() not in ['png', 'jpg', 'jpeg', 'heic']:
                    msg = MESSAGE_UPLOAD_TYPE[upload_type]["error_messages"]["tail_file"]
                    break

                link_folder = UPLOAD_DIRECTORY + "/" + folder_name

                if not is_null_or_empty(child_folder):
                    link_folder = link_folder + "/" + child_folder

                file_name_init = convert_no_accent_vietnamese(file_obj.name)

                if not os.path.exists(link_folder):
                    os.makedirs(link_folder)

                abs_dir = os.path.abspath(link_folder)

                filename = str_datetime + "_" + file_name_init

                filepath = os.path.join(abs_dir, filename)

                save_file(file_obj, filepath)
                if file_obj.content_type == "image/heic":
                    # file_obj.format = 'jpg'
                    # file_obj.content_type = 'jpg'

                    file_name_init_heic = file_name_init.replace(".heic", ".png")
                    filepath_after_heic = os.path.join(abs_dir, file_name_init_heic)
                    process_heic_file(filepath, filepath_after_heic)
                    # link_public = link_public + "/" + str_datetime + "_" + file_name_init_heic
                    file_name_init = file_name_init_heic

                str_uuid = str(uuid.uuid4().node).zfill(16)
                link_public = UPLOAD_DIRECTORY_PUBLIC + str_uuid
                print("==============check download====================")
                print(file_obj.content_type)
                print(file_obj.content_type not in ['image/heic', 'image/png', 'image/jpeg', 'application/pdf'])
                if file_obj.content_type not in ['image/heic', 'image/png', 'image/jpeg', 'application/pdf']:
                    link_public = DOWNLOAD_DIRECTORY_PUBLIC + str_uuid

                list_link_public.append(link_public)
                list_file_name.append(file_name_init)

                # import thong tin file vao database
                save_data_db(user_email, folder_name, filepath, link_public, str_uuid, child_folder, fname)

            ok = True
        else:
            ok = False
            msg = MESSAGE_UPLOAD_TYPE[upload_type]["error_messages"]["tail_file_blank"]

        # link_folder = UPLOAD_DIRECTORY + "/" + folder_name
        # if not is_null_or_empty(child_folder):
        #     link_folder  = link_folder + "/" + child_folder
        # if not os.path.exists(link_folder):
        #     os.makedirs(link_folder)
        # str_datetime = get_current_datetime().strftime(DATETIME_FORMAT3)
        # link_public = UPLOAD_DIRECTORY_PUBLIC + "/" + "upload/" + folder_name + "/" + file_obj.name + "_"
        # abs_dir = os.path.abspath(link_folder)
        # filename = str_datetime + "_" + file_obj.name
        # filepath = os.path.join(abs_dir, filename)
        # print("++++++")
        # print(filepath)
        # print(link_public)
        #
        # save_file(file_obj, filepath)
        #
        # # import thong tin fil vao data base
        # ok = True
    except Exception as e:
        print("upload_file: {} --------------".format(fname))
        print(e)

    dict_output = {
        "ok": ok,
        "link_public": list_link_public,
        "file_name": list_file_name,
        "message": msg
    }
    return dict_output


def convert_no_accent_vietnamese(text, fname=""):
    """
    Convert from 'Tieng Viet co dau' thanh 'Tieng Viet khong dau'
    text: input string to be converted
    Return: string converted
    """

    new_text = ""
    try:
        patterns = {
            '[àáảãạăắằẵặẳâầấậẫẩ]': 'a',
            '[đ]': 'd',
            '[èéẻẽẹêềếểễệ]': 'e',
            '[ìíỉĩị]': 'i',
            '[òóỏõọôồốổỗộơờớởỡợ]': 'o',
            '[ùúủũụưừứửữự]': 'u',
            '[ỳýỷỹỵ]': 'y',
            '[ ]': "_"
        }
        if not is_null_or_empty(text):
            output_init = text.strip()
            output = output_init.lower()
            for regex, replace in patterns.items():
                output = re.sub(regex, replace, output)
                # deal with upper case
                output = re.sub(regex.upper(), replace.lower(), output)
                new_text = output
    except Exception as e:
        print(e)
        # logger.info("convert_no_accent_vietnamese >> {} Error/Loi : {}".format(fname, e))
    return new_text


def process_heic_file(file_path, filename_after):
    # image = cv2.imread(file_path)
    # cv2.imwrite(filename_after, image, [int(cv2.IMWRITE_JPEG_QUALITY), 100])
    # pi = cv2.imread('D:/opt/pdx/mypt/upload/tool_support/20220722_173624_sample1.heic')
    # cv2.imwrite('D:/opt/pdx/mypt/upload/tool_support/sample1.png', pi, [int(cv2.IMWRITE_JPEG_QUALITY), 100])

    # heif_file = pillow_heif.read_heif('D:/opt/pdx/mypt/upload/tool_support/20220725_140441_sample1.heic')
    # image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw", )
    # image.save("D:/opt/pdx/mypt/upload/tool_support/sample1.png", format("png"))
    print(file_path)
    print(filename_after)
    heif_file = pillow_heif.read_heif(file_path)
    image = Image.frombytes(heif_file.mode, heif_file.size, heif_file.data, "raw", )
    image.save(filename_after, format("png"))
    print(405)


def save_data_db(user_email, folder, link_folder, link_public, str_uuid, child_folder=None, fname=""):
    ok = False
    try:
        # str_uuid = str(uuid.uuid4().node).zfill(16)
        time_now = get_current_datetime()
        storage_uuid = StorageUuid()
        storage_uuid.uuid = str_uuid
        storage_uuid.email = user_email
        storage_uuid.folder = folder
        storage_uuid.child_folder = child_folder
        storage_uuid.update_time = time_now.strftime(DATETIME_FORMAT)
        storage_uuid.link_data = link_public
        storage_uuid.link_local = link_folder
        storage_uuid.save()
        ok = True



    except Exception as e:
        print("save_data_db:{} >> Error/Loi :{}".format(fname, e))
    return ok


def to_str_fr_list(_list):
    if isinstance(_list, list):
        return ';'.join([str(item) for item in _list])
