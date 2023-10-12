import base64
import json
import tempfile

import requests
from django.conf import settings as project_settings
from rest_framework import serializers
from rest_framework.serializers import *

from app.configs.service_api_config import SERVICE_CONFIG
from app.http.validation.simulate_wifi_image_validation import SimulateWifiImageValidate


class HouseModelValidate(Serializer):
    data = None

    # def __init__(self, *args, **kwargs):
    #     self.data = kwargs.pop('validate')
    #     super().__init__(*args, **kwargs)

    contractCode = CharField(required=True, allow_null=False, allow_blank=False, error_messages={
        'required': 'Mã hợp đồng là bắt buộc!',
        'null': 'Vui lòng chọn mã hợp đồng!'
    })
    listModel = ListField(required=True,
                          allow_null=False,
                          allow_empty=False,
                          error_messages={
                              'required': 'Thông tin dựng mô hình nhà là bắt buộc!',
                              'null': 'Thông tin dựng mô hình nhà không được là giá trị null',
                          })

    def validate_contractCode(self, value):
        return value

    # def validate_listData(self, data):
    #     contract_code = self.initial_data.get('contractCode')
    #     result = []
    #     for model in data:
    #         model['contractCode'] = contract_code
    #         serializer_validate = DetailModelValidate(data=model)
    #         if not serializer_validate.is_valid():
    #             raise ValidationError(list(serializer_validate.errors.values())[0][0])
    #         result.append(serializer_validate.validated_data)
    #     return result

    def validate_listData(self, data):
        return data


