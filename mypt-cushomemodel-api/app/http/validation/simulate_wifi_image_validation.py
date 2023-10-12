from rest_framework.serializers import *


class SimulateWifiImageValidate(Serializer):
    houseFloor = IntegerField(required=True, allow_null=False, error_messages={
        'required': 'Số tầng của ảnh là bắt buộc!',
        'null': 'Vui lòng chọn số tầng của ảnh!'
    })

    houseWidth = FloatField(required=True, allow_null=False,
                            error_messages={
                                'required': 'Chiều rộng là bắt buộc!',
                                'null': 'Vui lòng chọn chiều rộng!',
                                'blank': 'Chiều rộng không được rỗng!',
                            })
    houseLength = FloatField(required=True, allow_null=False,
                             error_messages={
                                 'required': 'Chiều dài là bắt buộc!',
                                 'null': 'Vui lòng chọn chiều dài!',
                                 'blank': 'Chiều dài không được rỗng!',
                             })
    txLocation = ListField(required=True,
                           allow_empty=False,
                           error_messages={
                               'required': 'Vị trị các thiết bị là bắt buộc!',
                               'null': 'Vị trị các thiết bị không được là giá trị null',
                               'empty': 'Vị trị các thiết bị không được rỗng!',
                           })
    txPower = ListField(required=True,
                        allow_empty=False,
                        error_messages={
                            'required': 'Vị trị các thiết bị là bắt buộc!',
                            'null': 'Vị trị các thiết bị không được là giá trị null',
                            'empty': 'Vị trị các thiết bị không được rỗng!',
                        })
    txName = ListField(required=True,
                       allow_empty=False,
                       error_messages={
                           'required': 'Tên các thiết bị là bắt buộc!',
                           'null': 'Tên các thiết bị không được là giá trị null',
                           'empty': 'Tên các thiết bị không được rỗng!',
                       })
    wallAttenuation = IntegerField(required=True, allow_null=False,
                                   error_messages={
                                       'required': 'Thông tin vật cản là bắt buộc!',
                                       'null': 'Vui lòng chọn thông tin vật cản!',
                                       'blank': 'Thông tin vật cản không được rỗng!',
                                   })
    wallAttenuationInfo = DictField(required=True, allow_null=False,
                                    error_messages={
                                        'required': 'Thông tin vật cản là bắt buộc!',
                                        'null': 'Vui lòng chọn thông tin vật cản!',
                                        'blank': 'Thông tin vật cản không được rỗng!',
                                    })
    imageShape = ListField(required=True,
                           allow_empty=False,
                           error_messages={
                               'required': 'Khung mô hình là bắt buộc!',
                               'null': 'Khung mô hình không được là giá trị null',
                               'empty': 'Khung mô hình không được rỗng!',
                           })
    corners = ListField(required=True,
                        allow_empty=False,
                        error_messages={
                            'required': 'Góc mô hình là bắt buộc!',
                            'null': 'Góc mô hình không được là giá trị null',
                            'empty': 'Góc mô hình không được rỗng!',
                        })
    edges = ListField(required=True,
                      allow_empty=False,
                      error_messages={
                          'required': 'Cạnh mô hình là bắt buộc!',
                          'null': 'Cạnh mô hình không được là giá trị null',
                          'empty': 'Cạnh mô hình không được rỗng!',
                      })

    def validate_houseFloor(self, houseFloor):
        return houseFloor

    def validate_houseWidth(self, houseWidth):
        if houseWidth == 0:
            raise ValidationError('Thông tin chiều rộng mô hình nhà không có trường hợp 0m!')
        return houseWidth

    def validate_houseLength(self, houseLength):
        if houseLength == 0:
            raise ValidationError('Thông tin chiều dài mô hình nhà không có trường hợp 0m!')
        return houseLength


class SimulateWifiAppImageValidate(Serializer):
    houseFloor = IntegerField(required=True, allow_null=False, error_messages={
        'required': 'Số tầng của ảnh là bắt buộc!',
        'null': 'Vui lòng chọn số tầng của ảnh!'
    })
    houseWidth = FloatField(required=True, allow_null=False, error_messages={
        'required': 'Chiều rộng là bắt buộc!',
        'null': 'Vui lòng chọn chiều rộng!',
        'blank': 'Chiều rộng không được rỗng!',
    })
    houseLength = FloatField(required=True, allow_null=False, error_messages={
        'required': 'Chiều dài là bắt buộc!',
        'null': 'Vui lòng chọn chiều dài!',
        'blank': 'Chiều dài không được rỗng!',
    })
    txInfo = ListField(required=True, allow_empty=False, error_messages={
        'required': 'Vị trị các thiết bị là bắt buộc!',
        'null': 'Vị trị các thiết bị không được là giá trị null',
        'empty': 'Vị trị các thiết bị không được rỗng!',
    })
    imageShape = ListField(required=True, allow_empty=False, error_messages={
        'required': 'Khung mô hình là bắt buộc!',
        'null': 'Khung mô hình không được là giá trị null',
        'empty': 'Khung mô hình không được rỗng!',
    })
    sketches = ListField(required=True, allow_empty=False, error_messages={
        'required': 'Bản thảo sketches là bắt buộc!',
        'null': 'Bản thảo sketches không được là giá trị null!',
        'empty': 'Bản thảo sketches không được rỗng!',
    })

    def validate_houseFloor(self, houseFloor):
        return houseFloor

    def validate_houseWidth(self, houseWidth):
        if houseWidth == 0:
            raise ValidationError('Thông tin chiều rộng mô hình nhà không có trường hợp 0m!')
        return houseWidth

    def validate_houseLength(self, houseLength):
        if houseLength == 0:
            raise ValidationError('Thông tin chiều dài mô hình nhà không có trường hợp 0m!')
        return houseLength

    def validate_txInfo(self, txInfo):
        for data in txInfo:
            if not all(key in data for key in ['location', 'power', 'type', 'modelType']):
                raise ValidationError('Thiếu thông tin vị trí thiết bị trên bản vẽ!')

            if not isinstance(data['location'], list):
                raise ValidationError('Sai thông tin định dạng location')

            if not isinstance(data['power'], dict):
                raise ValidationError('Sai thông tin định dạng công suất wifi')

            if 'wifi24' not in data['power'] or 'wifi5' not in data['power']:
                raise ValidationError('Sai thông tin định dạng công suất wifi')

        return txInfo
