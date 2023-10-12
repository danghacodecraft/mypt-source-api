import concurrent.futures
import json

import redis
from django.conf import settings as project_settings
from django.core.exceptions import RequestDataTooBig
from rest_framework.viewsets import ViewSet

from app.configs import app_settings
from ..models.iqc_config import IqcConfig
from ..validations.iqc_validation import *
from ...configs.service_api_config import IQC_API, SERVICE_CONFIG
from core.helpers import auth_session_handler as authSessionHandler
from core.helpers import create_image_iqc
from core.helpers import helper
from core.helpers.global_variable import *
from core.helpers.iqc_global_variable import *
from core.helpers.my_datetime import getSecondFromNowToLastOfDay
from core.helpers.response import *
from core.helpers.utils import *
import ast


def check_iqc_contract(data={}):
    msg = ""

    if 'typeiQC' not in data:
        msg += "Sai thông tin đầu vào, không có loại tác vụ"

    if empty(data['typeiQC']) or \
            data['typeiQC'] not in ['trien_khai', 'ha_tang_ngoai_vi', 'hop_dong_tra_ve']:
        msg += "Loại tác vụ không hợp lệ"
    else:
        if data['typeiQC'] == 'trien_khai':
            validate = iQCDeploymentValidate(data=data)
        elif data['typeiQC'] == 'ha_tang_ngoai_vi':
            validate = iQCPracticePointValidate(data=data)
        elif data['typeiQC'] == 'hop_dong_tra_ve':
            validate = iQCReturnContractVeValidate(data=data)

        if not validate.is_valid():
            msg += list(validate.errors.values())[0][0]
    return msg


def search_deployment_contract(request, dataInput={}):
    # api này search hợp đồng triển khai
    result = []
    app_env = "base_http_" + project_settings.APP_ENVIRONMENT
    params = {
        "Contract": dataInput['contractCode'],
        "MobiAccount": dataInput['accountMBN']
    }
    response = call_api_method_get(host=IQC_API[app_env] + IQC_API['search_deployment_contract']['func'],
                                   params=params)

    for data in response['ResponseResult']['Results']:
        result.append({
            'name': data['Contract'],
            'image': revert_link_image(request, data['Image']),
            'status': data['Status'],
            'version': -1
        })

    return result


def search_practice_point(request, dataInput={}):
    # api này search hợp đồng triển khai
    result = []
    app_env = "base_http_" + project_settings.APP_ENVIRONMENT
    data = {
        "Code": dataInput['contractCode'],
        "MobiAccount": dataInput['accountMBN']
    }
    response = call_api_method_post(host=IQC_API[app_env] + IQC_API['search_practice_point']['func'],
                                    json=data)

    for data in response['ResponseResult']['Results']:
        result.append({
            'name': data['PracticePoint'],
            'image': revert_link_image(request, data['Image']),
            'status': data['Status'],
            'version': data['Version']
        })

    return result


def search_return_contract(request, dataInput={}):
    # api này search hợp đồng triển khai
    result = []
    app_env = "base_http_" + project_settings.APP_ENVIRONMENT
    params = {
        "Contract": dataInput['contractCode'],
        "MobiAccount": dataInput['accountMBN']
    }
    response = call_api_method_get(host=IQC_API[app_env] + IQC_API['search_return_contract']['func'],
                                   params=params)

    for data in response['ResponseResult']['Results']:
        result.append({
            'name': data['Contract'],
            'image': revert_link_image(request, data['Image']),
            'status': data['Status'],
            'version': -1
        })

    return result


def load_album_deployment(request, dataInput={}):
    """
    statusImage
    1: Chưa kiểm soát
    2: Đang kiểm soát
    3: Đã kiểm soát
    4: Chờ kiểm soát lại
    5: Không có ảnh - thiểu ảnh
    :return:
    """
    mobi_account = dataInput.get("accountMBN", "")
    per_page = dataInput.get("perPage", MAX_PAGE_SIZE)
    page = dataInput.get("page")

    app_env = "base_http_" + project_settings.APP_ENVIRONMENT
    proxies = {
        "http": None,
        "https": "proxy.hcm.fpt.vn",
    }
    response = call_api(
        host=IQC_API[app_env],
        func=IQC_API["load_album_deployment"][
                 "func"] + f"?MobiAccount={mobi_account}&PerPage={per_page}&PageNum={page}",
        method=IQC_API["load_album_deployment"]["method"],
        proxies=proxies
    )
    data_json = json.loads(response)

    list_data = []
    data_return = None
    if "ResponseResult" in data_json \
            and data_json["ResponseResult"]["ErrorCode"] == IQC_STATUS_CODE_SUCCESS:
        results = data_json["ResponseResult"]["Results"]

        for data in results["data"]:
            list_data.append({"name": data.get("Contract", ""),
                              "status": data.get("Status", ""),
                              "image": revert_link_image(request, data.get("InsteadImg", ""))
                              })
        data_return = {
            "perPage": results["limit"],
            "page": results["page"],
            "totalPage": results["totalpage"],
            "listData": list_data
        }

    return data_return


def create_contract_deployment(dataInput={}):
    try:
        id_img = "5b31fc4621dafa1a8f323ea6"
        trans_type = get_or_save_iqc_config_to_redis(IQC_CONFIG_TRANSACTION_TYPES)
        house_model = get_or_save_iqc_config_to_redis(IQC_CONFIG_HOUSE_MODELS)

        if int(dataInput['modelHouse']) > len(house_model['aChoice']) or int(dataInput['typeServiceDeploy']) > len(
                trans_type['aChoice']):
            return "Sai thông tin mô hình nhà hoặc loại dịch vụ triển khai"

        contract = {
            "Contract": dataInput['nameContract'],
            "MobiAccount": dataInput['accountMBN'],
            "DeviceIMEI": dataInput['deviceID'],
            "LocationUpload": dataInput['locationUpload'],
            "LocationContract": dataInput['locationContract'],
            "HouseModel": house_model['aChoice'][str(dataInput['modelHouse'])],
            "TransactionType": trans_type['aChoice'][str(dataInput['typeServiceDeploy'])],
            "Images": [
                {
                    "link": image['image'],
                    "index": image['index'],
                    "accuracy": "1",
                    "_id": id_img,
                    "cause": []
                } for image in dataInput['images']]
        }

        app_env = "base_http_" + project_settings.APP_ENVIRONMENT
        response = call_api_method_post(
            host=IQC_API[app_env] + IQC_API["create_contract_deployment"]["func"],
            json=contract
        )
    except Exception as ex:
        print(str(ex))
        return None
    return response


def update_contract_deployment(dataInput={}):
    try:
        current_date = get_current_datetime()
        if dataInput['accuracyDate']:
            accuracyDate = datetime.strptime(dataInput['accuracyDate'], "%H:%M:%S %d/%m/%Y")
            dayTime = current_date - accuracyDate
            # nếu lớn hơn 48h trả về None
            if dayTime.total_seconds() > 172800:
                return None
        else:
            accuracyDate = ""

        list_image = [x["image"] for x in dataInput["images"]]

        list_image = decode_link_images(list_image)
        # nếu không đủ 6 link ảnh
        if len(list_image) != 6:
            return None

        for index, value in enumerate(dataInput['images']):
            value['link'] = list_image[index]

        contract = {
            "Contract": dataInput['nameContract'],
            "MobiAccount": dataInput['accountMBN'],
            "DeviceIMEI": dataInput['deviceID'],
            "LocationUpload": dataInput['locationUpload'],
            "Images": [
                {
                    "link": list_image[image['index']],
                    "index": image['index'],
                    "accuracy": image['status'],
                    "cause": []
                } for image in dataInput['images']]
        }

        app_env = "base_http_" + project_settings.APP_ENVIRONMENT
        response = call_api_method_post(
            host=IQC_API[app_env] + IQC_API["update_contract_deployment"]["func"],
            json=contract
        )
    except Exception as ex:
        print(str(ex))
        return None
    return response


