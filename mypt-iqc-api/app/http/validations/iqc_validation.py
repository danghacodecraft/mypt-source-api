import ast
from rest_framework.serializers import *
from rest_framework import serializers
from app.core.helpers.utils import *
from core.helpers import helper, iqc_global_variable


class iQCDeploymentValidate(Serializer):
    contractCode = CharField(required=False, error_messages={
        'required': 'Số hợp đồng là bắt buộc',
        'blank': 'Số hợp đồng không được rỗng!',
        'null': 'Số hợp đồng không là giá trị null!'
    })

    def validate_contractCode(self, contractCode):
        if len(contractCode) != 9:
            raise ValidationError("Số hợp đồng phải đủ 9 ký tự")
        if not contractCode.isalnum():
            raise ValidationError("Số hợp đồng không được có ký tự đặc biệt")
        return contractCode


class iQCPracticePointValidate(Serializer):
    contractCode = CharField(required=False, error_messages={
        'required': 'Số hợp đồng là bắt buộc',
        'blank': 'Số hợp đồng không được rỗng!',
        'null': 'Số hợp đồng không là giá trị null!'
    })

    def validate_contractCode(self, contractCode):
        if not len(contractCode) == 14:
            raise ValidationError("Mã tập điểm phải bằng 14 ký tự")
        return contractCode


class iQCReturnContractVeValidate(Serializer):
    contractCode = CharField(required=False, error_messages={
        'required': 'Số hợp đồng là bắt buộc',
        'blank': 'Số hợp đồng không được rỗng!',
        'null': 'Số hợp đồng không là giá trị null!'
    })

    def validate_contractCode(self, contractCode):
        if len(contractCode) != 9:
            raise ValidationError("Số hợp đồng phải đủ 9 ký tự")
        if not contractCode.isalnum():
            raise ValidationError("Số hợp đồng không được có ký tự đặc biệt")
        return contractCode


class IqcUploadImageValidate(Serializer):
    contract = CharField(required=True,
                         error_messages={'required': 'Hợp đồng là bắt buộc!',
                                         'blank': 'Hợp đồng không được rỗng!',
                                         'null': 'Hợp đồng không là giá trị null!'})
    location = CharField(required=True,
                         error_messages={
                             'required': 'Tọa độ là bắt buộc!',
                             'blank': 'Tọa độ không được rỗng!',
                             'null': 'Tọa độ không là giá trị null'
                         })
    timeUpload = CharField(required=True,
                           error_messages={
                               'required': 'Thời gian upload là bắt buộc!',
                               'blank': 'Thời gian upload không được rỗng!',
                               'null': 'Thời gian upload không là giá trị null!'
                           })
    image = FileField(required=True,
                      error_messages={
                          "required": 'File ảnh là bắt buộc!',
                          'empty': 'File ảnh là bắt buộc!',
                          'blank': 'File ảnh không được rỗng!',
                          'null': 'File ảnh không là giá trị null!'
                      })

    def validate_timeUpload(self, time_upload_str):
        try:
            datetime.strptime(time_upload_str, helper.format_to)
        except ValueError:
            raise serializers.ValidationError("Định dạng timeUpload change hợp lệ!")

        now = datetime.now()
        time_upload = datetime.strptime(time_upload_str, helper.format_to)
        if time_upload > now:
            raise serializers.ValidationError("Thời gian upload không hợp lệ!")
        if not (now - timedelta(hours=iqc_global_variable.IMAGE_UPLOAD_DEADLINE)) <= time_upload <= now:
            raise serializers.ValidationError("Ảnh hết hạn upload (quá 24h)")

        return time_upload_str


