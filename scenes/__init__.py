from .realtime_fr import ScenesRealTimeFaceRecognization
'''
@Author: TangZhiFeng
@Data: 2018-12-28
@LastEditors: Please set LastEditors
@LastEditTime: 2018-12-29 09:52:58
@Description: 应用工程算法基类
'''
import queue
from processes.recorder import CameraReader
import os
import sys
current = os.path.dirname(__name__)
project = os.path.dirname(current)

sys.path.append(project)


class BaseEngineering(object):
    '''应用工程视频类算法基类
    '''

    def __init__(self, ip, read_fps_interval):
        '''多算法多位置处理定义，在使用该算法时，通常会有多个算法，同时在多个算法处理完毕之后，需要将算法进行，多级处理
        例如算法处理完毕之后，可能会要存照片，可能会发请求等等。

        Arguments:
            ip {str} -- 摄像头ip地址

        '''
        self.q1 = queue.Queue()
        self.q2 = queue.Queue()
        self.camera = CameraReader(ip, ip, read_fps_interval, self.q1, None)
        self.algothems = []

    def algorithms_distribution(self):
        '''让数据经过算法1->算法2->算法3等等
        '''
        


    def add_algothems(self, algorithms, processes=False):
        '''添加算法

        Arguments:
            algorithms {func} -- 执行算法的函数

        Keyword Arguments:
            processes {bool} -- 是否使用进程的方式 (default: {False})
        '''
        self.algothems.append(algorithms)
