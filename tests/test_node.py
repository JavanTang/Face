import sys
import os
import unittest

here = os.path.abspath(os.path.dirname(__file__))

# 将所要测试的源码路径放入path下面
source_path = os.path.join(here, '../')
sys.path.append(source_path)

from processes.nodes import recorder


class TestNode(unittest.TestCase):

    def test_reader(self):
        reader = recorder.CameraReader()
        reader.init_node([os.path.join(source_path, 'database/cache/video_friday/4.avi')], [1], 200, 'test')
        reader.set_test_option_on()
        reader.run()

        for _ in range(5):
            ret = reader.get()
            print(ret)



if __name__ == "__main__":
    unittest.main()