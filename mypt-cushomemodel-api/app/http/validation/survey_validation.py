import json

from django.db import transaction
from rest_framework.serializers import *

from app.core.helpers import global_variable as gb
from app.core.helpers.my_datetime import getFormatDatetimeNow
from app.core.helpers.utils import return_choice_id_or_code
from app.http.models.house_model_survey import HouseModelSurvey
from app.http.models.house_model_survey_image import HouseModelSurveyImage
from app.http.validation.views_validation import InputCalculateModelValidate


class ModelSurveyInfoValidate(InputCalculateModelValidate):
    key_result_model_other = ['model', 'other']
    key_calculate_result = ['result', 'present']
    key_internet_package = ['id', 'name', 'quantity', 'downloadSpeed', 'uploadSpeed']
    key_routers = ['id', 'name', 'quantity', 'LANWifi', 'wifi', 'wifi24Pow', 'wifi5Pow']
    key_access_point = ['id', 'name', 'quantity', 'LANWifi', 'wifi', 'wifi24Pow', 'wifi5Pow']

    appId = CharField(required=True, allow_null=False, allow_blank=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='app ID'),
        'blank': gb.TXT_ERROR_MESSAGE_FORMAT['blank'].format(item='app ID'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='app ID')
    })
    accUsername = CharField(required=True, allow_null=False, allow_blank=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='username'),
        'blank': gb.TXT_ERROR_MESSAGE_FORMAT['blank'].format(item='username'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='username')
    })
    userId = CharField(required=True, allow_blank=False, allow_null=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='user ID'),
        'blank': gb.TXT_ERROR_MESSAGE_FORMAT['blank'].format(item='user ID'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='user ID')
    })
    regions = CharField(required=True, allow_blank=True, allow_null=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='vùng'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='vùng')
    })
    branchFullName = CharField(required=True, allow_blank=True, allow_null=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='chi nhánh'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='chi nhánh'),
    })
    totalAP = DictField(required=True, allow_null=False, allow_empty=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='tổng số Access Point'),
        'empty': gb.TXT_ERROR_MESSAGE_FORMAT['empty'].format(item='tổng số Access Point'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='tổng số Access Point'),
        'invalid': gb.TXT_ERROR_MESSAGE_FORMAT['invalid'].format(item='tổng số Access Point')
    })
    internetPackages = DictField(required=True, allow_null=False, allow_empty=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='thông tin các gói cước'),
        'empty': gb.TXT_ERROR_MESSAGE_FORMAT['empty'].format(item='thông tin các gói cước'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='thông tin các gói cước'),
        'invalid': gb.TXT_ERROR_MESSAGE_FORMAT['invalid'].format(item='thông tin các gói cước')
    })
    routers = DictField(required=True, allow_null=False, allow_empty=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='thông tin các router/modem'),
        'empty': gb.TXT_ERROR_MESSAGE_FORMAT['empty'].format(item='thông tin các router/modem'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='thông tin các router/modem'),
        'invalid': gb.TXT_ERROR_MESSAGE_FORMAT['invalid'].format(item='thông tin các router/modem')
    })
    accessPoints = DictField(required=True, allow_null=False, allow_empty=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='thông tin các access point'),
        'empty': gb.TXT_ERROR_MESSAGE_FORMAT['empty'].format(item='thông tin các access point'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='thông tin các access point'),
        'invalid': gb.TXT_ERROR_MESSAGE_FORMAT['invalid'].format(item='thông tin các access point')
    })
    conclusion = ListField(required=True, allow_empty=False, allow_null=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='kết luận khảo sát'),
        'empty': gb.TXT_ERROR_MESSAGE_FORMAT['empty'].format(item='kết luận khảo sát'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='kết luận khảo sát')
    })
    statusSurvey = CharField(required=True, allow_blank=False, allow_null=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='đánh giá khảo sát'),
        'blank': gb.TXT_ERROR_MESSAGE_FORMAT['blank'].format(item='đánh giá khảo sát'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='đánh giá khảo sát')
    })
    listModel = ListField(required=True, allow_null=False, allow_empty=True, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='thông tin các các mô hình'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='thông tin các các mô hình'),
        'invalid': gb.TXT_ERROR_MESSAGE_FORMAT['invalid'].format(item='thông tin các các mô hình')
    })

    def create(self, validated_data):
        try:
            with transaction.atomic():
                survey_object = HouseModelSurvey.objects.create(
                    contract_code=validated_data['contractCode'],
                    regions=validated_data['regions'],
                    branch_fullname=validated_data['branchFullName'],
                    sdk_user_id=validated_data['userId'],
                    app_id=validated_data['appId'],
                    sdk_acc_username=validated_data['accUsername'],
                    id_type=validated_data['idType'],
                    model_type=validated_data['modelType'],
                    customer_type=validated_data['customerType'],
                    house_length=validated_data['houseLength'],
                    house_width=validated_data['houseWidth'],
                    floors=validated_data['floors'],
                    rows_per_floor=validated_data['rowsPerFloor'],
                    rooms_per_row=validated_data['roomsPerRow'],
                    people_per_room=validated_data['peoplePerRoom'],
                    user_wifi=validated_data['userWifi'],
                    user_lan=validated_data['userLAN'],
                    user_camera=validated_data['userCamera'],
                    lux_package_check=validated_data['luxPackageCheck'],
                    upload_alot_check=validated_data['uploadAlotCheck'],
                    concurrent_usage_rate=validated_data['concurrentUsageRate'],
                    other_check=validated_data['otherCheck'],
                    other_width=validated_data['otherWidth'],
                    other_length=validated_data['otherLength'],
                    other_user_wifi=validated_data['otherUserWifi'],
                    internet_packages=json.dumps(validated_data['internetPackages']),
                    routers=json.dumps(validated_data['routers']),
                    access_points=json.dumps(validated_data['accessPoints']),
                    total_ap=json.dumps(validated_data['totalAP']),
                    conclusion=json.dumps(validated_data['conclusion']),
                    status_survey=validated_data['statusSurvey'],
                    is_current=1,
                    reason='Cập nhật lần đầu tiên',
                    created_at=getFormatDatetimeNow()
                )
                validated_data['id'] = survey_object.id

                # Thực hiện các hoạt động khác nếu cần

                # Nếu không có lỗi, commit các thay đổi vào database
        except Exception as e:
            # Nếu có lỗi, thực hiện rollback tự động
            print('Error/Loi: ' + str(e))
            raise e
        return validated_data

    def validate_totalAP(self, data):
        for _key in self.key_calculate_result:
            if _key not in data:
                raise ValidationError('Số lượng thiết bị AP sai định dạng ' + str(_key))
        for _key in self.key_result_model_other:
            if _key not in data[self.key_calculate_result[0]]:
                raise ValidationError('Kết quả thiết bị AP sai định dạng ' + str(_key))
        return data

    def validate_internetPackages(self, data):
        for _key in self.key_calculate_result:
            if _key not in data:
                raise ValidationError('Kết quả gói cước sai định dạng sai định dạng ' + str(_key))

            for i in data[_key]:
                if not isinstance(i, dict):
                    raise ValidationError('Các đối tượng trong danh sách gói cước không phải dạng dict')

                for _key_internet in self.key_internet_package:
                    i[_key_internet] = i.get(_key_internet, None)
                    if _key == 'result':
                        if _key_internet == 'id' and i[_key_internet] == 0:
                            raise ValidationError('Thiêu thông tin gói cước, xin vui lòng nhập đầy đủ '
                                                  'thông tin kết quả ' + _key_internet + '=' + str(i[_key_internet]))

                    if _key == 'present':
                        if _key_internet == 'id':
                            i['id'] = 0
                    if i[_key_internet] is None:
                        raise ValidationError('Thiêu thông tin gói cước, xin vui lòng nhập đầy đủ thông tin hiện trạng '
                                              + _key_internet + '=' + str(i[_key_internet]))

                if i['quantity'] <= 0:
                    raise ValidationError('Số lượng gói cước không phù hợp: ' + str(i['quantity']))
        return data

    def validate_routers(self, data):
        for _key in self.key_calculate_result:
            if _key not in data:
                raise ValidationError('Kết quả router sai định dạng sai định dạng ' + str(_key))

            for i in data[_key]:
                if not isinstance(i, dict):
                    raise ValidationError('Các đối tượng trong danh sách router không phải dạng dict')

                for _key_router in self.key_routers:
                    i[_key_router] = i.get(_key_router, None)

                    if _key == 'result':
                        if _key_router == 'id':
                            if i[_key_router] == 0:
                                raise ValidationError('Thiêu thông tin router, xin vui lòng nhập đầy đủ '
                                                      'thông tin kết quả ' + _key_router + '=' + str(i[_key_router]))
                        if i[_key_router] is None:
                            raise ValidationError('Thiêu thông tin router, xin vui lòng nhập đầy đủ thông tin kết quả '
                                                  + _key_router + '=' + str(i[_key_router]))

                    if _key == 'present':
                        if _key_router == 'id':
                            i['id'] = 0
                        if i[_key_router] is None and _key_router not in ['wifi24Pow', 'wifi5Pow']:
                            raise ValidationError('Thiêu thông tin router, xin vui lòng nhập đầy đủ '
                                                  'thông tin hiện trạng ' + _key_router + '=' + str(i[_key_router]))

                if i['quantity'] <= 0:
                    raise ValidationError('Số lượng router không phù hợp: ' + str(i['quantity']))
        return data

    def validate_accessPoints(self, data):
        for _key in self.key_calculate_result:
            if _key not in data:
                raise ValidationError('Kết quả thiết bị AP sai định dạng ' + str(_key))
        for _key in self.key_result_model_other:
            if _key not in data[self.key_calculate_result[0]]:
                raise ValidationError('Kết quả thiết bị AP sai định dạng ' + str(_key))

        for _key, _value in data.items():
            if _key == 'result':
                for _key_result in self.key_result_model_other:
                    for i in _value[_key_result]:
                        if not isinstance(i, dict):
                            raise ValidationError('Các đối tượng trong danh sách AP không phải dạng dict')
                        for _key_access_point in self.key_access_point:
                            i[_key_access_point] = i.get(_key_access_point, None)
                            if _key_access_point == 'id' and i[_key_access_point] == 0:
                                raise ValidationError('Thiêu thông tin AP, xin vui lòng nhập đầy đủ '
                                                      'thông tin kết quả ' + _key_access_point + '=' +
                                                      str(i[_key_access_point]))
                            if i[_key_access_point] is None:
                                raise ValidationError('Thiêu thông tin AP, xin vui lòng nhập đầy đủ '
                                                      'thông tin kết quả ' + _key_access_point + '=' +
                                                      str(i[_key_access_point]))
                        if i['quantity'] <= 0:
                            raise ValidationError('Số lượng AP không phù hợp: ' + str(i['quantity']))
            else:
                for i in _value:
                    if not isinstance(i, dict):
                        raise ValidationError('Các đối tượng trong danh sách AP không phải dạng dict')
                    for _key_access_point in self.key_access_point:
                        i[_key_access_point] = i.get(_key_access_point, None)
                        if _key_access_point == 'id':
                            i['id'] = 0
                        if i[_key_access_point] is None and _key_access_point not in ['wifi24Pow', 'wifi5Pow']:
                            raise ValidationError('Thiêu thông tin AP, xin vui lòng nhập đầy đủ '
                                                  'thông tin hiện trạng ' + _key_access_point + '=' +
                                                  str(i[_key_access_point]))
                    if i['quantity'] <= 0:
                        raise ValidationError('Số lượng AP không phù hợp: ' + str(i['quantity']))

        return data

    def validate_conclusion(self, data):
        return data

    def validate_statusSurvey(self, data):
        return return_choice_id_or_code(data, HouseModelSurvey.STATUS_SURVEY_CHOICES)


