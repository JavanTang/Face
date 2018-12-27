import threading


class Saver(threading.Thread):
    """Thread for save image to file system and database
    """

    def __init__(self, face_image_saver, queue):
        super(Saver, self).__init__()
        self.saver = face_image_saver
        self.queue = queue
        self.pool = dict()

    def run(self):
        print("Saver Thread has been started.")
        while(True):
            try:

                if self.queue.qsize() > 10:
                    print("Queue size of %s is greater than 10. %d." %
                        (self.__class__.__name__, self.queue.qsize()))

                params = self.queue.get()
                name = params.get('name')
                channel_id = params.get('chanel_id')
                print("摄像头%d检测到%s" % (channel_id, name))

                self.saver.save(**params)
            except Exception as e:
                print(e)
                continue
