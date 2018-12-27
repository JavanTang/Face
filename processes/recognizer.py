"""Face Recognization threads with hook
"""

import time
import threading


class BaseRecognizer(threading.Thread):

    def __init__(self,
                 engine,
                 minsize,
                 threshold,
                 pool_limit_time,
                 shared_queue,
                 data_queue,
                 tag,
                 monitor_queue=None):

        super(BaseRecognizer, self).__init__()
        self.engine = engine
        self.minsize = minsize
        self.threshold = threshold
        self.pool_limit_time = pool_limit_time
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

            # Get the message from Queue
            msg = self.queue.get()

            frame, channel_id, img_time = msg.image, msg.channel_id, msg.record_time

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

            for img, name, p in zip(original_face_image, names, probabilities):

                self.on_detect(channel_id, name)

                params = {
                    "image_matrix": img,
                    'name': name,
                    'record_time': img_time,
                    'chanel_id': channel_id, 
                    'tag': self.tag
                }
                self.data_queue.put(params)


class GateRecognizer(BaseRecognizer):
    def __init__(self, *args, **kwargs):
        super(GateRecognizer, self).__init__(*args, **kwargs)
        import serial
        self.serial = serial
        self.pool = dict()

    def on_detect(self, channel_id, name):

        if name in self.pool and time.time() - self.pool[name] < self.pool_limit_time:
            return True
        
        self.pool[name] = time.time()

        # 开闸机
        try:
            msg = self.open_door(channel_id)
        except Exception as e:
            print(e)
            return False
        if msg == 0:
            return False

        print("闸机%d开%s" % (channel_id, name))
        return True

    def open_door(self, cameraKey):
        ser = self.serial.Serial(port='/dev/ttyUSB0',
                            baudrate=9600,
                            bytesize=self.serial.EIGHTBITS,
                            parity=self.serial.PARITY_NONE,
                            stopbits=self.serial.STOPBITS_ONE,
                            timeout=0,
                            xonxoff=False,
                            rtscts=True,
                            writeTimeout=None,
                            dsrdtr=False,
                            interCharTimeout=None)
        

        if cameraKey == 0:
            ser.write(b'\xEB\x01\x41\x00\xAB')
        elif cameraKey == 1:
            ser.write(b'\xEB\x01\x40\x00\xAA')
        elif cameraKey == 2:
            ser.write(b'\xEB\x02\x41\x00\xA8')
        elif cameraKey == 3:
            ser.write(b'\xEB\x02\x40\x00\xA9')
        else:
            print('cameraKey error!')
        
        data = ''
        data = data.encode('utf-8')#由于串口使用的是字节，故而要进行转码，否则串口会不识别
        n = ser.inWaiting()
        if n: 
            #读取数据并将数据存入data
            data = data + ser.read(n)
            #输出接收到的数据
            print('get data from serial port:', data)
            #显示data的类型，便于如果出错时检查错误
            print(type(data))
        
        ser.close()
        msg = 1
        return msg

class FridayRecognizer(BaseRecognizer):

    def on_detect(self, channel_id, name):
        # print("摄像头%d检测到%s" % (channel_id, name))
        pass


class AbnormalRecognizer(BaseRecognizer):

    pass
             