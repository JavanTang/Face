from .realtime_fr import ScenesRealTimeFaceRecognization
'''
@Author: TangZhiFeng
@Data: 2018-12-28
@LastEditors: TangZhiFeng
@LastEditTime: 2018-12-29 15:59:42
@Description: 应用工程算法基类
'''
import queue
from processes.recorder import CameraReader
import os
import sys
import random
import _thread
current = os.path.dirname(__name__)
project = os.path.dirname(current)

sys.path.append(project)


class BaseEngineering(object):
    '''应用工程视频类算法基类
    使用方式：
        1. 初始化。
        2. 添加算法。
        3. 运行算法。
        4. 通过generater监听最后的结果。
    '''

    def __init__(self, real_time):
        '''多算法多位置处理定义，在使用该算法时，通常会有多个算法，同时在多个算法处理完毕之后，需要将算法进行，多级处理
        例如算法处理完毕之后，可能会要存照片，可能会发请求等等。

        Arguments:
            ip {str} -- 摄像头ip地址

        '''
        self.q1 = queue.Queue()
        self.q2 = queue.Queue()
        self.algorithems = []
        self.real_time = real_time

        self.lucky_number = random.uniform(9.9, 2)  # 用来判断是否需要丢失这个data，用在algorithms_distribution中判断build_data之后的数据是否符合要求。

    def generater(self, data):
        '''经过最后的节点产生的数据，返回数据

        Arguments:
            data {[type]} -- [description]
        '''
        raise NotImplementedError('generater')

    def build_data(self, i, data):
        '''处理数据,当data已经没有意义传递了就直接将data赋值成为self.lucky_number。

        Arguments:
            i {int} -- 是第几个算法需要进行处理。
            data {obj} -- 需要处理的数据，我们要通过不同的算法步骤self.current去定义数据的处理方式。
        '''
        raise NotImplementedError('build_data')

    def into_algorithems(self, i, data):
        '''将数据传入algorithems[i]里面。

        Arguments:
            i {[type]} -- [description]
            data {[type]} -- [description]
        '''
        self.algorithems[i].put(data)   # 通用方式 TODO 都把put变成data

    def algorithms_distribution(self, i,  data):
        '''算法行走流程

        Arguments:
            i {int} -- 当前算法的第几个阶段
            data {obj} -- 这个算法的数据
        '''

        if i >= len(self.algorithems):
            self.generater(data)
        else:
            data = self.build_data(i, data)
            # 这里判断是否已经不需要往后面走了
            if data != self.lucky_number:
                self.into_algorithems(i, data)
            else:
                self.generater(data)
    
    def run(self):
        '''开始运行，运行方式是监听每一个算法的返回，用线程的方式。
        '''
        def listen(index, algorithms_obj):
            while True:
                data = algorithms_obj.get()
                self.algorithms_distribution(index+1, data)
        for i in range(len(self.algorithems)):
            _thread.start_new_thread(list, self.algorithems[i])

        
            

    def add_algorithems(self, algorithms, processes=False):
        '''添加算法

        Arguments:
            algorithms {func} -- 执行算法的函数

        Keyword Arguments:
            processes {bool} -- 是否使用进程的方式 (default: {False})
        '''
        self.algorithems.append(algorithms)
