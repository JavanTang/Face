"""Face Recognization threads with hook
"""

import time
import threading
from utils.decorator import UnitTestDecorator


@UnitTestDecorator
class BaseRecognizer(threading.Thread):

    def __init__(self,
                 engine,
                 minsize,
                 threshold,
                 shared_queue,
                 data_queue,
                 tag,
                 monitor_queue=None):

        super(BaseRecognizer, self).__init__()
        self.engine = engine
        self.minsize = minsize
        self.threshold = threshold
        self.queue = shared_queue
        self.data_queue = data_queue
        self.tag = tag
        if monitor_queue is not None:
            self.monitor_queue = monitor_queue
            self.monitor_on = True
        else:
            self.monitor_on = False
        

    def on_detect(self, channel_id, name):
        """
        当某个人脸符合条件时调用
        """
        raise NotImplementedError

    def run(self):
        print("Gate Thread has been started.")
        while True:
            # 如果当前模式为单元测试模式并且队列为空则程序返回， 此处不影响程序正常运行
            if self.get_test_option() and self.queue.qsize() == 0:
                break

            # Get the message from Queue
            msg = self.queue.get()

            frame, channel_id, img_time, tag = msg.image, msg.channel_id, msg.record_time, msg.tag

            # TODO 这里运行时间长汇出错，这里判断一下
            try:
                original_face_image, names, probabilities, boxes = self.engine.detect_recognize(
                    frame, p_threshold=self.threshold, min_size=self.minsize)

                if self.monitor_on and self.monitor_queue.qsize(channel_id) < 3:
                    processed_image = self.engine.visualize(frame, names, probabilities, boxes)
                    self.monitor_queue.put(processed_image, channel_id)
            except Exception:
                print("Recogize error. Camera id: %d." % channel_id)
                continue

            for _, name, _ in zip(original_face_image, names, probabilities):

                self.on_detect(channel_id, name)

            # 照片中没有人脸的时候不往队列里存储
            if len(names) > 0:

                params = {
                    "image_matrix": original_face_image,
                    'name': names,
                    'record_time': img_time,
                    'chanel_id': channel_id, 
                    'tag': tag
                }
                self.data_queue.put(params)



class RealTimeRecognizer(BaseRecognizer):

    def on_detect(self, channel_id, name):
        # 测试状况下不打印
        if not self.get_test_option():
            print("摄像头%d检测到%s" % (channel_id, name))
            

class AbnormalRecognizer(BaseRecognizer):

    pass
             