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


class RecognizerMessage(object):

    """
    Wrap message transfer from recognizer to root management node
    """

    def __init__(self,
                 image_matrix,
                 names,
                 record_time,
                 chanel_id,
                 tag
                 ):
        self.image_matrix = image_matrix
        self.names = names
        self.record_time = record_time
        self.chanel_id = chanel_id
        self.tag = tag