def iqc_upload_image_validate_func(data, files):
    if "typeiQC" not in data:
        return {
            "result": False,
            "message": "typeiQC là bắt buộc!"
        }
    if "contract" not in data:
        return {
            "result": False,
            "message": "contract là bắt buộc!"
        }
    if "imagesInfo" not in data:
        return {
            "result": False,
            "message": "imagesInfo là bắt buộc!"
        }
    type_IQC = data["typeiQC"]
    contract_str = data["contract"]
    images_info_str = data["imagesInfo"]
    images = files.getlist('images')

    # kiem tra typeIQC
    if empty(type_IQC):
        return {
            "result": False,
            "message": "typeiQC không hợp lệ!"
        }
    elif type_IQC not in iqc_global_variable.MIN_MAX_IMAGE_UPLOAD:
        return {
            "result": False,
            "message": "typeiQC này không tồn tại!"
        }

    # Kiem tra so hop dong
    if type_IQC == "trien_khai":
        deployment_contract_validate = iQCDeploymentValidate(data={"contractCode": contract_str})
        if not deployment_contract_validate.is_valid():
            return {
                "result": False,
                "message": list(deployment_contract_validate.errors.values())[0][0]
            }
    elif type_IQC == "ha_tang_ngoai_vi":
        practice_point_validate = iQCPracticePointValidate(data={"contractCode": contract_str})
        if not practice_point_validate.is_valid():
            return {
                "result": False,
                "message": list(practice_point_validate.errors.values())[0][0]
            }
    else:
        return_contract_validate = iQCReturnContractVeValidate(data={"contractCode": contract_str})
        if not return_contract_validate.is_valid():
            return {
                "result": False,
                "message": list(return_contract_validate.errors.values())[0][0]
            }
    if empty(images_info_str):
        return {
            "result": False,
            "message": "imagesInfo không hợp lệ!"
        }
    if empty(images):
        return {
            "result": False,
            "message": "images là bắt buộc và không được rỗng!"
        }

    contract = contract_str
    images_info = ast.literal_eval(images_info_str)
    images = images

    if len(images_info) > len(images):
        return {
            "result": False,
            "message": "Số lượng thông tin ảnh lớn hơn số lượng ảnh!"
        }
    elif len(images_info) < len(images):
        return {
            "result": False,
            "message": "Số lượng ảnh lớn hơn số lượng thông tin ảnh!"
        }

    min_images = iqc_global_variable.MIN_MAX_IMAGE_UPLOAD[type_IQC]["MIN"]
    max_images = iqc_global_variable.MIN_MAX_IMAGE_UPLOAD[type_IQC]["MAX"]
    if not (min_images <= len(images) <= max_images):
        return {
            "result": False,
            "message": f"Số lượng ảnh không hợp lệ! ({min_images} <= Số lượng ảnh <= {max_images})"
        }

    # Kiem tra du lieu trong mang imagesInfo
    for idx, image_info in enumerate(images_info):
        err_msg = ""
        if "location" not in image_info or empty(image_info.get("location", None)):
            err_msg = f"location trong imagesInfo index={idx} là bắt buộc và không được rỗng!"
        elif "timeUpload" not in image_info or empty(image_info.get("timeUpload", None)):
            err_msg = f"timeUpload trong imagesInfo index={idx} là bắt buộc và không được rỗng!"
        else:
            time_upload_str = image_info["timeUpload"]
            try:
                datetime.strptime(time_upload_str, helper.format_to)
            except ValueError:
                err_msg = f"timeUpload trong imagesInfo index={idx} không hợp lệ!"

            now = datetime.now()
            time_upload = datetime.strptime(time_upload_str, helper.format_to)
            if time_upload > now:
                err_msg = f"Thời gian timeUpload trong imagesInfo index={idx} không hợp lệ!"
            elif not (now - timedelta(hours=iqc_global_variable.IMAGE_UPLOAD_DEADLINE)) <= time_upload <= now:
                err_msg = f"Ảnh hết hạn upload (quá 24h) trong imagesInfo, index={idx}!"
        if err_msg:
            return {
                "result": False,
                "message": err_msg
            }
        image_info["image"] = images[idx]
        image_info["contract"] = contract

    # kiem tra size, content_type trong danh sach anh upload
    for idx, image in enumerate(images):
        err_msg = ""

        if image.size > 5242880:
            err_msg = f"Ảnh ở index={idx}, có kích thước file quá lớn!"
        elif image.content_type not in ['image/heic', 'image/png', 'image/jpeg']:
            err_msg = f"Ảnh ở index={idx} có loại file không phù hợp!"
        if err_msg:
            return {
                "result": False,
                "message": err_msg
            }

    # ket qua tra ve sau khi da validate
    return {
        "result": True,
        "message": "Success",
        "data": images_info
    }


