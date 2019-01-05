import tensorflow as tf

from utils.decorator import UnitTestDecorator

from algorithm.fire_detection.smoke_detect import detect
from processes.message import AbnormalDetectionMessage
from algorithm.fire_detection.train_and_detection.train_libs_auxiliary import get_model_and_hparams

from . import BaseNode

@UnitTestDecorator
class SmokeDetection(BaseNode):


    def init_node(self, netName, ckpt_dir, block_threshold):
        """Init SmokeDetection

        Args:
            netName (str): 要使用哪个网络,值为'cnn3d'或'cnn2d_lstm'
            ckpt_dir (str): 模型所在路径  注意：记得改checkpoint中的路径
            block_threshold (int): 如果烟雾块大于block_threshold, 报警
        """
        self.netName = netName
        self.ckpt_dir = ckpt_dir
        self.block_threshold = block_threshold


    def _run_sigle_process(self, i):

        # 加载参数和模型
        hparams, model = get_model_and_hparams(self.netName)

        cfg = tf.ConfigProto()
        cfg.gpu_options.allow_growth = True
        sess = tf.InteractiveSession(config=cfg)
        saver = tf.train.Saver(tf.global_variables())
        ckpt = tf.train.get_checkpoint_state(self.ckpt_dir)
        saver.restore(sess, ckpt.model_checkpoint_path)

        while True:

            # Get the message from Queue
            msg = self.q_in.get()

            frame, channel_id, img_time, tag = msg.image, msg.channel_id, msg.record_time, msg.tag

            # 烟雾检测返回结果
            flag, frame, channel_id, image_id = detect(sess=sess,
                                                       model=model,
                                                       frame_height=frame.shape()[0],
                                                       frame_width=frame.shape()[1],
                                                       block_threshold=self.block_threshold,
                                                       cameraKey=channel_id)
            # 如果flag为True, 表示检测到烟雾, 将结果存入队列
            if flag:
                msg = AbnormalDetectionMessage(abnormal_type='smoke',
                                               flag=flag,
                                               base64_data=frame,
                                               image_id=image_id,
                                               camera_key=channel_id)
                self.q_out.put(msg)
            else:
                continue

    def run(self):
        # 在新开的进程中使用线程运行
        super(SmokeDetection, self).run(type='threading')
