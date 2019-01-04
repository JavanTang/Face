import base64
import traceback
import io
import numpy as np
import os
from .time_utils import genera_stamp
import cv2

current = os.path.dirname(__name__)
project = os.path.dirname(current)
img_path = os.path.join(project, 'database/detect_image') # 图片需要存放的位置


def array_to_file(array_data, names):
    '''数组转图片文件

    Arguments:
        array_data {array} -- 人脸的数组
        names {str} -- 人员的编号
    '''
    path = [os.path.join(img_path, genera_stamp())+'.jpg' for i in names]
    for index in range(len(array_data)):
        img_array = array_data[index]
        cv2.imwrite(path[index], img_array)
    
    return path


def array_to_base64(array_data):
    '''数组转base64

    Arguments:
        array_data {numpy} -- 图片数组
    '''
    arr = np.arange(12).reshape(3, 4)
    bytesio = io.BytesIO()
    np.savetxt(bytesio, arr)  # 只支持1维或者2维数组，numpy数组转化成字节流
    content = bytesio.getvalue()  # 获取string字符串表示
    b64_code = base64.b64encode(content)
    return b64_code


def base64_to_image(base64_data):
    """
    :param base64_data: 图片的base64编码
    :return: image: 图片对象
    """

    image = base64.b64decode(base64_data)
    return image


def image_to_base64(image):
    """
    :param image: 图片所在路径
    :return: base64_data: 图片对应的base64编码
    """

    try:
        with open(image, 'rb') as f:
            base64_data = base64.b64encode(f.read())
            base64_data = base64_data.decode()
            return base64_data
    except:
        traceback.print_exc()
