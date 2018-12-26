import unittest
import os
import sys
import numpy as np
import insightface
import db
import multiprocessing
import time

from .recognizer import FridayRecognizer, GateRecognizer, AbnormalRecognizer
from .recorder import CameraReader

here = os.path.abspath(os.path.dirname(__file__))
thismodule = sys.modules[__name__]


def start_camera(camera_list,
                 tag,
                 queue):

    tasks = []

    for i in camera_list:
        reader = CameraReader(
            config.cameras[i], i, getattr(config, tag+'_fps_interval'), queue, tag)
        reader.start()
        tasks.append(reader)

    for t in tasks:
        t.join()


def start_recognizer(engine_name,  # 人脸识别引擎名称
                     recognizer_name,  # 进程类型名称
                     tag,  # tag
                     camera_queue,  # 接收摄像头读取图片的队列
                     data_queue,  # 存储识别结果的队列
                     monitor_on,  # 是否开启监控模块
                     gpu_id):  # 使用那一块gpu

   # 获取人脸识别引擎对象
    engine = getattr(insightface, engine_name)(gpu_id=gpu_id)
    engine.load_database(config.face_database_path,
                         config.force_reload_dataset)

    if monitor_on:
        monitor_queue = db.Queue.get_by_name("RedisQueue", "monitor")
    else:
        monitor_queue = None

    recognizer = getattr(thismodule, recognizer_name)(engine=engine,
                                                      minsize=getattr(
                                                          config, tag+'_min_size'),
                                                      threshold=getattr(
                                                          config, tag+'_threshold'),
                                                      pool_limit_time=getattr(
                                                          config, tag+'_pool_limit_time'),
                                                      shared_queue=camera_queue,
                                                      data_queue=data_queue,
                                                      tag=tag,
                                                      monitor_queue=monitor_queue)
    recognizer.run()
