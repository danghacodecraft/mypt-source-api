import cv2
import numpy as np
from datetime import datetime
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

font = cv2.FONT_HERSHEY_COMPLEX


# resize image keep original ratio, make sure width and height smaller than width or height of 960x1280, if width or
# height after resize is smaller than 960 or 1280, add extra space to 4 side to fit 960x1280
def resize_image(img):
    if img.shape[0] > img.shape[1]:
        ratio = img.shape[0] / 1280
        width = int(img.shape[1] / ratio)
        height = 1280
    else:
        ratio = img.shape[1] / 960
        width = 960
        height = int(img.shape[0] / ratio)
    img = cv2.resize(img, (width, height))
    # add extra space to 4 side to fit 960x1280
    if width < 960:
        img = cv2.copyMakeBorder(img, 0, 0, int((960 - width) / 2), int((960 - width) / 2), cv2.BORDER_CONSTANT,
                                 value=(255, 255, 255))
    if height < 1280:
        img = cv2.copyMakeBorder(img, int((1280 - height) / 2), int((1280 - height) / 2), 0, 0, cv2.BORDER_CONSTANT,
                                 value=(255, 255, 255))
    return img


def create_image(image, contract, location, timeUpload):
    image = resize_image(image)
    # image = cv2.resize(image, (960, 1280), interpolation=cv2.INTER_LINEAR)
    h, w, c = image.shape
    # # xoay ảnh về đúng hướng
    # if w > h:
    #     image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    ha = int(0.1 * h)
    area = np.full((ha, w, c), fill_value=255, dtype=np.uint8)

    textsize = cv2.getTextSize(contract, font, 1, 2)[0]
    textX = 10
    textY = textsize[1] + 10
    p = (textX, textY)
    cv2.putText(area, contract, p, fontFace=font, fontScale=1, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)

    textsize = cv2.getTextSize(timeUpload, font, 1, 2)[0]
    textX = w - textsize[0] - 10
    textY = textsize[1] + 10
    p = (textX, textY)
    cv2.putText(area, timeUpload, p, fontFace=font, fontScale=1, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)

    textsize = cv2.getTextSize(location, font, 1, 2)[0]
    textX = int((w - textsize[0]) / 2)
    textY = ha - 10
    p = (textX, textY)
    cv2.putText(area, location, p, fontFace=font, fontScale=1, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_AA)

    # # xoay ảnh về đúng hướng
    # if w > h:
    #     image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    out = np.concatenate((image, area))
    # cv2.imwrite("C:/Users/long/Desktop/out.jpg", out)
    return out


def create_and_save_image(image_file, contract, location, timeUpload):
    try:
        myfile = image_file.read()
        image = cv2.imdecode(np.frombuffer(myfile, np.uint8), cv2.IMREAD_UNCHANGED)

        out = create_image(image, contract, location, timeUpload)
        out = cv2.cvtColor(out, cv2.COLOR_BGR2RGB)

        PIL_image = Image.fromarray(out, mode="RGB")

        thumb_io = BytesIO()
        PIL_image.save(thumb_io, format='JPEG')
        out = ContentFile(thumb_io.getvalue())
        return out
    except Exception as ex:
        print(f"{datetime.now()} >> create_image_custom >> {ex}")
        return None

# Test
# contract = "SGH123456"
# location = "10.7820056,106.6616821"
# timeUpload = "03/11/2022 15:49:20"
#
# image_path = "img_input/1.jpg"
# image = cv2.imread(image_path)
# out = create_image(image, contract, location, timeUpload)
# cv2.imwrite("img_output/out.jpg", out)
# print(type(out))
# cv2.imshow("out", out)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