class DetailModelValidate(SimulateWifiImageValidate):
    data = None

    def __init__(self, *args, **kwargs):
        self.data = kwargs.pop('validate')
        super().__init__(*args, **kwargs)

    contractCode = CharField(required=True, allow_null=False, allow_blank=False, error_messages={
        'required': 'Mã hợp đồng là bắt buộc để lưu ảnh!',
        'null': 'Vui lòng chọn mã hợp đồng để lưu ảnh!'
    })
    txLocation = ListField(required=True,
                           allow_null=True,
                           allow_empty=True,
                           error_messages={
                               'required': 'Vị trị các thiết bị là bắt buộc!',
                               'null': 'Vị trị các thiết bị không được là giá trị null',
                               'empty': 'Vị trị các thiết bị không được rỗng!',
                           })
    txPower = ListField(required=True,
                        allow_null=True,
                        allow_empty=True,
                        error_messages={
                            'required': 'Vị trị các thiết bị là bắt buộc!',
                            'null': 'Vị trị các thiết bị không được là giá trị null',
                            'empty': 'Vị trị các thiết bị không được rỗng!',
                        })
    txName = ListField(required=True,
                       allow_null=True,
                       allow_empty=True,
                       error_messages={
                           'required': 'Tên các thiết bị là bắt buộc!',
                           'null': 'Tên các thiết bị không được là giá trị null',
                           'empty': 'Tên các thiết bị không được rỗng!',
                       })
    wallAttenuation = IntegerField(required=True, allow_null=False,
                                   error_messages={
                                       'required': 'Thông tin vật cản là bắt buộc!',
                                       'null': 'Vui lòng chọn thông tin vật cản!',
                                       'blank': 'Vui lòng chọn thông tin vật cản!',
                                   })
    wallAttenuationInfo = DictField(required=True, allow_null=False,
                                    error_messages={
                                        'required': 'Thông tin vật cản là bắt buộc!',
                                        'null': 'Vui lòng chọn thông tin vật cản!',
                                    })
    image = serializers.CharField(required=True, allow_null=False, allow_blank=False, error_messages={
        'required': 'Thông tin ảnh gốc là bắt buộc!',
        'null': 'Thông tin ảnh gốc Vui lòng chọn thông tin ảnh gốc!',
        'blank': 'Thông tin ảnh gốc không được rỗng!'
    })
    wifi24Image = serializers.CharField(required=True, allow_null=True, allow_blank=False, error_messages={
        'required': 'Thông tin ảnh mô phỏng wifi 2.4ghz là bắt buộc!',
        'null': 'Thông tin ảnh mô phỏng wifi 2.4ghz Vui lòng chọn thông tin ảnh mô phỏng wifi 2.4GHz!',
        'blank': 'Thông tin ảnh mô phỏng wifi 2.4ghz không được rỗng!'
    })
    wifi5Image = serializers.CharField(required=True, allow_null=True, allow_blank=False, error_messages={
        'required': 'Thông tin ảnh mô phỏng wifi 5ghz là bắt buộc!',
        'null': 'Thông tin ảnh mô phỏng wifi 5ghz Vui lòng chọn thông tin ảnh mô phỏng wifi 5GHz!',
        'blank': 'Thông tin ảnh mô phỏng wifi 5ghz không được rỗng!'
    })

    def validate_txName(self, value):
        txt_error_message = 'Thông tin tên thiết bị không đúng định dạng!'
        list_key_txName = ['id', 'name', 'type', 'modelType']
        for data in value:
            for key in list_key_txName:
                if key not in data:
                    raise ValidationError(txt_error_message)
            if data['type'] not in ['access_point', 'modem']:
                raise ValidationError(txt_error_message)
            if data['modelType'] not in ['model', 'other']:
                raise ValidationError(txt_error_message)
        return value

    def validate_image(self, value):
        try:
            base_env = project_settings.APP_ENVIRONMENT
            url = SERVICE_CONFIG['HO_MEDIA'][base_env] + SERVICE_CONFIG['HO_MEDIA']['upload_file_private']['func']

            image_decode = base64.b64decode(value)
            # print(image_decode)

            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as image_file:
                image_file.write(image_decode)

            payload = {
                'folder': '/cushomemodel/contract_original_images/' + str(self.initial_data.get('contractCode')) + '/',
                'userEmail': 'longthk',
                'numberFile': '1'
            }

            file_image = {
                'file_1': ('image_original.jpg', open(image_file.name, 'rb'), 'image/jpeg')
            }

            link_image = requests.post(url, data=payload, files=file_image)
            # print(link_image.text)

            link_image = json.loads(link_image.text.replace('"', '\"'))
            result = link_image['data']['linkFile'][0]
        except Exception as ex:
            raise ValidationError('Thông tin ảnh gốc có vấn đề với lỗi: ' + str(ex))
        return result

    def validate_wifi24Image(self, value):
        if value is None:
            return value
        try:
            base_env = project_settings.APP_ENVIRONMENT
            url = SERVICE_CONFIG['HO_MEDIA'][base_env] + SERVICE_CONFIG['HO_MEDIA']['upload_file_private']['func']

            image_decode = base64.b64decode(value)

            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as image_file:
                image_file.write(image_decode)

            payload = {'folder': '/cushomemodel/contract_heatmap_images/' +
                                 str(self.initial_data.get('contractCode')) + '/',
                       'userEmail': 'longthk',
                       'numberFile': '1'}

            file_image = {
                'file_1': ('image_wifi24.jpg', open(image_file.name, 'rb'), 'image/jpeg')
            }

            link_image = requests.post(url, data=payload, files=file_image)

            link_image = json.loads(link_image.text.replace('"', '\"'))
            result = link_image['data']['linkFile'][0]
        except Exception as ex:
            raise ValidationError('Thông tin ảnh mô phỏng wifi 2.4ghz có vấn đề với lỗi: ' + str(ex))
        return result

    def validate_wifi5Image(self, value):
        if value is None:
            return value
        try:
            base_env = project_settings.APP_ENVIRONMENT
            url = SERVICE_CONFIG['HO_MEDIA'][base_env] + SERVICE_CONFIG['HO_MEDIA']['upload_file_private']['func']

            image_decode = base64.b64decode(value)

            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as image_file:
                image_file.write(image_decode)

            payload = {'folder': '/cushomemodel/contract_heatmap_images/'
                                 + str(self.initial_data.get('contractCode')) + '/',
                       'userEmail': 'longthk',
                       'numberFile': '1'}

            file_image = {
                'file_1': ('image_wifi5.jpg', open(image_file.name, 'rb'), 'image/jpeg')
            }

            link_image = requests.post(url, data=payload, files=file_image)

            link_image = json.loads(link_image.text.replace('"', '\"'))
            result = link_image['data']['linkFile'][0]
        except Exception as ex:
            raise ValidationError('Thông tin ảnh mô phỏng wifi 2.4ghz có vấn đề với lỗi: ' + str(ex))
        return result


class UpdateHouseModelValidate(HouseModelValidate):
    reason = CharField(required=True, allow_null=False, allow_blank=False,
                       error_messages={
                           'required': 'Nguyên nhân cập nhật là bắt buộc!',
                           'null': 'Nguyên nhân cập nhật không được là giá trị null!',
                           'blank': 'Nguyên nhân cập nhật không là giá trị rỗng!',
                       })
