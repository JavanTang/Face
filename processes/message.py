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

    def __str__(self):
        return "Image shape: %s\nChannel_id: %s\nRecord_time: %s\nTag: %s." % (self.image.shape, self.channel_id, self.record_time, self.tag)


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

    def __str__(self):
        return "Face number: %s\nNames: %s\nRecord_time: %s\nChannel_id: %s. Tag: %s." % (len(self.image_matrix), self.names, self.record_time, self.chanel_id, self.tag)


class AbnormalDetectionMessage(object):
    """Wrap message transfer from abnormal recognizer to root management node
    """

    def __init__(self,
                 abnormal_type,
                 flag,
                 base64_data,
                 image_id,
                 camera_key
                 ):
        self.abnormal_type = abnormal_type
        self.flag = flag
        self.base64_data = base64_data
        self.image_id = image_id
        self.camera_key = camera_key

    def __str__(self):
        return "Camera Key: %s detect %s situation. flag: %s." % (self.camera_key, self.abnormal_type, self.flag)
