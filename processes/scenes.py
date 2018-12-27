import unittest
import os
import sys
import numpy as np
import insightface
import db
import multiprocessing
import time

from .recognizer import RealTimeRecognizer, AbnormalRecognizer
from .recorder import CameraReader
from .queues import ProcessingQueue, RedisQueue

here = os.path.abspath(os.path.dirname(__file__))
thismodule = sys.modules[__name__]


def start_camera(camera_id_list,  # 摄像头id列表
                 camera_ip_list,   # 摄像头ip列表
                 read_fps_interval,  # 每隔多少帧读取一次摄像头
                 tag,  # 摄像头标识
                 queue  # 从摄像头读取图片的存储队列
                 ):

    tasks = []

    for i, ip in zip(camera_id_list, camera_ip_list):
        reader = CameraReader(
            ip, i, read_fps_interval, queue, tag)
        reader.start()
        tasks.append(reader)

    for t in tasks:
        t.join()


def start_recognizer(engine_name,  # 人脸识别引擎名称
                     face_database_path,  # 人脸库路径
                     minsize,  # 最小人脸像素
                     threshold,  # 人脸识别相似度阈值
                     recognizer_name,  # 进程类型名称
                     pool_limit_time,  # 最小识别间隔 （对于部分识别器有用）
                     tag,  # tag
                     camera_queue,  # 接收摄像头读取图片的队列
                     data_queue,  # 存储识别结果的队列
                     monitor_on,  # 是否开启监控模块
                     gpu_id):  # 使用那一块gpu

   # 获取人脸识别引擎对象
    engine = getattr(insightface, engine_name)(gpu_id=gpu_id)
    engine.load_database(face_database_path)

    if monitor_on:
        monitor_queue = db.Queue.get_by_name("RedisQueue", "monitor")
    else:
        monitor_queue = None

    recognizer = getattr(thismodule, recognizer_name)(engine=engine,
                                                      minsize=minsize,
                                                      threshold=threshold,
                                                      pool_limit_time=pool_limit_time,
                                                      shared_queue=camera_queue,
                                                      data_queue=data_queue,
                                                      tag=tag,
                                                      monitor_queue=monitor_queue)
    recognizer.run()


class ScenesClassRoom(object):

    def __init__(self, config):
        self.config = config
        
        # 准备进程池以及通讯队列
        self.pool = multiprocessing.Pool(self.config.p_algorithm_num + 1)
        self.camrea_queue = db.Queue.get_by_name("ProcessingQueue", self.config.tag + '_' + 'camera')
        self.data_queue = db.Queue.get_by_name("ProcessingQueue", self.config.tag + '_' + "data")


    def start(self):
        """
        启动整个模块
        """
        
        for _ in range(self.config.p_algorithm_num):
            self.pool.apply_async(start_recognizer, args=config.algorithm_params)

        # wait for recognizers ready
        time.sleep(10)

        self.pool.apply_async(start_camera, args=(camera_list, tag, camrea_queue))

        self.pool.close()