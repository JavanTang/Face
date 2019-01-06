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
from processes.nodes import smoke
from processes.nodes import human


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

    def test_stranger_recognizer(self):
        recog = recognizer.RealTimeStrangerRecognizer(1)
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

    def test_smoke(self):
        # TODO test fail.
        smoke_detector = smoke.SmokeDetection(1)
        smoke_detector.init_node(10)
        for i in range(5):
            frame = cv2.imread(os.path.join(
                here, '../database/cache/smoke.png'))
            msg = smoke_detector.TOP(frame, '2', 'test')
            smoke_detector.put(msg)

        smoke_detector.set_test_option_on()
        smoke_detector._run_sigle_process(0)

        print(smoke_detector.q_out.qsize())

    def test_people_detection(self):

        print(123123)
        people_detector = human.HumanDetection(1)
        people_detector.init_node()
        for i in range(5):
            frame = cv2.imread(os.path.join(
                here, '../database/cache/person.jpg'))
            msg = people_detector.TOP(frame, '2', 'test')
            people_detector.put(msg)

        people_detector.set_test_option_on()
        people_detector._run_sigle_process(0)

        assert people_detector.q_out.qsize() == 5
