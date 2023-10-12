
from app.configs.variable import *
import requests

def call_api_save_file(request, number_files, user_email, fname=""):
    url = MEDIA_URL + NAME_SERVICE_MEDIA + "upload-file-private"
    try:

        files = {}

        cnt_send = 0

        ok_size = True
        ok_type_file = True
        for i_file in range(int(number_files)):
            cnt = i_file + 1
            key_file = 'file_{}'.format(cnt)




            # file_obj = request.FILES[key_file]
            file_obj = request.FILES.get(key_file)
            print("====================check up hinh =========================")
            print(file_obj.content_type)

            if file_obj.size > 5242880:
                ok_size = False
                break

            if file_obj.content_type not in ['image/heic', 'image/png', 'image/jpeg']:
                ok_type_file = False
                break

            name_file = file_obj.name
            name_file_split = name_file.split(".")
            if len(name_file_split) > 2:
                ok_type_file = False
            final_file = name_file_split[-1]
            if final_file.lower() not in ['png', 'jpg', 'jpeg', 'heic']:
                ok_type_file = False


            if file_obj is not None:
                cnt_send = cnt_send + 1
                files.update({
                    key_file: file_obj
                })


        if not ok_size:
            return STATUS_CODE_ERROR_SYSTEM, "Size hình vượt quá kích thước", {}

        if not ok_type_file:
            return STATUS_CODE_ERROR_SYSTEM, "Loại file không phù hợp", {}

        data = {
            "numberFile": cnt_send,
            "userEmail": user_email,
            "folder": "xe_cai_tien"

        }
        if len(files) > 0:
            proxies = {
                "http": None,
                "https": "proxy.hcm.fpt.vn",
            }
            res = requests.post(url=url,  files=files, data=data, proxies=proxies)

            if res is not None:
                if res.status_code == 200:

                    result = res.json()
                    status_code = result.get('statusCode')
                    if status_code == 1:
                        data_api = result.get('data', {})
                        # print("{} >> Call api :{} THANH CONG".format(fname, url))
                        # print(result)
                        # print(data_api)
                        return STATUS_CODE_SUCCESS, MESSAGE_API_SUCCESS, data_api
                    else:
                        print("{} >> Call api :{} >> status_code {} THAT BAI -------------------------------\n \n ".format(fname, url, status_code))
                        return STATUS_CODE_ERROR_LOGIC, MESSAGE_API_ERROR_LOGIC, {}
                else:
                    print("{} >> Call api :{} THAT BAI status code {} \n \n ".format(fname, url, res.status_code))
                    return STATUS_CODE_ERROR_SYSTEM, MESSAGE_API_ERROR_SYSTEM, {}
            else:

                print("{} >> Call api :{} THAT BAI res is None \n \n ".format(fname, url))
                return STATUS_CODE_ERROR_SYSTEM, MESSAGE_API_ERROR_SYSTEM, {}
        else:
            return STATUS_CODE_ERROR_SYSTEM, "Không có data", {}

    except Exception as ex:
        print("{} >> Call api :{} THAT BAI: {} \n \n ".format(fname, url, ex))
        return STATUS_CODE_ERROR_SYSTEM, MESSAGE_API_ERROR_SYSTEM, {}
    
def call_api_save_file_new(request, user_email, fname=""):
    url = MEDIA_URL + NAME_SERVICE_MEDIA + "upload-file-private"
    try:

        files = {}

        cnt_send = 0
        # print(96)
        # print(request.FILES.getlist('file'))
        # for i_file in range(int(number_files)):
        cnt = 0

        ok_size = True
        ok_type_file = True

        for i_file in request.FILES.getlist('file'):
            # print("----------------------")
            #
            # print(i_file.content_type)
            # print("==========================================UP HINH KIEM TRA CONTENT TYPE========================================")
            #
            # print(i_file.content_type)

            if i_file.size > 5242880:
                ok_size = False
                break

            if i_file.content_type not in ['image/heic', 'image/png', 'image/jpeg']:
                ok_type_file = False
                break

            name_file = i_file.name
            name_file_split = name_file.split(".")
            if len(name_file_split) > 2:
                ok_type_file = False
            final_file = name_file_split[-1]

            if final_file.lower() not in ['png', 'jpg', 'jpeg', 'heic']:
                ok_type_file = False



            cnt = cnt + 1
            key_file = 'file_{}'.format(cnt)
            #
            # # file_obj = request.FILES[key_file]
            # file_obj = request.FILES.get(key_file)


            if i_file is not None:
                cnt_send = cnt_send + 1
                files.update({
                    key_file: i_file
                })


        if not ok_size:
            return 99, "Size hình vượt quá kích thước", {}

        if not ok_type_file:
            return 99, "Loại file không phù hợp", {}

        data = {
            "numberFile": cnt_send,
            "userEmail": user_email,
            "folder": "tool_support"

        }
        if len(files) > 0:
            # proxies = {
            #     "http": None,
            #     "https": "proxy.hcm.fpt.vn",
            # }
            res = requests.post(url=url,  files=files, data=data)

            if res is not None:
                if res.status_code == 200:

                    result = res.json()
                    status_code = result.get('statusCode')
                    if status_code == 1:
                        data_api = result.get('data', {})
                        print("{} >> Call api :{} THANH CONG".format(fname, url))
                        # print(result)
                        # print(data_api)
                        return STATUS_CODE_SUCCESS, MESSAGE_API_SUCCESS, data_api
                    else:
                        print("{} >> Call api :{} >> status_code {} THAT BAI -------------------------------\n \n ".format(fname, url, status_code))
                        return STATUS_CODE_ERROR_LOGIC, MESSAGE_API_ERROR_LOGIC, {}
                else:
                    print("{} >> Call api :{} THAT BAI status code {} \n \n ".format(fname, url, res.status_code))
                    return STATUS_CODE_ERROR_SYSTEM, MESSAGE_API_ERROR_SYSTEM, {}
            else:

                print("{} >> Call api :{} THAT BAI res is None \n \n ".format(fname, url))
                return STATUS_CODE_ERROR_SYSTEM, MESSAGE_API_ERROR_SYSTEM, {}
        else:
            return STATUS_CODE_ERROR_SYSTEM, "Không có data", {}

    except Exception as ex:
        print("{} >> Call api :{} THAT BAI: {} \n \n ".format(fname, url, ex))
        return STATUS_CODE_ERROR_SYSTEM, MESSAGE_API_ERROR_SYSTEM, {}