def get_or_save_iqc_config_to_redis(config_key):
    data_result = {
        "listChoice": None,
        "aChoice": {}
    }

    redis_instance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                       , port=project_settings.REDIS_PORT_CENTRALIZED
                                       , db=project_settings.REDIS_DATABASE_SERVICE_CHECKIN,
                                       password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                       , decode_responses=True, charset="utf-8")
    iqc_configs_str = redis_instance.get(f'{IQC_CONFIG_CACHE_KEY_NAME}:{config_key}')

    if iqc_configs_str is None:
        # luu tat ca config vao redis
        iqc_config_data = {}
        dict_config_data = IqcConfig.objects.values('config_key', 'config_value')
        for value in list(dict_config_data):
            if value['config_key'] in LIST_DATA_IQC_CONFIG_CAPITALIZE:
                for item in value['config_value']:
                    item['name'] = item['name'].capitalize()
            data_save = {
                "listChoice": value['config_value'],
                "aChoice": {}
            }
            if value['config_key'] in LIST_DATA_IQC_CONFIG:
                # luu vao redis
                for item in value['config_value']:
                    data_save['aChoice'][int(item['index'])] = item['name']
            if value['config_key'] == IQC_CONFIG_TITLE_DEPLOYMENT_CONTRACT:
                data_save = value['config_value']
            redis_instance.set(f'{IQC_CONFIG_CACHE_KEY_NAME}:{value["config_key"]}', json.dumps(data_save))

        # tra value theo key
        data_result = json.loads(redis_instance.get(f'{IQC_CONFIG_CACHE_KEY_NAME}:{config_key}'))
    else:
        # return json.loads(iqc_configs_str)
        return json.loads(iqc_configs_str)
        # iqc_configs = json.loads(iqc_configs_str)
        # iqc_config_key_str = f"{IQC_CONFIG_CACHE_KEY_NAME}:{config_key}"
        #
        # if iqc_config_key_str not in iqc_configs:
        #     print(22333)
        #     # luu value key nay vao redis
        #     list_data = IqcConfig.objects.filter(config_key=config_key).values("config_key", "config_value")
        #     if len(list_data) > 0:
        #         iqc_configs[f'{IQC_CONFIG_CACHE_KEY_NAME}:{list_data[0]["config_key"]}'] = list_data[0]["config_value"]
        #         # luu vao redis
        #         redis_instance.set(IQC_CONFIG_CACHE_KEY_NAME, str(iqc_configs))
        #         # tra value theo key
        #         data_result = list_data[0]["config_value"]
        # else:
        #     # lay value cua key
        #     data_result = iqc_configs[iqc_config_key_str]
    return data_result


def upload_image_get_link(**kwargs):
    try:
        app_env = project_settings.APP_ENVIRONMENT
        image = kwargs.pop("image")
        image_name = kwargs.pop("image_name")
        contract = kwargs.pop("contract")
        contract = contract.replace("/", "").replace("\\", "")
        location = kwargs.pop("location")
        time_upload = kwargs.pop("time_upload")
        mobi_account = kwargs.pop("mobi_account")

        name_file_split = image_name.split(".")
        file_name = location + time_upload + name_file_split[0]
        file_name = file_name.replace("/", "") \
                        .replace("\\", "") \
                        .replace(",", "") \
                        .replace(".", "") \
                        .replace(":", "") \
                        .replace(" ", "") + "." + name_file_split[1]

        # Goi upload anh tai day
        headers = {
            'Content-Disposition': f'"attachment; filename="{file_name}"',
            'Session-ID': app_settings.IQC_SESSION_ID,
            'X-Chunk-Index': '1',
            'X-Chunks-Number': '10',
            'Content-Length': str(image.size),
            'Connection': 'Keep-Alive',
            'iqc-contract-name': str(contract),
            'iqc-mobi-account': str(mobi_account),
            'Content-Type': 'image/jpeg',
        }

        if app_env in ["staging", "production"]:
            response = requests.post(IQC_BASE_URL_UPLOAD + "upload",
                                     headers=headers,
                                     data=image,
                                     proxies=PROXIES)
        else:
            response = requests.post(IQC_BASE_URL_UPLOAD + "upload",
                                     headers=headers,
                                     data=image)

        print(
            f">> Khi upload anh >> data: {image} >> headers: {headers} >> response: {response.text}, status: {response.status_code}")
        if response.status_code == 200:
            res_data = json.loads(response.text)
            if res_data["ErrorCode"] == 0:
                return res_data["ImgPath"]
            return None
        else:
            return None
    except Exception as ex:
        print(f"{datetime.now()} >> upload_image_get_link >> {ex}")
        return None


def upload_and_get_link_one_image(mobi_account, image_info):
    try:
        contract = image_info["contract"]
        location = image_info["location"]
        time_upload = image_info["timeUpload"]
        image = image_info["image"]
        image_name = image.name

        # Xy ly hinh anh
        out_image = create_image_iqc.create_and_save_image(image, contract, location, time_upload)
        if out_image is None:
            print(f"[{datetime.now()}][upload_and_get_link_one_image] >> ERROR: lỗi khi xử lý hình ảnh!")
            return ""

        # upload hinh anh
        link = upload_image_get_link(mobi_account=mobi_account,
                                     contract=contract,
                                     location=location,
                                     time_upload=time_upload,
                                     image=out_image,
                                     image_name=image_name)
        if link is None:
            print(
                f"[{datetime.now()}][upload_and_get_link_one_image] >> ERROR: lỗi khi upload hình ảnh >> image la: {out_image} >> image_name: {image_name}")
            return ""
        return link
    except Exception as ex:
        print(f"[{datetime.now()}][upload_and_get_link_one_image] >> ERROR: {ex}")
        return ""


def update_mock_account_mbn(email={}, **kwargs):
    redis_instance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                       , port=project_settings.REDIS_PORT_CENTRALIZED
                                       , db=project_settings.REDIS_DATABASE_SERVICE_CHECKIN,
                                       password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                       , decode_responses=True, charset="utf-8")
    key = kwargs.pop('config_key', None)
    fake_data_raw = IqcConfig.objects.filter(config_key=key).first()
    fake_data_json = json.loads(fake_data_raw.config_value)
    IqcConfig.objects.filter(config_key=key).update(config_value=json.dumps(email))

    secondTimeOut = getSecondFromNowToLastOfDay()

    if redis_instance.get('allAccountMobiNet'):
        data = redis_instance.get('allAccountMobiNet')
        json_data = json.loads(data)
        for key, value in email.items():
            x = key.split("-")
            json_data.update({'mbnacc-' + x[1]: value})
    else:
        allAccountMobiNet = {}
        for key, value in fake_data_json.items():
            x = key.split("-")
            allAccountMobiNet.update({'mbnacc-' + x[1]: value})
        json_data = allAccountMobiNet

        app_env = "base_http_" + project_settings.APP_ENVIRONMENT
        call_api(
            host=SERVICE_CONFIG['HO-CHECKIN'][app_env],
            func=SERVICE_CONFIG['HO-CHECKIN']["save_mbn_account_from_isc"]["func"],
            # params=params,
            method=SERVICE_CONFIG['HO-CHECKIN']["save_mbn_account_from_isc"]["method"],
            # proxies=PROXIES
        )
    redis_instance.set('allAccountMobiNet', json.dumps(json_data), secondTimeOut)

    return json_data


def delete_mock_account_mbn(email={}, **kwargs):
    redis_instance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                       , port=project_settings.REDIS_PORT_CENTRALIZED
                                       , db=project_settings.REDIS_DATABASE_SERVICE_CHECKIN,
                                       password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                       , decode_responses=True, charset="utf-8")

    key = kwargs.pop('config_key', None)
    fake_data_raw = IqcConfig.objects.filter(config_key=key).first()
    fake_data_json = json.loads(fake_data_raw.config_value)
    for key, value in email.items():
        if key in fake_data_json:
            del fake_data_json[key]
    IqcConfig.objects.filter(config_key=key).update(config_value=json.dumps(fake_data_json))

    secondTimeOut = getSecondFromNowToLastOfDay()
    data = redis_instance.get('allAccountMobiNet')
    json_data = json.loads(data)

    for key, value in email.items():
        x = value.split("-")
        if 'mbnacc-' + x[0] in json_data:
            del json_data['mbnacc-' + x[0]]
    redis_instance.set('allAccountMobiNet', json.dumps(json_data), secondTimeOut)
    return json_data


