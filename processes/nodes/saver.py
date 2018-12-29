import time
import os

from utils.decorator import UnitTestDecorator
from processes.message import RecognizerMessage, CameraMessage

from . import BaseNode


@UnitTestDecorator
class Saver(BaseNode):
    # TODO 获取算法节点的数据后进行各种操作
    pass
