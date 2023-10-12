from rest_framework.serializers import *

from app.core.helpers import global_variable as gb
from app.http.models.house_model_type import HouseModelType


class InputCalculateModelValidate(Serializer):
    checkbox_model = ['Khách sạn có sảnh chờ/phòng hội nghị', 'Quán cafe có phòng lạnh riêng']
    model_type = None
    key_internet_package = ['id', 'name', 'quantity', 'downloadSpeed', 'uploadSpeed']
    key_routers = ['id', 'name', 'quantity', 'LANWifi', 'wifi', 'wifi24Pow', 'wifi5Pow']
    key_access_point = ['id', 'name', 'quantity', 'LANWifi', 'wifi', 'wifi24Pow', 'wifi5Pow']

    def __init__(self, *args, **kwargs):
        # Lấy giá trị idType từ tham số truyền vào
        self.model_type = HouseModelType.objects.filter(model_type=1, is_active=1)
        super().__init__(*args, **kwargs)

    contractCode = CharField(required=True, allow_null=False, allow_blank=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='mã hợp đồng'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='mã hợp đồng'),
    })
    idType = IntegerField(required=True, allow_null=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='ID mô hình'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='ID mô hình'),
    })
    modelType = CharField(required=True, allow_null=False, allow_blank=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='loại mô hình'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='loại mô hình'),
        'blank': gb.TXT_ERROR_MESSAGE_FORMAT['blank'].format(item='loại mô hình'),
    })
    customerType = CharField(required=True, allow_null=False, allow_blank=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='loại khách hàng'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='loại khách hàng'),
        'blank': gb.TXT_ERROR_MESSAGE_FORMAT['blank'].format(item='loại khách hàng'),
    })
    regions = CharField(required=True, allow_null=False, allow_blank=True, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='vùng'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='vùng'),
    })
    branchFullName = CharField(required=True, allow_null=False, allow_blank=True, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='chi nhánh'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='chi nhánh'),
    })
    houseWidth = FloatField(required=True, allow_null=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='chiều rộng'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='chiều rộng'),
        'invalid': gb.TXT_ERROR_MESSAGE_FORMAT['invalid'].format(item='chiều rộng'),
    })
    houseLength = FloatField(required=True, allow_null=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='chiều dài'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='chiều dài'),
        'invalid': gb.TXT_ERROR_MESSAGE_FORMAT['invalid'].format(item='chiều dài'),
    })
    floors = IntegerField(required=True, allow_null=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='số tầng'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='số tầng'),
    })
    rowsPerFloor = IntegerField(required=True, allow_null=True, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='số dãy mỗi tầng'),
    })
    roomsPerRow = IntegerField(required=True, allow_null=True, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='số phòng mỗi dãy'),
    })
    peoplePerRoom = IntegerField(required=True, allow_null=True, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='số người mỗi phòng'),
    })
    otherCheck = IntegerField(required=True, allow_null=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='phòng họp/sảnh chờ'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='phòng họp/sảnh chờ'),
    })
    otherWidth = FloatField(required=True, allow_null=True, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='chiều rộng phòng họp/sảnh chờ'),
    })
    otherLength = FloatField(required=True, allow_null=True, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='chiều dài phòng họp/sảnh chờ'),
    })
    otherUserWifi = IntegerField(required=True, allow_null=True, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='số người dùng wifi phòng họp/sảnh chờ'),
    })
    userWifi = IntegerField(required=True, allow_null=False, error_messages={
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='số người dùng wifi'),
    })
    userLAN = IntegerField(required=True, allow_null=False, error_messages={
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='số người dùng LAN'),
    })
    userCamera = IntegerField(required=True, allow_null=False, error_messages={
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='số người dùng camera'),
    })
    luxPackageCheck = IntegerField(required=True, allow_null=False, error_messages={
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='thông tin gói LUX'),
    })
    uploadAlotCheck = IntegerField(required=True, allow_null=False, error_messages={
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='giá trị upload nhiều'),
    })
    concurrentUsageRate = IntegerField(required=True, allow_null=False, error_messages={
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='tỷ lệ sử dụng đồng thời'),
    })
    totalAP = IntegerField(required=True, allow_null=False, error_messages={
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='tống số AP'),
    })
    internetPackages = ListField(required=True, allow_empty=True, allow_null=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='danh sách gói cước'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='danh sách gói cước'),
    })
    routers = ListField(required=True, allow_empty=True, allow_null=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='danh sách router'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='danh sách router'),
    })
    accessPoints = ListField(required=True, allow_empty=True, allow_null=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='danh sách access point'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='danh sách access point'),
    })

    def validate_contractCode(self, value):
        return value

    def validate_idType(self, id_type):
        """
        Trong database mypt_chm_house_model_type:
        id - 1 - Nhà trệt, chung cư
        id - 3 - Nhà cao tầng
        id - 4 - Khu nhà trọ, khách sạn, ktx, karaoke
        id - 5 - Cty, nhà xưởng, quán ăn, cafe, nhà hàng (phòng/nhà ống)
        id - 6 - Cty, cafe/nhà hàng, nhà xưởng có số lượng vật cản không quá nhiều
        id - 7 - Cafe/nhà hàng sân vườn, nhà xưởng,... ít vật cản (cửa gỗ/nhà kính)
        id - 8 - Cafe/nhà hàng sân vườn, nhà xưởng không/rất ít vật cản
        """
        if id_type not in [x.id for x in self.model_type] and id_type == 2:
            raise ValidationError('Id loại mô hình nhà không hợp lệ!')
        return id_type

    def validate_modelType(self, model_type):
        data = model_type
        model_name = {x.id: x.name for x in self.model_type}
        if self.initial_data['idType'] not in model_name.keys():
            raise ValidationError('Id loại mô hình nhà không hợp lệ!')
        data = model_name[self.initial_data['idType']]
        return data.capitalize()

    def validate_customerType(self, customerType):
        if customerType.lower() not in ['cá nhân', 'doanh nghiệp']:
            raise ValidationError('Loại khách hàng không hợp lệ!')
        return customerType.capitalize()

    def validate_regions(self, regions):
        return regions.strip()

    def validate_branchFullName(self, branchFullName):
        return branchFullName.strip()

    def validate_houseWidth(self, houseWidth):
        if houseWidth <= 0:
            raise ValidationError('Thông tin chiều rộng mô hình nhà không có trường hợp 0m!')
        return houseWidth

    def validate_houseLength(self, houseLength):
        if houseLength <= 0:
            raise ValidationError('Thông tin chiều dài mô hình nhà không có trường hợp 0m!')
        return houseLength

    def validate_floors(self, total_floors):
        """
        Trong database mypt_chm_house_model_type:
        id - 3 - Nhà cao tầng
        id - 4 - Khu nhà trọ, khách sạn, ktx, karaoke
        id - 7 - Cafe/nhà hàng sân vườn, nhà xưởng,... ít vật cản (cửa gỗ/nhà kính)
        id - 8 - Cafe/nhà hàng sân vườn, nhà xưởng không/rất ít vật cản
        """
        # if self.initial_data['idType'] != 1:
        #     if total_floors == 0:
        #         raise ValidationError(
        #             'Thiếu hoặc sai thông tin số tầng đối với mô hình ' + str(self.initial_data['modelType'].lower()
        #                                                                       + "!"))

        if total_floors < 0:
            raise ValidationError(
                'Thông tin số tầng mô hình nhà không có trường hợp âm!')

        if self.initial_data['idType'] == 1:
            total_floors = 0
            # if total_floors != 0:
            #     raise ValidationError(
            #         'Số tầng phải bằng 0 đối với mô hình ' + str(self.initial_data['modelType'].lower()
            #                                                      + "!"))
        return total_floors

    def validate_rowsPerFloor(self, total_rows):
        """
        Trong database mypt_chm_house_model_type:
        id - 4 - Khu nhà trọ, khách sạn, ktx, karaoke
        """
        if self.initial_data['idType'] == 4:
            if total_rows is None:
                raise ValidationError(
                    'Số dãy không được là giá trị null đối với mô hình ' + str(self.initial_data['modelType'].lower()
                                                                               + "!"))
            if total_rows <= 0:
                raise ValidationError(
                    'Số dãy không được là giá trị 0 đối với mô hình ' + str(self.initial_data['modelType'].lower()
                                                                            + "!"))
        if self.initial_data['idType'] != 4:
            total_rows = None
            # if total_rows is not None:
            #     raise ValidationError(
            #         'Số dãy phải là giá trị null đối với mô hình ' + str(self.initial_data['modelType'].lower()
            #                                                              + "!"))
        return total_rows

    def validate_roomsPerRow(self, total_rooms):
        """
        Trong database mypt_chm_house_model_type:
        id - 4 - Khu nhà trọ, khách sạn, ktx, karaoke
        """
        if self.initial_data['idType'] == 4:
            if total_rooms is None:
                raise ValidationError(
                    'Số phòng mỗi dãy không được là giá trị null đối với mô hình ' + str(self.initial_data['modelType'].lower()
                                                                                         + "!"))
            if total_rooms <= 0:
                raise ValidationError(
                    'Số phòng mỗi dãy không được là giá trị 0 đối với mô hình ' + str(self.initial_data['modelType'].lower()
                                                                                      + "!"))
        if self.initial_data['idType'] != 4:
            total_rooms = None
            # if total_rooms is not None:
            #     raise ValidationError(
            #         'Số phòng mỗi dãy phải là giá trị null đối với mô hình ' + str(self.initial_data['modelType'].lower()
            #                                                                        + "!"))
        return total_rooms

    def validate_peoplePerRoom(self, total_people):
        """
        Trong database mypt_chm_house_model_type:
        id - 4 - Khu nhà trọ, khách sạn, ktx, karaoke
        """
        if self.initial_data['idType'] == 4:
            if total_people is None:
                raise ValidationError(
                    'Số người mỗi phòng không được là giá trị null đối với mô hình ' + str(
                        self.initial_data['modelType'].lower()
                        + "!"))
            if total_people <= 0:
                raise ValidationError(
                    'Số người mỗi phòng không được là giá trị 0 đối với mô hình ' + str(self.initial_data['modelType'].lower()
                                                                                        + "!"))
        if self.initial_data['idType'] != 4:
            total_people = None
            # if total_people is not None:
            #     raise ValidationError(
            #         'Số người mỗi phòng phải là giá trị null đối với mô hình ' + str(self.initial_data['modelType'].lower()
            #                                                                          + "!"))
        return total_people

    def validate_otherCheck(self, other_check):
        """
        True - 1
        False - 0
        """
        if other_check not in [0, 1]:
            raise ValidationError(self.checkbox_model[0] + ' sai hoặc thiếu thông tin')
        if self.initial_data['idType'] in [1, 3]:
            other_check = 0
        # if other_check == 1 and self.initial_data['idType'] in [1, 3]:
        #     raise ValidationError('Mô hình ' + self.initial_data['modelType'].lower() + ' không có phòng họp/sảnh chờ/phòng '
        #                                                                         'lạnh riêng')
        # if other_check == 1:
        #     if self.initial_data['idType'] == 3:
        #         raise ValidationError(self.checkbox_model[0] + ' sai hoặc thiếu thông tin')
        #     if self.initial_data['idType'] == 1:
        #         raise ValidationError(self.checkbox_model[1] + ' sai hoặc thiếu thông tin')
        return other_check

    def validate_otherWidth(self, other_width):
        if self.initial_data['idType'] not in [1, 3]:
            if self.initial_data['otherCheck'] == 1:
                if other_width <= 0:
                    if self.initial_data['idType'] in [4, 5, 6]:
                        raise ValidationError(
                            'Chiều rộng ' + self.checkbox_model[0].lower() + ' không có trường hợp 0m')
                    if self.initial_data['idType'] in [7, 8]:
                        raise ValidationError(
                            'Chiều rộng ' + self.checkbox_model[1].lower() + ' không có trường hợp 0m')
                if other_width is None:
                    if self.initial_data['idType'] in [4, 5, 6]:
                        raise ValidationError(
                            'Chiều rộng ' + self.checkbox_model[0].lower() + ' không có trường hợp null')
                    if self.initial_data['idType'] in [7, 8]:
                        raise ValidationError(
                            'Chiều rộng ' + self.checkbox_model[1].lower() + ' không có trường hợp null')
            if self.initial_data['otherCheck'] == 0:
                other_width = None
                # if other_width is not None:
                #     raise ValidationError('Phải đánh dấu có thông tin phòng họp/sảnh chờ/phòng lạnh riêng')
        else:
            other_width = None
            # if other_width is not None:
            #     raise ValidationError(
            #         'Đối với mô hình ' + self.initial_data['modelType'].lower() + 'sẽ không có thông tin chiều '
            #                                                               'rộng phòng họp/sảnh '
            #                                                               'chờ/phòng lạnh')
        return other_width

    def validate_otherLength(self, other_length):
        if self.initial_data['idType'] not in [1, 3]:
            if self.initial_data['otherCheck'] == 1:
                if other_length <= 0:
                    if self.initial_data['idType'] in [4, 5, 6]:
                        raise ValidationError('Chiều dài ' + self.checkbox_model[0].lower() + ' không có trường hợp 0m')
                    if self.initial_data['idType'] in [7, 8]:
                        raise ValidationError('Chiều dài ' + self.checkbox_model[1].lower() + ' không có trường hợp 0m')
                if other_length is None:
                    if self.initial_data['idType'] in [4, 5, 6]:
                        raise ValidationError('Chiều dài ' + self.checkbox_model[0].lower() + 'không có trường hợp '
                                                                                              'null')
                    if self.initial_data['idType'] in [7, 8]:
                        raise ValidationError('Chiều dài ' + self.checkbox_model[1].lower() + 'không có trường hợp '
                                                                                              'null')
            if self.initial_data['otherCheck'] == 0:
                other_length = None
                # if other_length is not None:
                #     raise ValidationError('Phải đánh dấu có thông tin phòng họp/sảnh chờ/phòng lạnh riêng')
        else:
            other_length = None
            # if other_length is not None:
            #     raise ValidationError(
            #         'Đối với mô hình ' + self.initial_data['modelType'].lower() + 'sẽ không có thông tin chiều '
            #                                                               'dài phòng họp/sảnh '
            #                                                               'chờ/phòng lạnh')
        return other_length

    def validate_otherUserWifi(self, total_people):
        if self.initial_data['idType'] not in [1, 3]:
            if self.initial_data['otherCheck'] == 1:
                if total_people <= 0:
                    if self.initial_data['idType'] in [4, 5, 6]:
                        raise ValidationError(
                            'Số người dùng wifi ' + self.checkbox_model[0].lower() + ' không có trường hợp 0')
                    if self.initial_data['idType'] in [7, 8]:
                        raise ValidationError(
                            'Số người dùng wifi ' + self.checkbox_model[1].lower() + ' không có trường hợp 0')
                if total_people is None:
                    if self.initial_data['idType'] in [4, 5, 6]:
                        raise ValidationError(
                            'Số người dùng wifi ' + self.checkbox_model[0].lower() + 'không có trường hợp '
                                                                                     'null')
                    if self.initial_data['idType'] in [7, 8]:
                        raise ValidationError(
                            'Số người dùng wifi ' + self.checkbox_model[1].lower() + 'không có trường hợp '
                                                                                     'null')
            if self.initial_data['otherCheck'] == 0:
                total_people = None
                # if total_people is not None:
                #     raise ValidationError('Phải đánh dấu có thông tin phòng họp/sảnh chờ/phòng lạnh riêng')
        else:
            total_people = None
            # if total_people is not None:
            #     raise ValidationError(
            #         'Đối với mô hình ' + self.initial_data['modelType'].lower() + 'sẽ không có thông tin số người '
            #                                                               'dùng wifi phòng '
            #                                                               'họp/sảnhchờ/phòng lạnh')
        return total_people

    def validate_userWifi(self, user_wifi):
        if user_wifi < 0:
            raise ValidationError(
                'Thông tin số người dùng Wifi đối với mô hình ' + str(
                    self.initial_data['modelType'].lower() + " không được < 0!"))
        if user_wifi == 0 and self.initial_data['idType'] != 4:
            raise ValidationError(
                'Thông tin số người dùng Wifi đối với mô hình ' + str(
                    self.initial_data['modelType'].lower() + " không được = 0!"))
        return user_wifi

    def validate_userLAN(self, user_lan):
        if user_lan < 0:
            raise ValidationError(
                'Thiếu hoặc sai thông tin số người dùng LAN đối với mô hình ' + str(
                    self.initial_data['modelType'].lower() + "!"))
        return user_lan

    def validate_userCamera(self, user_camera):
        if user_camera < 0:
            raise ValidationError(
                'Thiếu hoặc sai thông tin số người dùng camera đối với mô hình ' + str(
                    self.initial_data['modelType'].lower() + "!"))
        return user_camera

    def validate_luxPackageCheck(self, lux_check):
        """
        True - 1
        False - 0
        """
        if lux_check not in [0, 1]:
            raise ValidationError('Gói LUX sai hoặc thiếu thông tin')
        return lux_check

    def validate_uploadAlotCheck(self, upload_a_lot):
        """
        True - 1
        False - 0
        """
        if upload_a_lot not in [0, 1]:
            raise ValidationError('Thông tin upload nhiều sai hoặc thiếu thông tin')
        return upload_a_lot

    def validate_concurrentUsageRate(self, data_used):
        if data_used > 100 or data_used < 0:
            raise ValidationError('Tỷ lệ sử dụng đồng thời không hợp lệ!')
        return data_used

    def validate_totalAP(self, data):
        count_item = 0
        if data < 0:
            raise ValidationError('Tổng số AP không được nhỏ hơn 0')
        for item in self.initial_data['accessPoints']:
            count_item += item['quantity']
        return count_item

    def validate_internetPackages(self, data):
        for i in data:
            if not isinstance(i, dict):
                raise ValidationError('Các đối tượng trong danh sách gói cước không phải dạng dict')
            for _key in self.key_internet_package:
                i[_key] = i.get(_key, None)
                if _key == 'id':
                    i[_key] = 0
                if i[_key] is None:
                    raise ValidationError('Thiêu thông tin gói cước, xin vui lòng nhập đầy đủ thông tin')
            if i['quantity'] <= 0:
                raise ValidationError('Số lượng gói cước không phù hợp: ' + str(i['quantity']))
        return data

    def validate_routers(self, routers):
        for i in routers:
            if not isinstance(i, dict):
                raise ValidationError('Các đối tượng trong danh sách router không phải dạng dict')
            for _key in self.key_routers:
                i[_key] = i.get(_key, None)
                if _key == 'id':
                    i[_key] = 0
                if i[_key] is None and _key not in ['wifi24Pow', 'wifi5Pow']:
                    raise ValidationError('Thiêu thông tin router, xin vui lòng nhập đầy đủ thông tin')
            if i['quantity'] <= 0:
                raise ValidationError('Số lượng router không phù hợp: ' + str(i['quantity']))
        return routers

    def validate_accessPoints(self, access_points):
        for i in access_points:
            if not isinstance(i, dict):
                raise ValidationError('Các đối tượng trong danh sách access point không phải dạng dict')
            for _key in self.key_access_point:
                i[_key] = i.get(_key, None)
                if _key == 'id':
                    i[_key] = 0
                if i[_key] is None and _key not in ['wifi24Pow', 'wifi5Pow']:
                    raise ValidationError('Thiêu thông tin access point, xin vui lòng nhập đầy đủ thông tin')
            if i['quantity'] <= 0:
                raise ValidationError('Số lượng access point không phù hợp: ' + str(i['quantity']))
        return access_points


