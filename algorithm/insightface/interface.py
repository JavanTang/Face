"""
人脸识别接口
"""

import os
import glob
import numpy as np
import cv2
import mxnet as mx
import sys

from gluonnlp.embedding.evaluation import CosineSimilarity

here = os.path.abspath(os.path.dirname(__file__))

sys.path.append(here)
import deploy.face_model as face_model
from utils import load_dataset


class ModelParam(object):
    """初始化模型的一些参数
    """

    image_size = "112,112"
    model = os.path.join(
        here, 'models/model-r100-ii/model, 0')  # 预训练模型的保存路径
    ga_model = ''  # 性别年龄模型，在这里没有用到，为空
    gpu = 0  # gpu的id
    det = 0  # mtcnn option, 1 means using R+O, 0 means detect from begining
    flip = 0  # whether do lr flip aug
    threshold = 1.24  # ver dist threshold


class BaseEngine(object):
    """人脸识别引擎基类，提供模型初始化、提取特征向量的方法

    """

    def __init__(self, gpu_id=0):

        # 初始化模型的一些参数
        ModelParam.gpu = gpu_id
        self.model = face_model.FaceModel(ModelParam)
        self.database = None
        self.index2name = []
        self.feature_matrix = None

    def load_database(self, path, force_reload=False, save_intermediate_result=True):
        """加载人脸库

        Args:
            path (str): 人脸库文件夹的绝对路径。路径下每个人的照片保存到以名字命名的文件夹中, 图片以jpg的格式存储
            force_reload (bool, optional): Defaults to False. 是否强制重新加载
            save_intermediate_result (bool, optional): Defaults to False. 是否保存生成的向量到embedding_matrix.npy。保存生成的向量可以提高下次加载模型的速度
        """
        self.feature_matrix, self.index2name, _ = load_dataset(
            path, self.model, force_reload=force_reload, save_intermediate_result=save_intermediate_result)

        # 将特征矩阵库加载到MXnet
        self.feature_matrix = mx.nd.array(
            self.feature_matrix, ctx=mx.gpu(ModelParam.gpu))

    def get_detection(self, img):
        """人脸检测。从照片中获取检测到的人脸

        Args:
            img (np.array|str): 图片矩阵。可以是从视频中获取的帧|图片路径
        """
        # 如果传入的是图片路径，则从图片路径中加载图片
        if isinstance(img, str):
            img = cv2.imread(img)
        scaled_images, boxes, flag = self.model.get_input(img)

        return scaled_images, boxes, flag

    def recognize(self, scaled_images):
        """给定人脸图片集合，返回识别的姓名，概率和向量.
            需要在子类实现

        Args:
            scaled_images (list)): 人脸图片矩阵列表
        """

        raise NotImplementedError

    def detect_recognize(self, img, batch_size=5, p_threshold=-1, min_size=0):
        """人脸检测+识别

        Args:
            img (np.array|str): 图片矩阵。可以是从视频中获取的帧|图片路径
            batch_size (int): batch caculation in order to avoid "cuda out of memory" error.
            p_threshold (float): min probability for recognize.
            min_size (int): The detected face smaller than <min_size> will be filtered out.
        """
        scaled_images, boxes, flag = self.get_detection(img)

        # 什么都没检测到，返回空
        if not flag:
            return [], [], [], []

        original_face_image = list()
        boxes = boxes.astype(np.int32)

        # filter images that don't meet the requirement out.
        size_filter = []
        for i, b in enumerate(boxes):
            if b[3] - b[1] > min_size and b[2] - b[0] > min_size:
                size_filter.append(i)

        scaled_images = scaled_images[size_filter]
        boxes = boxes[size_filter]

        # 如果数据量过大，分batch防止显存溢出
        loop_num = (scaled_images.shape[0]-1)//batch_size + 1
        names, probabilities = [], []
        for i in range(loop_num):
            if (i+1) * batch_size > scaled_images.shape[0]:
                input_matrix = scaled_images[i*batch_size:]
            else:
                input_matrix = scaled_images[i*batch_size: (i+1)*batch_size]

            n, p = self.recognize(input_matrix)
            names.extend(n)
            probabilities.extend(p)

        # probablities filter
        probabilities = np.array(probabilities)
        p_filter = probabilities > p_threshold
        probabilities = probabilities[p_filter]
        boxes = boxes[p_filter]
        names = [n for n, flag in zip(names, p_filter) if flag]

        for box in boxes:
            original_face_image.append(img[box[1]: box[3], box[0]: box[2]])

        return original_face_image, names, probabilities, boxes

    def visualize(self, image, names, probabilities, boxes):
        for name, p, box in zip(names, probabilities, boxes):
            cv2.rectangle(image, (box[0], box[1]),
                          (box[2], box[3]), (255, 0, 0), 2)

            cv2.putText(image,'%s: %f' % (name, p),(box[0], box[3]), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),2,cv2.LINE_AA)

        return image

