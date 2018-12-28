import sys
import os
import unittest

here = os.path.abspath(os.path.dirname(__file__))

# 将所要测试的源码路径放入path下面
source_path = os.path.join(here, '../')
sys.path.append(source_path)

from processes.queues import ProcessingQueue
import processes.recognizer as recognizer
import processes.recorder as recorder
import processes.message as message


class TestEngine(object):
    """模拟人脸识别节点测试Recognizer
    """

    def detect_recognize(self, frame, p_threshold, min_size):
        return [1], [1], [1], [1]

    def visualize(self, frame, names, probabilities, boxes):

        return [1]


class TestRecognizer(unittest.TestCase):

    def test_realtime_recognizer(self):
        """recognizer.RealTimeRecognizer 的测试用例
        """

        engine = TestEngine()
        minsize = [40]
        threshold = 0.5
        camera_queue = ProcessingQueue('test')
        data_queue = ProcessingQueue('test')
        tag = 'test'

        # 准备一些假数据
        for _ in range(10):
            camera_queue.put(message.CameraMessage(1, 2, 'test'))

        # 测试开始
        re = recognizer.RealTimeRecognizer(
            engine, minsize, threshold, camera_queue, data_queue, tag)
        re.set_test_option_on()
        re.run()

        while data_queue.qsize() != 0:
            data = data_queue.get()
            assert "image_matrix" in data
            assert "name" in data
            assert "record_time" in data
            assert "chanel_id" in data
            assert "tag" in data



class TestRecorder(unittest.TestCase):

    def setUp(self):
        self.test_camera = os.path.join(
            here, '../database/cache/test_video.mp4')  # 这里用视频代替摄像头

    def test_camera_reader(self):
        """
        recorder.CameraRecorder 的测试用例
        """
        
        camera_queue = ProcessingQueue('test')
        reader = recorder.CameraReader(
            self.test_camera, 1, 10, camera_queue, 'test')
        reader.set_test_option_on()

        reader.run()

        while camera_queue.qsize() != 0:
            obj = camera_queue.get()
            assert isinstance(obj, message.CameraMessage)
            