class TransformImageValidate(Serializer):
    image = ImageField(required=True, allow_null=False, allow_empty_file=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='tệp tin hình ảnh'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='tệp tin hình ảnh'),
        'invalid_image': gb.TXT_ERROR_MESSAGE_FORMAT['invalid_image'].format(item='tệp tin hình ảnh'),
    })
    sketches = ListField(required=True, allow_null=False, allow_empty=True, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='thông số bản vẽ hình ảnh'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='thông số bản vẽ hình ảnh'),
        'invalid': gb.TXT_ERROR_MESSAGE_FORMAT['invalid'].format(item='thông số bản vẽ hình ảnh'),
        'empty': gb.TXT_ERROR_MESSAGE_FORMAT['empty'].format(item='thông số bản vẽ hình ảnh'),
    })
    sketchesType = CharField(required=True, allow_null=False, allow_blank=False, error_messages={
        'required': gb.TXT_ERROR_MESSAGE_FORMAT['required'].format(item='loại thông số bản vẽ hình ảnh'),
        'null': gb.TXT_ERROR_MESSAGE_FORMAT['null'].format(item='loại thông số bản vẽ hình ảnh'),
        'blank': gb.TXT_ERROR_MESSAGE_FORMAT['blank'].format(item='loại thông số bản vẽ hình ảnh'),
    })

    def validate_sketchesType(self, sketchesType):
        if sketchesType.lower() not in ['paper', 'app']:
            raise ValidationError('Loại thông số bản vẽ hình ảnh không hợp lệ')
        return sketchesType.lower()
