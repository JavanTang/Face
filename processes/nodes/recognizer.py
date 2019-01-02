"""Face Recognization threads with hook
"""
import time
import os

from utils.decorator import UnitTestDecorator
from algorithm import insightface
from algorithm import abnormal_detection
from processes.message import RecognizerMessage, CameraMessage

from . import BaseNode


@UnitTestDecorator
class BaseRecognizer(BaseNode):

    def init_node(self,
                  engine_name,  # 人脸识别引擎名称
                  face_database_path,  # 人脸库路径
                  minsize,  # 最小人脸像素
                  threshold,  # 人脸识别相似度阈值
                  tag,  # tag
                  gpu_ids  # 可用的gpu编号
                  ):

        self.engine_name = engine_name
        self.face_database_path = face_database_path
        self.minsize = minsize
        self.threshold = threshold
        self.tag = tag
        self.gpu_ids = gpu_ids

    TOP = CameraMessage  # 上游节点需要传递的消息类
    BOTTOM = RecognizerMessage  # 下游节点需要传递的消息类

    def on_detect(self, channel_id, name):
        """
        当某个人脸符合条件时调用
        """
        raise NotImplementedError

    def _run_sigle_process(self, i):
        print("Recognization node has been started.")

        gpu_id = self.gpu_ids[i % len(self.gpu_ids)]
        engine = getattr(insightface, self.engine_name)(gpu_id=gpu_id)
        engine.load_database(self.face_database_path)

        while True:
            # 如果当前模式为单元测试模式并且队列为空则程序返回， 此处不影响程序正常运行
            if self.get_test_option() and self.q_in.qsize() == 0:
                break

            # Get the message from Queue
            msg = self.q_in.get()

            frame, channel_id, img_time, tag = msg.image, msg.channel_id, msg.record_time, msg.tag

            # TODO 这里运行时间长汇出错，这里判断一下
            try:
                original_face_image, names, probabilities, boxes = engine.detect_recognize(
                    frame, p_threshold=self.threshold, min_size=self.minsize)

            except Exception:
                print("Recogize error. Camera id: %d." % channel_id)
                continue

            for _, name, _ in zip(original_face_image, names, probabilities):

                self.on_detect(channel_id, name)

            # 照片中没有人脸的时候不往队列里存储
            if len(names) > 0:
                msg = RecognizerMessage(
                    original_face_image, names, img_time, channel_id, tag)
                self.q_out.put(msg)


source_root = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../..')


class RealTimeRecognizer(BaseRecognizer):

    default_params = {
        'engine_name': 'CosineSimilarityEngine',
        'face_database_path': os.path.join(source_root, 'database/origin'),
        'minsize': 40,
        'threshold': 0.5,
        'tag': "RealTimeRecognizer",
        'gpu_ids': [0]
    }

    def init_node(self, **kwargs):
        params = self.default_params.copy()
        params.update(kwargs)
        super(RealTimeRecognizer, self).init_node(**params)

    def on_detect(self, channel_id, name):
        # 测试状况下不打印
        if not self.get_test_option():
            print("摄像头%d检测到%s" % (channel_id, name))


class AbnormalDetectionRecognizer(BaseRecognizer):

    def _run_sigle_process(self, i):
        print("Recognization node has been started.")

        def detect_abnormal(cameraImg, box, emb_array, cameraKey):
            # 异常检测代码
            all_people = []
            for mini_index, mini_box in enumerate(box):
                each_person = list()
                first_appear_time = time.time()
                final_disappear_time = 0
                each_person.append(emb_array[mini_index])
                each_person.append(first_appear_time)
                each_person.append(final_disappear_time)
                each_person.append(
                    [mini_box[0], mini_box[1], mini_box[2], mini_box[3]])
                all_people.append(each_person)
            self.before_last_time = abnormal_detection.stay_detect(
                cameraImg, self.before_last_time, all_people, cameraKey)
            self.before_last_time_cluster = abnormal_detection.box_cluster(
                cameraImg, self.before_last_time_cluster, all_people, cameraKey)

        gpu_id = self.gpu_ids[i % len(self.gpu_ids)]
        engine = getattr(insightface, self.engine_name)(gpu_id=gpu_id)
        engine.load_database(self.face_database_path)

        while True:
            msg = self.q_in.get()
            frame, channel_id, _ = msg.image, msg.channel_id, msg.record_time
            try:
                scaled_images, boxes, flag = engine.model.get_input(frame)
                if not flag:
                    continue
                mx_image_tensor = engine.model.get_feature_tensor(
                    scaled_images)
                print("start detect abnormal")
                detect_abnormal(
                    frame, boxes, mx_image_tensor.asnumpy(), channel_id)
            except Exception as e:
                print(e)
                continue
