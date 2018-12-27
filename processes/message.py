"""
Define some data structure for muti-thread comunication.
"""
import time


class CameraMessage(object):
    """Wrap message transfer from CameraReader to Recognizer
    """

    def __init__(self, image, channel_id, tag):
        self.image = image
        self.channel_id = channel_id
        self.record_time = time.time()
        self.tag = tag
