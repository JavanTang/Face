import sys
import os
import unittest
import time
import cv2

here = os.path.abspath(os.path.dirname(__file__))

# 将所要测试的源码路径放入path下面
source_path = os.path.join(here, '../')
sys.path.append(source_path)

from algorithm import fire_detection


class TestFireDetection(unittest.TestCase):

    def test_smoke_detection(self):
        sess, model = fire_detection.get_default_model()
        frame = os.path.join(here, '../database/cache/smoke.png')
        frame = cv2.imread(frame)
        flag, frame, cameraKey, image_id = fire_detection.detect(
            sess, model, frame, frame.shape[0], frame.shape[1], 10, '1')

        print(flag)
