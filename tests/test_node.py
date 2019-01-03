import sys
import os
import unittest
import time
import cv2

here = os.path.abspath(os.path.dirname(__file__))

# 将所要测试的源码路径放入path下面
source_path = os.path.join(here, '../')
sys.path.append(source_path)

from processes.nodes import recorder
from processes.nodes import recognizer
from processes.nodes import diff_node


class TestNode(unittest.TestCase):

    def test_reader(self):
        reader = recorder.CameraReader()
        reader.init_node([os.path.join(
            source_path, 'database/cache/video_friday/4.avi')], ['1'], 200, 'test')
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

        msg = recog.TOP(frame, '2', 'test')
        recog.put(msg)
        recog.set_test_option_on()
        recog.run()

        time.sleep(2)

        ret = recog.get()
        print(ret)

    def test_abnormal_detecter(self):
        abn_detecter = recognizer.AbnormalDetectionRecognizer()
        abn_detecter.init_node()

        for i in range(5):
            frame = cv2.imread(os.path.join(
                here, '../database/cache/test_picture.png'))
            msg = abn_detecter.TOP(frame, '2', 'test')
            abn_detecter.put(msg)

        abn_detecter.set_test_option_on()
        abn_detecter.run()

        time.sleep(5)

        while abn_detecter.q_out.qsize() > 0:
            msg = abn_detecter.get()
            print(msg)

    def test_frame_diff(self):
        differ = diff_node.FrameDiffNode()
        differ.init_node()

        for i in range(5):
            frame = cv2.imread(os.path.join(
                here, '../database/cache/test_picture.png'))
            msg = differ.TOP(frame, '2', 'test')
            differ.put(msg)

        differ.set_test_option_on()
        differ.run()

        time.sleep(5)
        assert differ.q_out.qsize() == 1
