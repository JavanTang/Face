import unittest
import os
import sys
import numpy as np
import multiprocessing
import time

here = os.path.abspath(os.path.dirname(__file__))
thismodule = sys.modules[__name__]

source_root = os.path.join(here, '..')
sys.path.append(source_root)
import algorithm.insightface as insightface

from processes import recognizer, recorder, queues
from utils.decorator import DebugPrintStackTrace


@DebugPrintStackTrace
def start_camera(recorder_name,  # recorder类型
                 camera_id_list,  # 摄像头id列表
                 camera_ip_list,   # 摄像头ip列表
                 read_fps_interval,  # 每隔多少帧读取一次摄像头
                 tag,  # 摄像头标识
                 queue  # 从摄像头读取图片的存储队列
                 ):
    
    print("Starting Camera.")
    tasks = []

    for i, ip in zip(camera_id_list, camera_ip_list):
        reader = getattr(recorder, 'CameraReader')(
            ip, i, read_fps_interval, queue, tag)
        reader.start()
        tasks.append(reader)

    for t in tasks:
        t.join()


@DebugPrintStackTrace
def start_recognizer(engine_name,  # 人脸识别引擎名称
                     face_database_path,  # 人脸库路径
                     minsize,  # 最小人脸像素
                     threshold,  # 人脸识别相似度阈值
                     recognizer_name,  # 进程类型名称
                     tag,  # tag
                     camera_queue,  # 接收摄像头读取图片的队列
                     data_queue,  # 存储识别结果的队列
                     monitor_on,  # 是否开启监控模块
                     gpu_id):  # 使用那一块gpu

    print("Starting Recognizer.")
   # 获取人脸识别引擎对象
    engine = getattr(insightface, engine_name)(gpu_id=gpu_id)
    engine.load_database(face_database_path)

    if monitor_on:
        monitor_queue = queues.Queue.get_by_name("RedisQueue", "monitor")
    else:
        monitor_queue = None

    recognizer = getattr(thismodule, recognizer_name)(engine=engine,
                                                      minsize=minsize,
                                                      threshold=threshold,
                                                      shared_queue=camera_queue,
                                                      data_queue=data_queue,
                                                      tag=tag,
                                                      monitor_queue=monitor_queue)
    recognizer.run()


class ScenesClassRoom(object):

    default_config = {
        'tag': 'class_room',

        # Algorithm config
        'p_algorithm_num': 1,
        'engine_name': 'CosineSimilarityEngine',
        'face_database_path': os.path.join(here, '../database/origin'),
        'minsize': 40,
        'threshold': 0.5,
        'recognizer_name': 'RealTimeRecognizer',
        'gpu_id': [0],
        'monitor_on': False,

        # Camera config
        'recorder_name': 'RecordOnRequest',
        'camera_id_list': [0],
        'camera_ip_list': [os.path.join(here, '../database/cache/video_friday/4.avi')],
        'read_fps_interval': 40,
    }

    def __init__(self, config={}):
        self.config = self.default_config.copy()
        self.config.update(config)

        # 准备进程池以及通讯队列
        self.pool = multiprocessing.Pool(self.config['p_algorithm_num'] + 1)
        self.camrea_queue = queues.Queue.get_by_name(
            "ProcessingQueue", self.config['tag'] + '_' + 'camera')
        self.data_queue = queues.Queue.get_by_name(
            "ProcessingQueue", self.config['tag'] + '_' + "data")

    def start(self):
        """
        启动整个模块
        """

        # 启动算法模块
        gpu_ids = self.config['gpu_id']
        for i in range(self.config['p_algorithm_num']):
            gpu_id = gpu_ids[i % len(gpu_ids)]
            self.pool.apply_async(start_recognizer, args=(
                self.config['engine_name'],
                self.config['face_database_path'],
                self.config['minsize'],
                self.config['threshold'],
                self.config['recognizer_name'],
                self.config['tag'],
                self.camrea_queue,
                self.data_queue,
                self.config['monitor_on'],
                gpu_id
            ))

        # wait for recognizers ready
        time.sleep(10)

        # 启动摄像头模块
        self.pool.apply_async(start_camera, args=(
            self.config['camera_id_list'],
            self.config['camera_ip_list'],
            self.config['read_fps_interval'],
            self.config['tag'],
            self.camrea_queue
        ))

        self.pool.close()
        self.pool.join()