class CosineSimilarityEngine(BaseEngine):
    """通过余弦相似度进行人脸识别的引擎
    """

    def __init__(self):
        super(CosineSimilarityEngine, self).__init__()
        self.cos_op = CosineSimilarity()

    def recognize(self, scaled_images):
        """Hook implementation of super class
        """
        mx_image_tensor = self.model.get_feature_tensor(scaled_images)
        result = self._comput_cos_similarity(
            mx_image_tensor, self.feature_matrix)
        return result

    def _comput_cos_similarity(self, a, b):
        """计算两个矩阵每个向量间的余弦相似度，可能会显存溢出，推荐batch大小为10个

        Args:
            a (mx.NDArray):
            b (mx.NDArray): 
        """

        a_ = a.expand_dims(1).broadcast_axes(
            1, b.shape[0]).reshape(-1, a.shape[-1])
        b_ = b.expand_dims(0).broadcast_axes(
            0, a.shape[0]).reshape(-1, b.shape[-1])
        batch_similarities = self.cos_op(
            a_, b_).reshape(a.shape[0], b.shape[0])
        best_similarities = batch_similarities.max(1).asnumpy().tolist()
        best_index = batch_similarities.argmax(1).asnumpy().astype(np.int32)
        names = [self.index2name[i] for i in best_index]

        return names, best_similarities


class CosineVoteEngine(BaseEngine):
    """通过余弦相似度加投票的方法进行人脸识别

    Args:
        BaseEngine ([type]): [description]
    """

    def __init__(self, top=5):
        super(CosineVoteEngine, self).__init__()
        self.cos_op = CosineSimilarity()
        self.top = top

    def recognize(self, scaled_images):
        """Hook implementation of super class
        """
        mx_image_tensor = self.model.get_feature_tensor(scaled_images)
        names, probabilities = self._comput_cos_similarity(
            mx_image_tensor, self.feature_matrix)
        return names, probabilities

    def _comput_cos_similarity(self, a, b):
        """计算两个矩阵每个向量间的余弦相似度, 可能会显存溢出，推荐batch大小为10个

        Args:
            a (mx.NDArray):
            b (mx.NDArray): 
        """

        a_ = a.expand_dims(1).broadcast_axes(
            1, b.shape[0]).reshape(-1, a.shape[-1])
        b_ = b.expand_dims(0).broadcast_axes(
            0, a.shape[0]).reshape(-1, b.shape[-1])
        batch_similarities = self.cos_op(
            a_, b_).reshape(a.shape[0], b.shape[0])
        best_index = batch_similarities.topk(
            1, k=self.top).asnumpy().astype(np.int32)
        names = []
        probabilities = []

        for i, item in enumerate(best_index):
            tmp = dict()
            for index in item:
                name = self.index2name[index]
                if name in tmp:
                    tmp[name] += batch_similarities[i][index]
                else:
                    tmp[name] = batch_similarities[i][index]
            sorted_name = sorted(tmp.items(), key=lambda x: x[1], reverse=True)
            names.append(sorted_name[0][0])
            probabilities.append(sorted_name[0][1])

        return names, probabilities