class IqcCreateUpdateReturnContractValidate(Serializer):
    actionType = CharField(required=True, error_messages={
        'required': 'actionType là bắt buộc',
        'blank': 'actionType không được rỗng!',
        'null': 'actionType không là giá trị null!'
    })
    nameContract = CharField(required=True, error_messages={
        'required': 'Hợp đồng là bắt buộc!',
        'blank': 'Hợp đồng không được rỗng!',
        'null': 'Hợp đồng không là giá trị null!'})
    returnCause = ListField(required=True,
                            allow_empty=False,
                            error_messages={
                                'required': 'Danh sách nguyên nhân là bắt buộc!',
                                'null': 'Danh sách nguyên nhân không là giá trị null',
                                'empty': 'Danh sách nguyên nhân không được rỗng!',
                            })
    images = ListField(required=True,
                       allow_empty=False,
                       error_messages={
                           'required': 'Danh sách hình ảnh là bắt buộc!',
                           'null': 'Danh sách hình ảnh không là giá trị null',
                           'empty': 'Danh sách hình ảnh không được rỗng!',
                       })

    def validate_actionType(self, action_type):
        if action_type not in ["CREATE", "UPDATE"]:
            raise serializers.ValidationError("actionType không hợp lệ!")
        return action_type

    def validate_nameContract(self, nameContract):
        if len(nameContract) != 9:
            raise serializers.ValidationError("Số hợp đồng phải đủ 9 ký tự")
        if not nameContract.isalnum():
            raise serializers.ValidationError("Số hợp đồng không được có ký tự đặc biệt")
        return nameContract

    def validate_returnCause(self, returnCause):
        for key, value in enumerate(returnCause):
            if not isinstance(value, int):
                raise serializers.ValidationError("Giá trị nguyên nhân trả về phải là index")
        return returnCause

    def validate_images(self, images):
        if not isinstance(images, list):
            raise serializers.ValidationError("images phải là một danh sách!")
        if len(images) < iqc_global_variable.MIN_RETURN_CONTRACT_IMAGE_UPLOAD:
            raise serializers.ValidationError(
                f"Tối thiểu là {iqc_global_variable.MIN_RETURN_CONTRACT_IMAGE_UPLOAD} ảnh!")
        if len(images) > iqc_global_variable.MAX_RETURN_CONTRACT_IMAGE_UPLOAD:
            raise serializers.ValidationError(f"Tối đa là {iqc_global_variable.MAX_RETURN_CONTRACT_IMAGE_UPLOAD} ảnh")

        errors_list = []
        for idx, image in enumerate(images):
            errs = []
            if "image" not in image:
                errs.append('không tồn tại key image')
            if "index" not in image:
                errs.append('không tồn tại key index')
            if not empty(errs):
                errors_list.append(f'images có object thứ {idx + 1} có lỗi: {", ".join(errs)}')

        if not empty(errors_list):
            raise serializers.ValidationError("; ".join(errors_list))

        return images


class IqcCreateDeploymentContractValidate(serializers.Serializer):
    nameContract = CharField(required=True, error_messages={
        'required': 'Số hợp đồng là bắt buộc',
        'blank': 'Số hợp đồng không được rỗng!',
        'null': 'Số hợp đồng không là giá trị null!'
    })
    typeServiceDeploy = IntegerField(required=True, error_messages={
        'required': 'Loại dịch vụ triển khai là bắt buộc',
        'blank': 'Loại dịch vụ triển khai không được rỗng!',
        'null': 'Loại dịch vụ triển khai không là giá trị null!'
    })

    modelHouse = IntegerField(required=True, error_messages={
        'required': 'Mô hình nhà là bắt buộc',
        'blank': 'Mô hình nhà không được rỗng!',
        'null': 'Mô hình nhà không là giá trị null!'
    })
    locationUpload = CharField(required=True, error_messages={
        'required': 'Toạ độ tạo hợp đồng là bắt buộc',
        'blank': 'Toạ độ tạo hợp đồng không được rỗng!',
        'null': 'Toạ độ tạo hợp đồng không là giá trị null!'
    })
    accuracyDate = CharField(required=False)
    images = ListField(required=True,
                       allow_empty=False,
                       error_messages={
                           'required': 'Danh sách hình ảnh là bắt buộc!',
                           'null': 'Danh sách hình ảnh không là giá trị null',
                           'empty': 'Danh sách hình ảnh không được rỗng!',
                       })

    def validate_nameContract(self, nameContract):
        if len(nameContract) != 9:
            raise serializers.ValidationError("Số hợp đồng phải đủ 9 ký tự")
        if not nameContract.isalnum():
            raise ValidationError("Số hợp đồng không được có ký tự đặc biệt")
        return nameContract

    def validate_typeServiceDeploy(self, typeServiceDeploy):
        if not isinstance(typeServiceDeploy, int):
            raise serializers.ValidationError("Giá trị loại dịch vụ triển khai phải là số nguyên")
        return typeServiceDeploy

    def validate_modelHouse(self, modelHouse):
        if not isinstance(modelHouse, int):
            raise serializers.ValidationError("Giá trị mô hình nhà phải là số nguyên")
        return modelHouse

    def validate_images(self, images):
        if not isinstance(images, list):
            raise serializers.ValidationError("images phải là một danh sách!")
        if len(images) != iqc_global_variable.FIXED_DEPLOYMENT_CONTRACT_IMAGE_UPLOAD:
            raise serializers.ValidationError(
                f"Hợp đồng triển khai là phải đủ {iqc_global_variable.FIXED_DEPLOYMENT_CONTRACT_IMAGE_UPLOAD} ảnh!")

        errors_list = []
        for idx, image in enumerate(images):
            if "image" not in image:
                errors_list.append('không tồn tại key image')
            if "index" not in image:
                errors_list.append('không tồn tại key index')
            if empty(image['image']):
                errors_list.append(f'Ảnh thứ {idx + 1} bị thiếu ảnh')
            # if not image['image'].endswith(".jpg"):
            #     errors_list.append(f'Ảnh thứ {idx + 1} sai định dạng ảnh (.jpg)')

        if not empty(errors_list):
            raise serializers.ValidationError("; ".join(errors_list))

        return images