class UpdateModelSurveyValidate(ModelSurveyInfoValidate):
    reason = CharField(required=True, allow_null=False, allow_blank=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='nguyên nhân'),
        'blank': gb.TXT_ERROR_MESSAGE_FORMAT['blank'].format(item='nguyên nhân'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='nguyên nhân')
    })
    listModel = ListField(required=False, allow_null=True, allow_empty=True)

    def create(self, validated_data):
        survey_objects = HouseModelSurvey.objects.filter(contract_code=validated_data['contractCode']) \
            .order_by('id')
        survey_object_current_id = list(survey_objects)[-1].id
        survey_objects.update(is_current=0)
        survey_object = HouseModelSurvey.objects.create(
            contract_code=validated_data['contractCode'],
            regions=validated_data['regions'],
            branch_fullname=validated_data['branchFullName'],
            sdk_user_id=validated_data['userId'],
            app_id=validated_data['appId'],
            sdk_acc_username=validated_data['accUsername'],
            id_type=validated_data['idType'],
            model_type=validated_data['modelType'],
            customer_type=validated_data['customerType'],
            house_length=validated_data['houseLength'],
            house_width=validated_data['houseWidth'],
            floors=validated_data['floors'],
            rows_per_floor=validated_data['rowsPerFloor'],
            rooms_per_row=validated_data['roomsPerRow'],
            people_per_room=validated_data['peoplePerRoom'],
            user_wifi=validated_data['userWifi'],
            user_lan=validated_data['userLAN'],
            user_camera=validated_data['userCamera'],
            lux_package_check=validated_data['luxPackageCheck'],
            upload_alot_check=validated_data['uploadAlotCheck'],
            concurrent_usage_rate=validated_data['concurrentUsageRate'],
            other_check=validated_data['otherCheck'],
            other_width=validated_data['otherWidth'],
            other_length=validated_data['otherLength'],
            other_user_wifi=validated_data['otherUserWifi'],
            internet_packages=json.dumps(validated_data['internetPackages']),
            routers=json.dumps(validated_data['routers']),
            access_points=json.dumps(validated_data['accessPoints']),
            total_ap=json.dumps(validated_data['totalAP']),
            conclusion=json.dumps(validated_data['conclusion']),
            status_survey=validated_data['statusSurvey'],
            is_current=1,
            reason=validated_data['reason'],
            created_at=getFormatDatetimeNow()
        )
        validated_data['id'] = survey_object.id

        queryset = HouseModelSurveyImage.objects.filter(model_survey_id=survey_object_current_id)
        if queryset.exists():
            new_objects = []
            for obj in queryset:
                new_obj = HouseModelSurveyImage(
                    model_survey_id=survey_object.id,
                    house_floor=obj.house_floor,
                    house_size=obj.house_size,
                    tx_devices_info='[]',
                    sketches=obj.sketches,
                    sketches_type=obj.sketches_type,
                    status_updated=0,
                    sdk_user_id=validated_data['userId'],
                    app_id=validated_data['appId'],
                    sdk_acc_username=validated_data['accUsername'],
                    created_at=getFormatDatetimeNow()
                )
                new_objects.append(new_obj)
            HouseModelSurveyImage.objects.bulk_create(new_objects)
        return validated_data