def get_mock_account_mbn(email={}):
    fake_data_raw = IqcConfig.objects.filter(config_key='IQC_EMPLOYEES_FAKE_INFO').first()
    fake_data_json = json.loads(fake_data_raw.config_value)
    fake_data_json.update(email)
    json_data = fake_data_json
    return json_data


def get_accountMBN(empCode):
    redis_instance = redis.StrictRedis(host=project_settings.REDIS_HOST_CENTRALIZED
                                       , port=project_settings.REDIS_PORT_CENTRALIZED
                                       , db=project_settings.REDIS_DATABASE_SERVICE_CHECKIN,
                                       password=project_settings.REDIS_PASSWORD_CENTRALIZED
                                       , decode_responses=True, charset="utf-8")
    data = redis_instance.get('allAccountMobiNet')
    if data:
        json_data = json.loads(data)
        if 'mbnacc-' + empCode in json_data:
            return json_data['mbnacc-' + empCode]
    else:
        # get data fake trong db
        fake_data_raw = IqcConfig.objects.filter(config_key='IQC_EMPLOYEES_FAKE_INFO').first()
        fake_data_json = json.loads(fake_data_raw.config_value)
        fake_data = update_mock_account_mbn(fake_data_json, config_key='IQC_EMPLOYEES_FAKE_INFO')

        # save db từ isc vào trong redis
        app_env = "base_http_" + project_settings.APP_ENVIRONMENT
        call_api(
            host=SERVICE_CONFIG['HO-CHECKIN'][app_env],
            func=SERVICE_CONFIG['HO-CHECKIN']["save_mbn_account_from_isc"]["func"],
            # params=params,
            method=SERVICE_CONFIG['HO-CHECKIN']["save_mbn_account_from_isc"]["method"],
            # proxies=PROXIES
        )
        data = redis_instance.get('allAccountMobiNet')
        json_data = json.loads(data)
        json_data.update(fake_data)
        if 'mbnacc-' + empCode in json_data:
            return json_data['mbnacc-' + empCode]

    return ""


