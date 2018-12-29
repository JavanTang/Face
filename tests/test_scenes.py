import sys
import os
import unittest

here = os.path.abspath(os.path.dirname(__file__))

# 将所要测试的源码路径放入path下面
source_path = os.path.join(here, '../')
sys.path.append(source_path)

import scenes


class TestScenes(unittest.TestCase):

    def test_realtime_fr_scene(self):
        """测试实时场景下的识别
        """
        # 使用默认参数测试实时人脸识别场景
        s = scenes.ScenesRealTimeFaceRecognization()
        s.start()


if __name__ == "__main__":
    unittest.main()    