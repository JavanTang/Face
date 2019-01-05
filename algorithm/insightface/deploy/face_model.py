from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from scipy import misc
import sys
import os
import argparse
#import tensorflow as tf
import numpy as np
import mxnet as mx
import random
import cv2
import sklearn
import sklearn.preprocessing
from time import sleep
from deploy.mtcnn_detector import MtcnnDetector
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'common'))
import face_image
import face_preprocess
import time


def do_flip(data):
    for idx in xrange(data.shape[0]):
        data[idx, :, :] = np.fliplr(data[idx, :, :])


def get_model(ctx, image_size, model_str, layer):
    _vec = model_str.split(',')
    print(_vec)
    assert len(_vec) == 2
    prefix = _vec[0]
    epoch = int(_vec[1])
    print('loading', prefix, epoch)
    sym, arg_params, aux_params = mx.model.load_checkpoint(prefix, epoch)
    all_layers = sym.get_internals()
    sym = all_layers[layer+'_output']
    model = mx.mod.Module(symbol=sym, context=ctx, label_names=None)
    #model.bind(data_shapes=[('data', (args.batch_size, 3, image_size[0], image_size[1]))], label_shapes=[('softmax_label', (args.batch_size,))])
    model.bind(data_shapes=[('data', (1, 3, image_size[0], image_size[1]))])
    model.set_params(arg_params, aux_params)
    return model


class FaceModel:
    def __init__(self, args):
        self.args = args
        ctx = mx.gpu(args.gpu)
        self.ctx = ctx
        _vec = args.image_size.split(',')
        assert len(_vec) == 2
        image_size = (int(_vec[0]), int(_vec[1]))
        self.model = None
        self.ga_model = None
        if len(args.model) > 0:
            self.model = get_model(ctx, image_size, args.model, 'fc1')
        if len(args.ga_model) > 0:
            self.ga_model = get_model(ctx, image_size, args.ga_model, 'fc1')

        self.threshold = args.threshold
        self.det_minsize = 50
        self.det_threshold = [0.8, 0.8, 0.9]
        #self.det_factor = 0.9
        self.image_size = image_size
        mtcnn_path = os.path.join(os.path.dirname(__file__), 'mtcnn-model')
        if args.det == 0:
            detector = MtcnnDetector(model_folder=mtcnn_path, ctx=ctx, num_worker=1,
                                     accurate_landmark=True, threshold=self.det_threshold)
        else:
            detector = MtcnnDetector(model_folder=mtcnn_path, ctx=ctx,
                                     num_worker=1, accurate_landmark=True, threshold=[0.0, 0.0, 0.2])
        self.detector = detector

    @ staticmethod
    def get_aligned(face_image, bbox, points):
        num_face = bbox.shape[0]
        aligned = np.zeros((num_face, 3, 112, 112))
        points = points.T
        for i in range(num_face):
            nimg = face_preprocess.preprocess(
                face_image, bbox[i, 0:4], points[i, :].reshape((2, 5)).T, image_size='112,112')
            nimg = cv2.cvtColor(nimg, cv2.COLOR_BGR2RGB)
            aligned[i] = np.transpose(nimg, (2, 0, 1))
        return aligned

    def get_input(self, face_img):
        ret = self.detector.detect_face(face_img, det_type=self.args.det)
        flag = True
        if ret is None:
            flag = False
            return None, None, None, flag
        bbox, points = ret
        num_face = bbox.shape[0]
        aligned = np.zeros((num_face, 3, 112, 112))
        # cv2_aligned = np.zeros((num_face, 112, 3, 3))
        for i in range(num_face):

            nimg = face_preprocess.preprocess(
                face_img, bbox[i, 0:4], points[i, :].reshape((2, 5)).T, image_size='112,112')
            nimg = cv2.cvtColor(nimg, cv2.COLOR_BGR2RGB)
            aligned[i] = np.transpose(nimg, (2, 0, 1))
        return aligned, bbox, points, flag

    def get_feature_tensor(self, aligned):
        data = mx.nd.array(aligned, ctx=self.ctx)
        db = mx.io.DataBatch(data=(data,))
        self.model.forward(db, is_train=False)
        embedding = self.model.get_outputs()[0]
        return embedding

    def get_feature(self, aligned):
        data = mx.nd.array(aligned, ctx=self.ctx)
        db = mx.io.DataBatch(data=(data,))
        self.model.forward(db, is_train=False)
        embedding = self.model.get_outputs()[0].asnumpy()
        embedding = sklearn.preprocessing.normalize(embedding)
        return embedding

    def get_ga(self, aligned):
        input_blob = np.expand_dims(aligned, axis=0)
        data = mx.nd.array(input_blob)
        db = mx.io.DataBatch(data=(data,))
        self.ga_model.forward(db, is_train=False)
        ret = self.ga_model.get_outputs()[0].asnumpy()
        g = ret[:, 0:2].flatten()
        gender = np.argmax(g)
        a = ret[:, 2:202].reshape((100, 2))
        a = np.argmax(a, axis=1)
        age = int(sum(a))

        return gender, age
