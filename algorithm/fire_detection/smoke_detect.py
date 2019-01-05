import cv2
import time
import tensorflow as tf
from algorithm.fire_detection.smoke_detection_core.core_function import single_frame_detect
from algorithm.fire_detection.train_and_detection.train_libs_auxiliary import get_model_and_hparams


def detect(sess, model, frame, frame_height, frame_width, block_threshold, cameraKey):

    """
    烟雾检测
    :param sess: 加载ckpt模型的变量
    :param model: 根据使用哪种网络加载的模型网络
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

    smoke_blocks = single_frame_detect(sess, model, frame, frame_height, frame_width)
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

    netName = 'cnn3d'
    ckpt_dir = './summary/cnn3d_17'
    block_threshold = 10

    hparams, model = get_model_and_hparams(netName)

    cfg = tf.ConfigProto()
    cfg.gpu_options.allow_growth = True
    sess = tf.InteractiveSession(config=cfg)
    saver = tf.train.Saver(tf.global_variables())
    ckpt = tf.train.get_checkpoint_state(ckpt_dir)
    saver.restore(sess, ckpt.model_checkpoint_path)

    cap = cv2.VideoCapture('./fire.mp4')
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    while True:
        frames = []
        res, frame = cap.read()
        if not res:
            break
        else:
            flag, frame, cameraKey, image_id = detect(sess=sess,
                                                      model=model,
                                                      frame=frame,
                                                      frame_height=height,
                                                      frame_width=width,
                                                      block_threshold=block_threshold,
                                                      cameraKey='1')
