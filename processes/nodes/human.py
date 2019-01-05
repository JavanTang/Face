from utils.decorator import UnitTestDecorator
from processes.message import HumanDetectionMessage

import pickle as pkl
from algorithm.object_detection.util import *
from algorithm.object_detection.darknet import Darknet
from algorithm.object_detection.person_detect import detect_person
from algorithm.object_detection.configs import cfg, weights

from . import BaseNode

@UnitTestDecorator
class HumanDetection(BaseNode):

    def init_node(self, class_model, pallete_model):
        """Init SmokeDetection

        Args:
            class_model (str): 模型是object_detection/data下的coco.names
            pallete_model (str): 模型是object_detection下的pallete
        """
        self.class_model = class_model
        self.pallete_model = pallete_model

    def _run_sigle_process(self, i):

        # 加载参数和模型
        print("Loading network.....")
        model = Darknet(cfg)
        model.load_weights(weights)
        print("Network successfully loaded")

        classes = load_classes('data/coco.names')
        colors = pkl.load(open("pallete", "rb"))

        while True:

            # Get the message from Queue
            msg = self.q_in.get()

            frame, channel_id, img_time, tag = msg.image, msg.channel_id, msg.record_time, msg.tag

            # 烟雾检测返回结果
            flag, frame, channel_id, image_id = detect_person(model=model,
                                                              frame=frame,
                                                              cameraKey=channel_id,
                                                              classes=classes,
                                                              colors=colors)
            # 如果flag为True, 表示检测到人体, 将结果存入队列
            if flag:
                msg = HumanDetectionMessage(flag=flag,
                                            image_matrix=frame,
                                            image_id=image_id,
                                            camera_key=channel_id)
                self.q_out.put(msg)
            else:
                continue

    def run(self):
        # 在新开的进程中使用线程运行
        super(HumanDetection, self).run(type='threading')
