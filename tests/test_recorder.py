import sys
import os
import unittest

here = os.path.abspath(os.path.dirname(__file__))

# 将所要测试的源码路径放入path下面
source_path = os.path.join(here, '../')
sys.path.append(source_path)

from processes.queues import ProcessingQueue, ThreadQueue
import processes.recorder as recorder
import processes.message as message


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

