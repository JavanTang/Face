import cv2
import time
import tensorflow as tf
from algorithm.fire_detection.smoke_detection_core.core_function import single_frame_detect
from algorithm.fire_detection.train_and_detection.train_libs_auxiliary import get_model_and_hparams

class SmokeDetect(object):

    def __init__(self, flag, ckpt_dir):

        """
        初始化对象
        :param flag: 要使用哪个网络,值为'cnn3d'或‘cnn2d_lstm’  类型：str
        :param ckpt_dir:  模型所在路径  类型：str  示例：./summary/cnn3d_17  注意：记得改checkpoint中的路径
        """

        self.flag = flag
        self.ckpt_dir = ckpt_dir
        self.hparams, self.model = get_model_and_hparams(self.flag)

        cfg = tf.ConfigProto()
        cfg.gpu_options.allow_growth = True
        self.sess = tf.InteractiveSession(config=cfg)
        saver = tf.train.Saver(tf.global_variables())
        ckpt = tf.train.get_checkpoint_state(self.ckpt_dir)
        saver.restore(self.sess, ckpt.model_checkpoint_path)


    def detect(self, frame, frame_height, frame_width, block_threshold, cameraKey):

        """
        烟雾检测
        :param frame: 摄像头当前帧的图片
        :param frame_height: 摄像头当前帧的高  获取方式：cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        :param frame_width:  摄像头当前帧的宽  获取方式：cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        :param block_threshold:  判断烟雾检测的阈值, len(smoke_block)大于block_threshold时报警
        :return:[
                  flag: 是否报警的标志位, flag为True时报警, flag未False时不报警
                  frame: 摄像头当前帧的图片
                  cameraKey: 摄像头编号
                  image_id: 时间戳生成的图片编号
                ]
        """

        flag = False
        image_id = ''

        smoke_blocks = single_frame_detect(self.sess, self.model, frame, frame_height, frame_width)
        print(len(smoke_blocks))

        if len(smoke_blocks) > block_threshold:

            # 报警将标志位更新为True
            flag = True

            # 时间戳生成图片编号
            image_id = str(int(time.time()))

            return flag, frame, cameraKey, image_id
        else:
            return flag, frame, cameraKey, image_id


if __name__ == '__main__':

    sd = SmokeDetect('cnn3d', './summary/cnn3d_17')

    cap = cv2.VideoCapture('fire.mp4')
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    while True:
        frames = []
        res, frame = cap.read()
        if not res:
            break
        else:
            sd.detect(frame, height, width)