class iQCView(ViewSet):
    def check_iqc_contract(self, request):
        try:
            getData = request.data
            msgError = check_iqc_contract(getData)
            if not empty(msgError):
                return response_data(data=None, message=msgError, status=STATUS_CODE_INVALID_INPUT)
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.check_iqc_contract.__name__, ex))
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)
        return response_data(data=None, message="Thành công", status=STATUS_CODE_SUCCESS)

    def load_iqc_album_upload_deployment(self, request):
        try:
            getData = request.data
            data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
            getData['accountMBN'] = get_accountMBN(data_token['empCode'])
            data = load_album_deployment(request, getData)
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.load_iqc_album_upload_deployment.__name__,
                                                        ex))
            api_save_log(request=request, data_input=getData, api_status=0, err_analysis=0, api_name="load_iqc_album_upload_deployment", status_code=STATUS_CODE_FAILED, message=MESSAGE_API_FAILED)
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)
        api_save_log(request=request, data_input=getData, data_output=data, api_name="load_iqc_album_upload_deployment", message=MESSAGE_API_SUCCESS)
        return response_data(data=data, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)

    def get_iqc_detail_deployment(self, request):
        try:
            getData = request.data
            data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
            getData['accountMBN'] = get_accountMBN(data_token['empCode'])
            listTitleDeploymentContract = get_or_save_iqc_config_to_redis(IQC_CONFIG_TITLE_DEPLOYMENT_CONTRACT)
            contractCode = getData.get("contractCode", "")
            data_return = None

            app_env = "base_http_" + project_settings.APP_ENVIRONMENT
            response = call_api_method_get(
                host=IQC_API[app_env] + IQC_API["get_contract_deployment_detail"]["func"],
                params={'Contract': contractCode}
            )
            if "ResponseResult" in response \
                    and response["ResponseResult"]["ErrorCode"] == IQC_STATUS_CODE_SUCCESS:
                result = response["ResponseResult"]["Results"]

                data_return = {
                    "nameContract": result.get('Contract', ''),
                    "accountMBN": getData.get('MobiAccount', ''),
                    "typeServiceDeploy": result['TransactionType'],
                    "modelHouse": result['HouseModel'],
                    "timeUpload": result['CreatedDate'],
                    "statusiQC": result['Status'],
                    "locationUpload": result['LocationUpload'],
                    "locationContract": result['LocationContract'],
                    "images": [
                        {
                            "image": revert_link_image(request, image['link']),
                            "status": int(image['accuracy']),
                            "name": listTitleDeploymentContract[int(image['index'])],
                            "index": image['index']
                        } for image in result['Images']]
                }
                if 'AccuracyDate' not in result:
                    data_return['accuracyDate'] = ""
                else:
                    data_return['accuracyDate'] = result['AccuracyDate']

                if empty(data_return['accuracyDate']):
                    data_return['accuracyDate'] = ""
                else:
                    data_return['accuracyDate'] = datetime.strptime(data_return['accuracyDate'],
                                                                    "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                        "%H:%M:%S %d/%m/%Y")

                data_return['timeUpload'] = datetime.strptime(data_return['timeUpload'],
                                                              "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%H:%M:%S %d/%m/%Y")
            else:
                data_return = {
                    "nameContract": "",
                    "accountMBN": "",
                    "typeServiceDeploy": "",
                    "modelHouse": "",
                    "timeUpload": "",
                    "statusiQC": 0,
                    "locationUpload": "",
                    "locationContract": "",
                    "images": [
                        {
                            "image": "",
                            "status": 1,
                            "name": listTitleDeploymentContract[int(image)],
                            "index": image
                        } for image in range(6)]
                }

            if data_return is None:
                api_save_log(request=request, data_input=getData, data_output=data_return, api_name="get_iqc_detail_deployment", status_code=STATUS_CODE_NO_DATA, message="Find not found!")
                return response_data(data=data_return, status=STATUS_CODE_NO_DATA, message="Find not found!")
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.get_iqc_detail_deployment.__name__, ex))
            api_save_log(request=request, data_input=getData, api_status=0, err_analysis=0, api_name="get_iqc_detail_deployment", status_code=STATUS_CODE_FAILED, message=str(ex))
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)
        api_save_log(request=request, data_input=getData, data_output=data_return, api_name="get_iqc_detail_deployment", message=MESSAGE_API_SUCCESS)
        return response_data(data=data_return, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)

    def create_contract_deployment(self, request):
        try:
            getData = request.data
            data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
            getData['accountMBN'] = get_accountMBN(data_token['empCode'])
            getData['deviceID'] = data_token['deviceId']
            getData['headers'] = request.headers

            serializer_validate = IqcCreateDeploymentContractValidate(data=getData)
            if not serializer_validate.is_valid():
                return response_data(data=None, status=STATUS_CODE_INVALID_INPUT,
                                     message=list(serializer_validate.errors.values())[0][0])

            data = create_contract_deployment(getData)

            if data == "Sai thông tin mô hình nhà hoặc loại dịch vụ triển khai":
                api_save_log(request=request, data_input=getData, api_status=0, err_analysis=-1, api_name="create_contract_deployment", status_code=STATUS_CODE_FAILED, message=data)
                return response_data(message=data, data=None, status=STATUS_CODE_FAILED)

            if data is False or data['ResponseResult']['ErrorCode'] != 0:
                api_save_log(request=request, data_input=getData, api_status=0, err_analysis=-1, api_name="create_contract_deployment", status_code=STATUS_CODE_FAILED, message="Upload ảnh không thành công")
                return response_data(message="Upload ảnh không thành công", data=None, status=STATUS_CODE_FAILED)
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.create_contract_deployment.__name__, ex))
            api_save_log(request=request, data_input=getData, api_status=0, err_analysis=0, api_name="create_contract_deployment", status_code=STATUS_CODE_FAILED, message=str(ex))
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)
        api_save_log(request=request, data_input=getData, api_name="create_contract_deployment", message="Upload ảnh thành công")
        return response_data(data=None, message="Upload ảnh thành công", status=STATUS_CODE_SUCCESS)

    def update_contract_deployment(self, request):
        try:
            getData = request.data
            data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
            getData['accountMBN'] = get_accountMBN(data_token['empCode'])
            getData['deviceID'] = data_token['deviceId']

            serializer_validate = IqcUpdateDeploymentContractValidate(data=getData)
            if not serializer_validate.is_valid():
                api_save_log(request=request, data_input=getData, api_status=0, err_analysis=-1, api_name="update_contract_deployment", status_code=STATUS_CODE_INVALID_INPUT, message=list(serializer_validate.errors.values())[0][0])
                return response_data(data=None, status=STATUS_CODE_INVALID_INPUT,
                                     message=list(serializer_validate.errors.values())[0][0])

            dataUpload = update_contract_deployment(getData)

            if dataUpload is None:
                api_save_log(request=request, data_input=getData, api_status=0, err_analysis=0, api_name="update_contract_deployment", status_code=STATUS_CODE_FAILED, message="Cập nhật ảnh không thành công")
                return response_data(message="Cập nhật ảnh không thành công", data=None, status=STATUS_CODE_FAILED)
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.update_contract_deployment.__name__, ex))
            api_save_log(request=request, data_input=getData, api_status=0, err_analysis=0, api_name="update_contract_deployment", status_code=STATUS_CODE_FAILED, message=str(ex))
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)
        api_save_log(request=request, data_input=getData, api_name="update_contract_deployment", message="Cập nhật ảnh thành công")
        return response_data(data=None, message="Cập nhật ảnh thành công", status=STATUS_CODE_SUCCESS)

    def load_iqc_upload_practice_point(self, request):
        try:
            data = request.data

            user_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
            if user_token is None:
                api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="load_iqc_upload_practice_point", status_code=STATUS_CODE_ERROR_SYSTEM, message=MESSAGE_API_ERROR_SYSTEM)
                return response_data(data=None, status=STATUS_CODE_ERROR_SYSTEM, message=MESSAGE_API_ERROR_SYSTEM)

            emp_code = user_token["empCode"]
            mobi_account = get_accountMBN(emp_code)
            if empty(mobi_account):
                api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="load_iqc_upload_practice_point", status_code=STATUS_CODE_FAILED, message="Account Mobinet không tồn tại!")
                return response_data(data=None, status=STATUS_CODE_FAILED, message="Account Mobinet không tồn tại!")

            per_page = data.get("perPage", MAX_PAGE_SIZE)
            page = data.get("page", 1)

            params = {
                "MobiAccount": mobi_account,

                "PerPage": per_page,
                "PageNum": page
            }

            app_env = "base_http_" + project_settings.APP_ENVIRONMENT
            response = call_api(
                host=IQC_API[app_env],
                func=IQC_API["load_iqc_upload_practice_point"]["func"],
                params=params,
                method=IQC_API["load_iqc_upload_practice_point"]["method"],
                # proxies=PROXIES
            )
            res_data = json.loads(response)
            if "ResponseResult" in res_data \
                    and res_data["ResponseResult"]["ErrorCode"] == IQC_STATUS_CODE_SUCCESS:
                results = res_data["ResponseResult"]["Results"]
                # Xu ly output tra
                list_data = []
                for result in results['data']:
                    list_data.append({
                        # name là practicePoint (sửa tên cho cùng model bên mobile)
                        'name': result.get('PracticePoint', ''),
                        'status': result.get('Status', ''),
                        'image': revert_link_image(request, result.get('InsteadImg', '')),
                        'version': result['Version'],

                        # 'mobiAccount': result['MobiAccount'],
                        # 'deviceIMEI': result['DeviceIMEI'],
                        # 'locationUpload': result['LocationUpload'],
                        # 'locationPracticePoint': result['LocationPracticePoint']
                        # if 'LocationPracticePoint' in result else '',
                        # 'accuracyDate': result['AccuracyDate'],
                        # 'images': result['Images'],
                        # 'accuracyBy': result['AccuracyBy'],
                        # 'locationContract': result['LocationContract'],
                    })

                data_return = {
                    "perPage": results["limit"],
                    "page": results["page"],
                    "totalPage": results["totalpage"],
                    "listData": list_data
                }
                api_save_log(request=request, data_input=data, data_output=data_return, api_name="load_iqc_upload_practice_point", message=MESSAGE_API_SUCCESS)
                return response_data(data=data_return, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.load_iqc_upload_practice_point.__name__,
                                                        ex))
            api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="load_iqc_upload_practice_point", status_code=STATUS_CODE_FAILED, message=str(ex))
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)

    def load_iqc_detail_practice_point(self, request):
        try:
            user_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
            if user_token is None:
                api_save_log(request=request, data_input=request.data.copy(), api_status=0, err_analysis=0, api_name="load_iqc_detail_practice_point", status_code=STATUS_CODE_ERROR_SYSTEM, message=MESSAGE_API_ERROR_SYSTEM)
                return response_data(data=None, status=STATUS_CODE_ERROR_SYSTEM, message=MESSAGE_API_ERROR_SYSTEM)

            emp_code = user_token["empCode"]
            mobi_account = get_accountMBN(emp_code)
            if empty(mobi_account):
                api_save_log(request=request, data_input=request.data.copy(), api_status=0, err_analysis=0, api_name="load_iqc_detail_practice_point", status_code=STATUS_CODE_FAILED, message="Account Mobinet không tồn tại!")
                return response_data(data=None, status=STATUS_CODE_FAILED, message="Account Mobinet không tồn tại!")

            data = request.data

            code = data.get("contractCode", "")
            version = data.get("version", None)

            params = {
                "Code": code,
            }
            if version:
                params.update({"Version": version})
            app_env = "base_http_" + project_settings.APP_ENVIRONMENT
            response = call_api(
                host=IQC_API[app_env],
                func=IQC_API["load_iqc_detail_practice_point"]["func"],
                params=params,
                method=IQC_API["load_iqc_detail_practice_point"]["method"],
                # proxies=PROXIES
            )

            res_data = json.loads(response)
            if "ResponseResult" in res_data \
                    and res_data["ResponseResult"]["ErrorCode"] == IQC_STATUS_CODE_SUCCESS:
                results = res_data["ResponseResult"]["Results"]
                detail = {
                    "practicePoint": results["PracticePoint"],
                    "version": results["Version"],
                    "status": results["Status"],
                    "updatedDate": helper.format_date_time(results["UpdatedDate"]),
                    "images": [dict(
                        link1=revert_link_image(request, image['link1']),
                        link2=revert_link_image(request, image['link2']) if image['link2'] else '',
                        accuracy2=int(image['accuracy2']) if image['accuracy2'] else None,
                        accuracy1=int(image['accuracy1']) if image['accuracy1'] else None,
                        fixError=image['fixError'],
                        causeImage=image['causeImage'],
                        # _id=image['_id'],
                        # causeError=image['causeError'],
                    ) for image in results["Images"]]

                    # "mobiAccount": results["MobiAccount"],
                    # "deviceIMEI": results["DeviceIMEI"],
                    # "createdBy": results["CreatedBy"],
                    # "updatedBy": results["UpdatedBy"],
                    # "locationUpload": results["LocationUpload"],
                    # "locationPracticePoint": results["LocationPracticePoint"],
                    # "accuracyDate": results["AccuracyDate"],
                    # "accuracyBy": results["AccuracyBy"],
                    # "createdDate": results["CreatedDate"],
                }

                if not empty(detail['updatedDate']):
                    detail['updatedDate'] = datetime.strptime(detail['updatedDate'],
                                                              "%d/%m/%Y %H:%M:%S").strftime("%H:%M:%S %d/%m/%Y")
                api_save_log(request=request, data_input=data, data_output=detail, api_name="load_iqc_detail_practice_point", message=MESSAGE_API_SUCCESS)
                return response_data(data=detail, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)
            api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="load_iqc_detail_practice_point", status_code=STATUS_CODE_FAILED, message=res_data['ResponseResult']['Message'])
            return response_data(message=res_data['ResponseResult']['Message'], data=None, status=STATUS_CODE_FAILED)

        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.load_iqc_detail_practice_point.__name__,
                                                        ex))
            api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="load_iqc_detail_practice_point", status_code=STATUS_CODE_FAILED, message=str(ex))
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)

    def practice_point_get_cause_image(self, request):
        try:
            listPracticePointCause = get_or_save_iqc_config_to_redis(IQC_CONFIG_PRACTICE_POINT_CAUSE)
            if listPracticePointCause is None:
                raise Exception("Lỗi khi lấy danh sách mô hình nhà trong redis!")
        except Exception as ex:
            print(
                "{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.practice_point_get_cause_image.__name__, ex))
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)
        return response_data(data=listPracticePointCause['listChoice'])

    def create_practice_point(self, request):
        try:
            user_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
            if user_token is None:
                api_save_log(request=request, data_input=request.data.copy(), api_status=0, err_analysis=0, api_name="create_practice_point", status_code=STATUS_CODE_ERROR_SYSTEM, message=MESSAGE_API_ERROR_SYSTEM)
                return response_data(data=None, status=STATUS_CODE_ERROR_SYSTEM, message=MESSAGE_API_ERROR_SYSTEM)

            emp_code = user_token["empCode"]
            mobi_account = get_accountMBN(emp_code)
            if empty(mobi_account):
                api_save_log(request=request, data_input=request.data.copy(), api_status=0, err_analysis=0, api_name="create_practice_point", status_code=STATUS_CODE_FAILED, message="Account Mobinet không tồn tại!")
                return response_data(data=None, status=STATUS_CODE_FAILED, message="Account Mobinet không tồn tại!")

            data = request.data
            iqc_serializer_validate = IqcCreatePracticePointValidate(data=data)
            if not iqc_serializer_validate.is_valid():
                api_save_log(request=request, data_input=data, data_output="", api_status=0, err_analysis=-1, api_name="create_practice_point", status_code=STATUS_CODE_INVALID_INPUT, message=list(iqc_serializer_validate.errors.values())[0][0])
                return response_data(status=STATUS_CODE_INVALID_INPUT,
                                     message=list(iqc_serializer_validate.errors.values())[0][0])

            practice_point_cause = get_or_save_iqc_config_to_redis(IQC_CONFIG_PRACTICE_POINT_CAUSE)

            data_request = {
                "PracticePoint": data['practicePoint'].upper(),
                "MobiAccount": mobi_account,
                "DeviceIMEI": user_token['deviceId'],
                "LocationUpload": data['locationUpload']
                if 'locationUpload' in data and data['locationUpload'] else '0.0,0.0',
                # "LocationPracticePoint": data['locationPracticePoint'],
                # "Images": data['images'],
                "Images": []
            }

            for image in data['images']:
                imageCause = []
                errorsFix = []
                for error in image['fixError']:
                    if error > len(practice_point_cause['aChoice']):
                        api_save_log(request=request, data_input=data, api_status=0, err_analysis=-1, api_name="create_practice_point", status_code=STATUS_CODE_INVALID_INPUT, message="Sai thông tin lỗi sửa")
                        return response_data(data=None, message="Sai thông tin lỗi sửa",
                                             status=STATUS_CODE_INVALID_INPUT)
                    errorsFix.append(str(practice_point_cause['aChoice'][str(error)]))

                for cause in image['causeImage']:
                    if cause > len(practice_point_cause['aChoice']):
                        api_save_log(request=request, data_input=data, api_status=0, err_analysis=-1, api_name="create_practice_point", status_code=STATUS_CODE_INVALID_INPUT, message="Sai thông tin lỗi ảnh")
                        return response_data(data=None, message="Sai thông tin lỗi ảnh",
                                             status=STATUS_CODE_INVALID_INPUT)
                    imageCause.append(str(practice_point_cause['aChoice'][str(cause)]))
                data_request['Images'].append({
                    "link1": image['link1'],
                    # "_id": "5e70a893258b36000fb7d8a2",
                    # "causeError": [],
                    # "accuracy2": image['accuracy2'],
                    # "accuracy1": image['accuracy1'],
                    "accuracy1": "1",
                    "link2": image['link2'],
                    "fixError": errorsFix,
                    "causeImage": imageCause
                })

            app_env = "base_http_" + project_settings.APP_ENVIRONMENT
            response = call_api(
                host=IQC_API[app_env],
                func=IQC_API["create_practice_point"]["func"],
                method=IQC_API["create_practice_point"]["method"],
                data=data_request,
                # proxies=PROXIES
            )
            json_response = json.loads(response)
            response_result = json_response['ResponseResult']
            error_code = response_result['ErrorCode']
            message = response_result['Message']
            if error_code != 0:
                api_save_log(request=request, data_input=data, data_output="", api_status=0, err_analysis=0, api_name="create_practice_point", status_code=0, message=message)
                return response_data(message=message, status=0)
            api_save_log(request=request, data_input=data, data_output="", api_name="create_practice_point", message=message)
            return response_data(message=message, status=1)

        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.create_practice_point.__name__, ex))
            api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="create_practice_point", status_code=STATUS_CODE_FAILED, message=str(ex))
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)

    def update_practice_point(self, request):
        try:
            user_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
            if user_token is None:
                api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="update_practice_point", status_code=STATUS_CODE_ERROR_SYSTEM, message=MESSAGE_API_ERROR_SYSTEM)
                return response_data(data=None, status=STATUS_CODE_ERROR_SYSTEM, message=MESSAGE_API_ERROR_SYSTEM)

            emp_code = user_token["empCode"]
            mobi_account = get_accountMBN(emp_code)
            if empty(mobi_account):
                api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="update_practice_point", status_code=STATUS_CODE_FAILED, message="Account Mobinet không tồn tại!")
                return response_data(data=None, status=STATUS_CODE_FAILED, message="Account Mobinet không tồn tại!")

            practice_point_cause = get_or_save_iqc_config_to_redis(IQC_CONFIG_PRACTICE_POINT_CAUSE)

            data = request.data

            iqc_serializer_validate = IqcCreatePracticePointValidate(data=data)
            if not iqc_serializer_validate.is_valid():
                api_save_log(request=request, data_input=data, api_status=0, err_analysis=-1, api_name="update_practice_point", status_code=STATUS_CODE_INVALID_INPUT, message=list(iqc_serializer_validate.errors.values())[0][0])
                return response_data(status=STATUS_CODE_INVALID_INPUT,
                                     message=list(iqc_serializer_validate.errors.values())[0][0])
            data_request = {
                "PracticePoint": data['practicePoint'].upper(),
                "MobiAccount": mobi_account,
                "DeviceIMEI": user_token['deviceId'] if 'deviceId' in user_token else '',

                # "DeviceIMEI": '353384092884718',
                # "MobiAccount": "ISC02.VIETCN",

                "LocationUpload": data['locationUpload']
                if 'locationUpload' in data and data['locationUpload'] else "0.0,0.0",
                "Version": data['version'],

                # "Status": data['status'],
                # "CreatedBy": "ISC02.VIETCN",
                # "UpdatedBy": "ISC02.VIETCN",
                # "AccuracyDate": "2020-03-17T11:43:11.039Z",
                # "AccuracyBy": "PN-HCM",
                # "UpdatedDate": "2020-03-17T10:38:11.042Z",
                # "CreatedDate": "2020-03-17T10:38:11.042Z",
                "Images": []
            }

            for image in data['images']:
                imageCause = []
                errorsFix = []
                for error in image['fixError']:
                    if error > len(practice_point_cause['aChoice']):
                        api_save_log(request=request, data_input=data, api_status=0, err_analysis=-1, api_name="update_practice_point", status_code=STATUS_CODE_INVALID_INPUT, message="Sai thông tin lỗi sửa")
                        return response_data(data=None, message="Sai thông tin lỗi sửa",
                                             status=STATUS_CODE_INVALID_INPUT)
                    errorsFix.append(str(practice_point_cause['aChoice'][str(error)]))

                for cause in image['causeImage']:
                    if cause > len(practice_point_cause['aChoice']):
                        api_save_log(request=request, data_input=data, api_status=0, err_analysis=-1, api_name="update_practice_point", status_code=STATUS_CODE_INVALID_INPUT, message="Sai thông tin lỗi ảnh")
                        return response_data(data=None, message="Sai thông tin lỗi ảnh",
                                             status=STATUS_CODE_INVALID_INPUT)
                    imageCause.append(str(practice_point_cause['aChoice'][str(cause)]))
                data_request['Images'].append({
                    "link1": decode_link_image(image['link1']),
                    # "_id": "5e70a893258b36000fb7d8a2",
                    # "causeError": [],
                    # "accuracy2": image['accuracy2'],
                    # "accuracy1": image['accuracy1'],
                    "accuracy1": "1",
                    "link2": decode_link_image(image['link2']),
                    "fixError": errorsFix,
                    "causeImage": imageCause
                })

            app_env = "base_http_" + project_settings.APP_ENVIRONMENT
            response = call_api(
                host=IQC_API[app_env],
                func=IQC_API["update_practice_point"]["func"],
                method=IQC_API["update_practice_point"]["method"],
                data=data_request,
                # proxies=PROXIES
            )
            json_response = json.loads(response)

            response_result = json_response['ResponseResult']
            error_code = response_result['ErrorCode']
            message = response_result['Message']
            if error_code != 0:
                api_save_log(request=request, data_input=data, data_output="", api_status=0, err_analysis=0, api_name="update_practice_point", status_code=0, message=message)
                return response_data(message=message, status=0)
            api_save_log(request=request, data_input=data, data_output="", api_name="update_practice_point", message=message)
            return response_data(message=message, status=1)

        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.update_practice_point.__name__, ex))
            api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="update_practice_point", status_code=STATUS_CODE_FAILED, message=str(ex))
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)

    def get_practice_point_check_version(self, request):

        try:
            user_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
            if user_token is None:
                return response_data(data=None, status=STATUS_CODE_ERROR_SYSTEM, message=MESSAGE_API_ERROR_SYSTEM)

            emp_code = user_token["empCode"]
            mobi_account = get_accountMBN(emp_code)
            if empty(mobi_account):
                return response_data(data=None, status=STATUS_CODE_FAILED, message="Account Mobinet không tồn tại!")

            query_params = request.query_params

            params = {
                "Code": query_params['code']
            }

            app_env = "base_http_" + project_settings.APP_ENVIRONMENT
            response = call_api(
                host=IQC_API[app_env],
                func=IQC_API["get_practice_point_check_version"]["func"],
                method=IQC_API["get_practice_point_check_version"]["method"],
                params=params
                # proxies=PROXIES
            )
            json_response = json.loads(response)

            response_result = json_response['ResponseResult']

            message = response_result['Message']
            if response_result['ErrorCode'] != 0:
                return response_data(message=message, status=5)

            results = {
                'version': response_result['Results']['Version'],
                # '_id': response_result['Results']['_id'],
                # 'practicePoint': response_result['Results']['PracticePoint'],
                # 'createdBy': response_result['Results']['CreatedBy'],
                # 'createdDate': helper.format_date_time(response_result['Results']['CreatedDate'])
            }
            return response_data(message=message, data=results)

        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.get_practice_point_check_version.__name__,
                                                        ex))
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)

    def get_practice_point_search(self, request):
        try:
            query_params = request.query_params

            user_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
            if user_token is None:
                return response_data(data=None, status=STATUS_CODE_ERROR_SYSTEM, message=MESSAGE_API_ERROR_SYSTEM)

            emp_code = user_token["empCode"]
            mobi_account = get_accountMBN(emp_code)
            if empty(mobi_account):
                return response_data(data=None, status=STATUS_CODE_FAILED, message="Account Mobinet không tồn tại!")

            data = {
                "Code": query_params.get("code", ""),
                "MobiAccount": mobi_account
            }

            app_env = "base_http_" + project_settings.APP_ENVIRONMENT
            response = call_api(
                host=IQC_API[app_env],
                func=IQC_API["get_practice_point_search"]["func"],
                method=IQC_API["get_practice_point_search"]["method"],
                data=data,
                # proxies=PROXIES
            )
            json_response = json.loads(response)

            response_result = json_response['ResponseResult']
            return response_data(data=response_result)
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.get_practice_point_search.__name__, ex))
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)

    def load_iqc_upload_return_contract(self, request):
        try:
            data = request.data

            user_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
            if user_token is None:
                api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="load_iqc_upload_return_contract", status_code=STATUS_CODE_ERROR_SYSTEM, message=MESSAGE_API_ERROR_SYSTEM)
                return response_data(data=None, status=STATUS_CODE_ERROR_SYSTEM, message=MESSAGE_API_ERROR_SYSTEM)

            emp_code = user_token["empCode"]
            mobi_account = get_accountMBN(emp_code)
            if empty(mobi_account):
                api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="load_iqc_upload_return_contract", status_code=STATUS_CODE_FAILED, message="Account Mobinet không tồn tại!")
                return response_data(data=None, status=STATUS_CODE_FAILED, message="Account Mobinet không tồn tại!")

            per_page = data.get("perPage", MAX_PAGE_SIZE)
            page = data.get("page", 1)

            params = {
                "MobiAccount": mobi_account,
                "PerPage": per_page,
                "PageNum": page
            }

            app_env = "base_http_" + project_settings.APP_ENVIRONMENT
            if app_env in ["staging", "production"]:
                response = call_api(
                    host=IQC_API[app_env],
                    func=IQC_API["load_iqc_upload_return_contract"]["func"],
                    params=params,
                    method=IQC_API["load_iqc_upload_return_contract"]["method"],
                    proxies=PROXIES
                )
            else:
                response = call_api(
                    host=IQC_API[app_env],
                    func=IQC_API["load_iqc_upload_return_contract"]["func"],
                    params=params,
                    method=IQC_API["load_iqc_upload_return_contract"]["method"],
                )
            res_data = json.loads(response)
            if "ResponseResult" in res_data \
                    and res_data["ResponseResult"]["ErrorCode"] == IQC_STATUS_CODE_SUCCESS:
                results = res_data["ResponseResult"]["Results"]
                # Xu ly output tra
                list_data = []
                for doc in results["docs"]:
                    list_data.append({"name": doc.get("Contract", ""),
                                      "status": doc.get("Status", ""),
                                      "image": revert_link_image(request, doc.get("InsteadImg", ""))})

                data_return = {
                    "perPage": results["limit"],
                    "page": results["page"],
                    "totalPage": results["pages"],
                    "listData": list_data
                }
                api_save_log(request=request, data_input=data, data_output=data_return, api_name="load_iqc_upload_return_contract", message=MESSAGE_API_SUCCESS)
                return response_data(data=data_return, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)
            else:
                raise Exception("Call API Get danh sách hợp đồng trả về thất bại!!!")
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.load_iqc_upload_return_contract.__name__,
                                                        ex))
            api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="load_iqc_upload_return_contract", status_code=STATUS_CODE_FAILED, message=str(ex))
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)

    def load_iqc_detail_return_contract(self, request):
        try:
            data = request.data

            if "contractCode" not in data:
                api_save_log(request=request, data_input=data, api_status=0, err_analysis=-1, api_name="load_iqc_detail_return_contract", status_code=STATUS_CODE_INVALID_INPUT, message="Mã hợp đồng là bắt buộc!")
                return response_data(data=None, status=STATUS_CODE_INVALID_INPUT, message="Mã hợp đồng là bắt buộc!")

            contract_code = data.get("contractCode", None)
            if not contract_code:
                api_save_log(request=request, data_input=data, api_status=0, err_analysis=-1, api_name="load_iqc_detail_return_contract", status_code=STATUS_CODE_INVALID_INPUT, message="Mã hợp đồng không hợp lệ!")
                return response_data(data=None, status=STATUS_CODE_INVALID_INPUT, message="Mã hợp đồng không hợp lệ!")

            app_env = "base_http_" + project_settings.APP_ENVIRONMENT
            params = {
                "Contract": contract_code,
            }

            if app_env in ["staging", "production"]:
                response = call_api(
                    host=IQC_API[app_env],
                    func=IQC_API["load_iqc_detail_return_contract"]["func"],
                    params=params,
                    method=IQC_API["load_iqc_detail_return_contract"]["method"],
                    proxies=PROXIES
                )
            else:
                response = call_api(
                    host=IQC_API[app_env],
                    func=IQC_API["load_iqc_detail_return_contract"]["func"],
                    params=params,
                    method=IQC_API["load_iqc_detail_return_contract"]["method"],
                )

            res_data = json.loads(response)
            if "ResponseResult" in res_data:
                if res_data["ResponseResult"]["ErrorCode"] == IQC_STATUS_CODE_SUCCESS:
                    results = res_data["ResponseResult"]["Results"]

                    # Xu ly output tra
                    images = []
                    return_causes = []
                    for image_dict in results["Images"]:
                        images.append({"image": revert_link_image(request, image_dict.get("link", "")),
                                       "index": image_dict.get("index", "")})
                        if empty(return_causes):
                            note = image_dict["note"]
                            try:
                                note_list = json.loads(note.replace("'", '"'))
                                if isinstance(note_list, list):
                                    return_causes = note_list
                                    # cho nay update
                                    listChoice = get_or_save_iqc_config_to_redis("RETURN_CONTRACT_CAUSE")
                                    a = listChoice.get("listChoice", [])
                                    return_causes = [x for x in a if x["name"] in return_causes]
                            except:
                                pass

                    data_return = {
                        "nameContract": results["Contract"],
                        "statusiQC": results["Status"],
                        "timeUpload": helper.format_date_time(results["CreatedDate"]),
                        "returnCause": return_causes,
                        "images": images
                    }

                    if not empty(data_return['timeUpload']):
                        data_return['timeUpload'] = datetime.strptime(data_return['timeUpload'],
                                                                      "%d/%m/%Y %H:%M:%S").strftime("%H:%M:%S %d/%m/%Y")
                    api_save_log(request=request, data_input=data, data_output=data_return, api_name="load_iqc_detail_return_contract", message=MESSAGE_API_SUCCESS)
                    return response_data(data=data_return, message=MESSAGE_API_SUCCESS, status=STATUS_CODE_SUCCESS)
                elif res_data["ResponseResult"]["ErrorCode"] == IQC_STATUS_NOT_FOUND:
                    api_save_log(request=request, data_input=data, api_name="load_iqc_detail_return_contract", status_code=STATUS_CODE_NO_DATA, message=MESSAGE_API_NO_DATA)
                    return response_data(status=STATUS_CODE_NO_DATA, message=MESSAGE_API_NO_DATA, data=None)
                else:
                    raise Exception("Call API Get chi tiết hợp đồng trả về thất bại!!!")
            else:
                raise Exception("Call API Get chi tiết hợp đồng trả về thất bại!!!")
        except Exception as ex:
            print(
                "{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.load_iqc_detail_return_contract.__name__,
                                                      ex))
            api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="load_iqc_detail_return_contract", status_code=STATUS_CODE_FAILED, message=str(ex))
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)

    def create_or_update_return_contract(self, request):
        try:
            data = request.data.copy()
            jsonParams = data.get("actionType", None)
            actionType = None
            try:
                if jsonParams == "CREATE":
                    actionType = 0
                elif jsonParams == "UPDATE":
                    actionType = 1
            except:
                pass
            user_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
            if user_token is None:
                api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="create_or_update_return_contract", status_code=STATUS_CODE_ERROR_SYSTEM, message=MESSAGE_API_ERROR_SYSTEM, jsonParamsRequired=jsonParams, action_type=actionType)
                return response_data(data=None, status=STATUS_CODE_ERROR_SYSTEM, message=MESSAGE_API_ERROR_SYSTEM)

            emp_code = user_token["empCode"]
            mobi_account = get_accountMBN(emp_code)
            if empty(mobi_account):
                api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="create_or_update_return_contract", status_code=STATUS_CODE_NO_DATA, message="Account Mobinet không tồn tại!", jsonParamsRequired=jsonParams, action_type=actionType)
                return response_data(data=None, status=STATUS_CODE_NO_DATA, message="Account Mobinet không tồn tại!")

            iqc_serializer_validate = IqcCreateUpdateReturnContractValidate(data=data)
            if not iqc_serializer_validate.is_valid():
                api_save_log(request=request, data_input=data, api_status=0, err_analysis=-1, api_name="create_or_update_return_contract", status_code=STATUS_CODE_INVALID_INPUT, message=list(iqc_serializer_validate.errors.values())[0][0], jsonParamsRequired=jsonParams, action_type=actionType)
                return response_data(status=STATUS_CODE_INVALID_INPUT,
                                     message=list(iqc_serializer_validate.errors.values())[0][0])

            return_cause = get_or_save_iqc_config_to_redis(IQC_CONFIG_RETURN_CONTRACT_CAUSE)

            action_type = data["actionType"]
            device_id = user_token.get("deviceId", "")
            name_contract = data["nameContract"]
            return_causes = []
            for cause in data['returnCause']:
                if cause > len(return_cause['aChoice']) or cause == 0:
                    api_save_log(request=request, data_input=data, api_status=0, err_analysis=-1, api_name="create_or_update_return_contract", status_code=STATUS_CODE_INVALID_INPUT, message="Sai thông tin lỗi sửa", jsonParamsRequired=jsonParams, action_type=actionType)
                    return response_data(data=None, message="Sai thông tin lỗi sửa", status=STATUS_CODE_INVALID_INPUT)
                if cause == -1:
                    if empty(data['otherCause']):
                        api_save_log(request=request, data_input=data, api_status=0, err_analysis=-1, api_name="create_or_update_return_contract", status_code=STATUS_CODE_INVALID_INPUT, message="Sai thông tin lỗi, nguyên nhân khác không được rỗng", jsonParamsRequired=jsonParams, action_type=actionType)
                        return response_data(data=None, message="Sai thông tin lỗi, nguyên nhân khác không được rỗng",
                                             status=STATUS_CODE_INVALID_INPUT)
                    return_causes.append(data['otherCause'])
                else:
                    return_causes.append(str(return_cause['aChoice'][str(cause)]))

            images = data["images"]
            images_body = []
            for image in images:
                images_body.append({
                    "link": image["image"] if action_type == "CREATE" else decode_link_image(image["image"]),
                    "index": image["index"],
                    "note": str(return_causes)
                })

            data_body = {
                "MobiAccount": mobi_account,
                "DeviceIMEI": device_id,
                "Contract": name_contract,
                "Images": images_body
            }

            app_env = "base_http_" + project_settings.APP_ENVIRONMENT
            host = IQC_API[app_env]
            if action_type == "CREATE":
                func = IQC_API["create_return_contract"]["func"]
                method = IQC_API["create_return_contract"]["method"]
            else:
                func = IQC_API["update_return_contract"]["func"]
                method = IQC_API["update_return_contract"]["method"]

            if project_settings.APP_ENVIRONMENT in ["staging", "production"]:
                response = call_api(host=host, func=func, method=method, data=data_body, proxies=PROXIES)
            else:
                response = call_api(host=host, func=func, method=method, data=data_body)

            res_data = json.loads(response)
            if "ResponseResult" in res_data:
                if res_data["ResponseResult"]["ErrorCode"] == IQC_STATUS_CODE_SUCCESS:
                    results = res_data["ResponseResult"]["Results"]
                    name_contract = results["Contract"]

                    return_data = {"nameContract": name_contract}

                    if action_type == "CREATE":
                        api_save_log(request=request, data_input=data, data_output=return_data, api_name="create_or_update_return_contract", message="Upload ảnh thành công", jsonParamsRequired=jsonParams, action_type=actionType)
                        return response_data(data=return_data, message="Upload ảnh thành công")
                    else:
                        api_save_log(request=request, data_input=data, data_output=return_data, api_name="create_or_update_return_contract", message="Cập nhật ảnh thành công", jsonParamsRequired=jsonParams, action_type=actionType)
                        return response_data(data=return_data, message="Cập nhật ảnh thành công")

            if action_type == "CREATE":
                api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="create_or_update_return_contract", status_code=STATUS_CODE_FAILED, message="Upload ảnh không thành công", jsonParamsRequired=jsonParams, action_type=actionType)
                return response_data(data=None, status=STATUS_CODE_FAILED, message="Upload ảnh không thành công")
            else:
                api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="create_or_update_return_contract", status_code=STATUS_CODE_FAILED, message="Cập nhật ảnh không thành công", jsonParamsRequired=jsonParams, action_type=actionType)
                return response_data(data=None, status=STATUS_CODE_FAILED, message="Cập nhật ảnh không thành công")
        except Exception as ex:
            print(f"{datetime.now()} >> create_or_update_return_contract >> {ex}")
            api_save_log(request=request, data_input=data, api_status=0, err_analysis=0, api_name="create_or_update_return_contract", status_code=STATUS_CODE_ERROR_SYSTEM, message=str(ex), jsonParamsRequired=jsonParams, action_type=actionType)
            return response_data(data=None, status=STATUS_CODE_ERROR_SYSTEM, message=MESSAGE_API_ERROR_SYSTEM)

    def get_list_house_model(self, request):
        try:
            listHouseModel = get_or_save_iqc_config_to_redis(IQC_CONFIG_HOUSE_MODELS)
            if listHouseModel is None:
                raise Exception("Lỗi khi lấy danh sách mô hình nhà trong redis!")
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.get_list_house_model.__name__, ex))
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)
        return response_data(data=listHouseModel['listChoice'])

    def get_list_transaction_type(self, request):
        try:
            listTransactionType = get_or_save_iqc_config_to_redis(IQC_CONFIG_TRANSACTION_TYPES)
            if listTransactionType is None:
                raise Exception("Lỗi khi lấy danh sách loại dịch vụ triển khai trong redis!")
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.get_list_transaction_type.__name__, ex))
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)
        return response_data(data=listTransactionType['listChoice'])

    def get_list_return_contract_cause(self, request):
        try:
            list_return_contract_type = get_or_save_iqc_config_to_redis(IQC_CONFIG_RETURN_CONTRACT_CAUSE)
            if list_return_contract_type is None:
                raise Exception("Lỗi khi lấy danh sách nguyên nhân hợp đồng trả về trong redis!")
        except Exception as ex:
            print(
                "{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.get_list_return_contract_cause.__name__, ex))
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)
        else:
            return response_data(data=list_return_contract_type['listChoice'])

    def upload_image(self, request):
        try:
            data = request.data
            files = request.FILES
            try:
                print(f"[{datetime.now()}][update_image_new] >> data: {data}")
                print(f"[{datetime.now()}][update_image_new] >> files: {files}")
            except Exception as ex:
                print(f"[{datetime.now()}][update_image_new]: {ex}")

            # lay thong tin account
            user_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
            if user_token is None:
                return response_data(data=None, status=STATUS_CODE_ERROR_SYSTEM, message=MESSAGE_API_ERROR_SYSTEM)

            emp_code = user_token["empCode"]
            mobi_account = get_accountMBN(emp_code)
            if empty(mobi_account):
                return response_data(data=None, status=STATUS_CODE_FAILED, message="Account Mobinet không tồn tại!")

            # kiem tra va xy ly du lieu
            check_data_result = iqc_upload_image_validate_func(data, files)
            if not check_data_result["result"]:
                return response_data(status=STATUS_CODE_INVALID_INPUT,
                                     message=check_data_result["message"],
                                     data=None)
            validated_data_list_images = check_data_result["data"]

            # xy ly va upload anh
            data_result = []
            for image_data in validated_data_list_images:
                link = upload_and_get_link_one_image(mobi_account, image_data)
                data_result.append(link)
        except RequestDataTooBig:
            return response_data(data=None, message="Dung lượng tải quá lớn")
        return response_data(data=data_result)

    def upload_image_new(self, request):
        try:
            data = request.data
            files = request.FILES
            try:
                print(f"[{datetime.now()}][update_image_new] >> data: {data}")
                print(f"[{datetime.now()}][update_image_new] >> files: {files}")
            except Exception as ex:
                print(f"[{datetime.now()}][update_image_new]: {ex}")

            # lay thong tin account
            user_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
            if user_token is None:
                return response_data(data=None, status=STATUS_CODE_ERROR_SYSTEM, message=MESSAGE_API_ERROR_SYSTEM)

            emp_code = user_token["empCode"]
            mobi_account = get_accountMBN(emp_code)
            if empty(mobi_account):
                return response_data(data=None, status=STATUS_CODE_FAILED, message="Account Mobinet không tồn tại!")

            # kiem tra va xy ly du lieu
            check_data_result = iqc_upload_image_validate_func(data, files)
            if not check_data_result["result"]:
                return response_data(status=STATUS_CODE_INVALID_INPUT,
                                     message=check_data_result["message"],
                                     data=None)
            validated_data_list_images = check_data_result["data"]

            # xy ly va upload anh
            futures = []
            data_result = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                for image_data in validated_data_list_images:
                    future = executor.submit(upload_and_get_link_one_image, mobi_account, image_data)
                    futures.append(future)
            for future in futures:
                data_result.append(future.result())
                future.done()
        except RequestDataTooBig:
            return response_data(data=None, message="Dung lượng tải quá lớn")
        return response_data(data=data_result)

    def update_mock_all_account_MBN(self, request):
        try:
            result = None
            getData = request.data
            if request.method == 'POST':
                result = update_mock_account_mbn(getData, config_key='IQC_EMPLOYEES_FAKE_INFO')
            elif request.method == 'GET':
                result = get_mock_account_mbn(getData)
            elif request.method == 'DELETE':
                result = delete_mock_account_mbn(getData, config_key='IQC_EMPLOYEES_FAKE_INFO')
        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.update_mock_all_account_MBN.__name__, ex))
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)
        return Response(result)

    def toolbar_search_iqc(self, request):
        try:
            getData = {
                'typeiQC': request.GET['typeiQC'],
                'contractCode': request.GET['contractCode']
            }
            data_token = authSessionHandler.getUserAuthSessionData(request.headers.get("Authorization"))
            getData['accountMBN'] = get_accountMBN(data_token['empCode'])
            result = []
            if empty(getData['typeiQC']) or \
                    getData['typeiQC'] not in ['trien_khai', 'ha_tang_ngoai_vi', 'hop_dong_tra_ve']:
                return response_data(data=None, status=STATUS_CODE_INVALID_INPUT, message="Loại tác vụ không hợp lệ")

            if getData['typeiQC'] == 'trien_khai':
                result = search_deployment_contract(request, getData)

            elif getData['typeiQC'] == 'ha_tang_ngoai_vi':
                result = search_practice_point(request, getData)

            elif getData['typeiQC'] == 'hop_dong_tra_ve':
                result = search_return_contract(request, getData)

        except Exception as ex:
            print("{} >> {} >> Error/Loi: >> {}".format(datetime.now(), self.toolbar_search_iqc.__name__, ex))
            return response_data(message=MESSAGE_API_FAILED, data=None, status=STATUS_CODE_FAILED)
        return response_data(data=result)
