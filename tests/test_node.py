import sys
import os
import unittest
import cv2

here = os.path.abspath(os.path.dirname(__file__))

# 将所要测试的源码路径放入path下面
source_path = os.path.join(here, '../')
sys.path.append(source_path)

from processes.nodes import recorder
from processes.nodes import recognizer
from processes.message import CameraMessage


class TestNode(unittest.TestCase):

    def test_reader(self):
        reader = recorder.CameraReader()
        reader.init_node([os.path.join(
            source_path, 'database/cache/video_friday/4.avi')], [1], 200, 'test')
        reader.set_test_option_on()
        reader.run()

        for _ in range(5):
            ret = reader.get()
            print(ret)

    def test_recognizer(self):

        recog = recognizer.RealTimeRecognizer(1)
        recog.init_node()
        frame = cv2.imread(os.path.join(
            here, '../database/cache/test_picture.png'))

        msg = CameraMessage(frame, 2, 'test')
        recog.put(msg)
        recog.set_test_option_on()
        recog.run()

        ret = recog.get()
        print(ret)

    def test_abnormal_detecter(self):
        pass


if __name__ == "__main__":
    unittest.main()
