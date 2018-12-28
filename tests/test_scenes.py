import sys
import os
import unittest

here = os.path.abspath(os.path.dirname(__file__))

# 将所要测试的源码路径放入path下面
source_path = os.path.join(here, '../')
sys.path.append(source_path)

import scenes


class TestScenes(unittest.TestCase):

    def test_classroom_scene(self):
        pass
