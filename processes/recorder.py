import threading
import json
import os
import cv2
import time

from .message import CameraMessage as Message

class CameraReader(threading.Thread):

    def __init__(self, channel_ip, channel_id, read_fps_interval, queue, tag):
        """Init CameraReader

        Args:
            channel_ip (str): IP address to acess camera
            channel_id (int): Camera identity number
            read_fps_interval (float): How often do you read the camera.
            queue (Queue): FIFO queue
            tag (str): tag for this thread
        """
        super(CameraReader, self).__init__()
        self.channel_ip = channel_ip
        self.read_fps_interval = read_fps_interval
        self.channel_id = channel_id
        self.cap = None
        self.queue = queue
        self.tag = tag

    def run(self, max_times=-1):
        self.cap = cv2.VideoCapture(self.channel_ip)
        i = 0
        print("Camera Thread %d has been started" % self.channel_id)
        while True:
            if not self.cap.isOpened():
                self.cap.release()
                time.sleep(10)
                print('摄像头%d断开，正在重连。' % (self.channel_id))
                self.cap = cv2.VideoCapture(self.channel_ip)
            res, image = self.cap.read()
            if res == False:
                self.cap.release()
                print('摄像头%d异常，释放后重连' % self.channel_id)
                continue

            # Push frame in queue every "read_fps_interval" times.
            i += 1
            if i == self.read_fps_interval:
                if self.queue.qsize() > 3:

                    print("Queue Name %s" % self.tag,
                            self.queue.qsize())

                else:
                    message = Message(
                        image=image,
                        channel_id=self.channel_id
                    )
                    self.queue.put(message)

                i = 0
