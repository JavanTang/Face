import base64
import traceback
import time


def base64_to_image(base64_data):
    """
    :param base64_data: 图片的base64编码
    :return: image: 图片对象
    """

    try:
        image = base64.b64decode(base64_data)
        return image
    except:
        traceback.print_exc()


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


def get_time_base64():
    """将当前时间戳转化为base64编码。
    """
    cur_time = time.time()
    encodestr = base64.b64encode(str(cur_time).encode('utf-8'))

    return encodestr


def str_to_base64(obj):
    """将字符串转化为base64
    """
    obj = str(obj)
    return base64.b64encode(obj.encode('utf-8'))