class IqcUpdateDeploymentContractValidate(serializers.Serializer):
    nameContract = CharField(required=True, error_messages={
        'required': 'Số hợp đồng là bắt buộc',
        'blank': 'Số hợp đồng không được rỗng!',
        'null': 'Số hợp đồng không là giá trị null!'
    })
    locationUpload = CharField(required=True, error_messages={
        'required': 'Toạ độ tạo hợp đồng là bắt buộc',
        'blank': 'Toạ độ tạo hợp đồng không được rỗng!',
        'null': 'Toạ độ tạo hợp đồng không là giá trị null!'
    })
    accuracyDate = CharField(required=False, allow_blank=True, allow_null=True)
    images = ListField(required=True,
                       allow_empty=False,
                       error_messages={
                           'required': 'Danh sách hình ảnh là bắt buộc!',
                           'null': 'Danh sách hình ảnh không là giá trị null',
                           'empty': 'Danh sách hình ảnh không được rỗng!',
                       })

    def validate_nameContract(self, nameContract):
        if len(nameContract) != 9:
            raise serializers.ValidationError("Số hợp đồng phải đủ 9 ký tự")
        if not nameContract.isalnum():
            raise ValidationError("Số hợp đồng không được có ký tự đặc biệt")
        return nameContract

    def validate_images(self, images):
        if not isinstance(images, list):
            raise serializers.ValidationError("images phải là một danh sách!")
        if len(images) != iqc_global_variable.FIXED_DEPLOYMENT_CONTRACT_IMAGE_UPLOAD:
            raise serializers.ValidationError(
                f"Hợp đồng triển khai là phải đủ {iqc_global_variable.FIXED_DEPLOYMENT_CONTRACT_IMAGE_UPLOAD} ảnh!")

        errors_list = []
        for idx, image in enumerate(images):
            if "image" not in image:
                errors_list.append('không tồn tại key image')
            if "index" not in image:
                errors_list.append('không tồn tại key index')
            if empty(image['image']):
                errors_list.append(f'Ảnh thứ {idx + 1} bị thiếu ảnh')
            # if not image['image'].endswith(".jpg"):
            #     errors_list.append(f'Ảnh thứ {idx + 1} sai định dạng ảnh (.jpg)')

        if not empty(errors_list):
            raise serializers.ValidationError("; ".join(errors_list))

        return images


class IqcCreatePracticePointValidate(serializers.Serializer):
    practicePoint = CharField(required=True, error_messages={
        'required': 'Số tập điểm là bắt buộc',
        'blank': 'Số tập điểm không được rỗng!',
        'null': 'Số tập điểm không là giá trị null!'
    })
    images = ListField(required=True,
                       allow_empty=False,
                       error_messages={
                           'required': 'Danh sách hình ảnh là bắt buộc!',
                           'null': 'Danh sách hình ảnh không là giá trị null',
                           'empty': 'Danh sách hình ảnh không được rỗng!',
                       })

    def validate_practicePoint(self, practice_point):
        if not len(practice_point) == 14:
            raise serializers.ValidationError("Số tập điểm phải bằng 14 ký tự!")
        return practice_point

    def validate_images(self, images):
        for obj in images:
            for index in obj['causeImage']:
                if not isinstance(index, int):
                    raise serializers.ValidationError("causeImage phải là giá trị số nguyên")
            for index in obj['fixError']:
                if not isinstance(index, int):
                    raise serializers.ValidationError("fixError phải là giá trị số nguyên")

        return images
