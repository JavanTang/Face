'''
@Author: TangZhiFeng
@Data: 2019-01-05
@LastEditors: TangZhiFeng
@LastEditTime: 2019-01-05 21:22:15
@Description: 火焰检测——NODE
'''

import time
import os

from utils.decorator import UnitTestDecorator
from processes.message import CameraMessage
from processes.message import AbnormalDetectionMessage
from algorithm.fire_discover.interface import FireEngine
from . import BaseNode


@UnitTestDecorator
class FrameDiffNode(BaseNode):
    TOP = CameraMessage
    BOTTOM = AbnormalDetectionMessage

    def __init__(self, process_size=1, queue_type="ProcessingQueue"):
        super(FrameDiffNode, self).__init__(
            process_size, queue_type)

    def init_node(self):
        self.fire = FireEngine()
        self.fire.load_model()



    def _run_sigle_process(self, i):

        while(True):
            if self.get_test_option() and self.q_in.qsize() == 0:
                break
            msg_in = self.q_in.get()

            image = msg_in.image

            if self.q_out.qsize() > 4:
                print("%s bottom queue size is greater than 4." % self.__class__.__name__)
                continue
            result = self.fire.predict(image)
            
            if result is True:
                data = AbnormalDetectionMessage(
                    'flame',
                    True,
                    image,
                    str(time.time()),
                    msg_in.channel_id
                )
                self.q_out.put(data)