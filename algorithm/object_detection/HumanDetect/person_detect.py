from __future__ import division
import cv2
import time
import random
import pickle as pkl
from util import *
from darknet import Darknet
from preprocess import letterbox_image
from configs import confidence, nms_thresh, cfg, weights, reso


class PersonDetect(object):

    def __init__(self):

        print("Loading network.....")
        self.model = Darknet(cfg)
        self.model.load_weights(weights)
        print("Network successfully loaded")

        self.classes = load_classes('data/coco.names')
        self.colors = pkl.load(open("pallete", "rb"))


    def get_test_input(self, frame, input_dim, CUDA):

        img = cv2.resize(frame, (input_dim, input_dim))
        img_ = img[:, :, ::-1].transpose((2, 0, 1))
        img_ = img_[np.newaxis, :, :, :]/255.0
        img_ = torch.from_numpy(img_).float()
        img_ = Variable(img_)

        if CUDA:
            img_ = img_.cuda()

        return img_

    def prep_image(self, img, inp_dim):

        """
        Prepare image for inputting to the neural network.
        Returns a Variable
        """

        orig_im = img
        dim = orig_im.shape[1], orig_im.shape[0]
        img = (letterbox_image(orig_im, (inp_dim, inp_dim)))
        img_ = img[:, :, ::-1].transpose((2, 0, 1)).copy()
        img_ = torch.from_numpy(img_).float().div(255.0).unsqueeze(0)
        return img_, orig_im, dim

    def write(self, x, img, classes, colors):

        c1 = tuple(x[1:3].int())
        c2 = tuple(x[3:5].int())
        cls = int(x[-1])
        label = "{0}".format(classes[cls])
        if label == 'person':
            color = random.choice(colors)
            cv2.rectangle(img, c1, c2, color, 1)
            # one_point = (c1[0].item(), c1[1].item())
            # two_point = (c2[0].item(), c2[1].item())
            # person_acreage = abs(one_point[0]-two_point[0]) * abs(one_point[1]-two_point[1])
            return img
        else:
            None

    def detect_person(self, frame, cameraKey):

        """
        人体检测
        :param frame:  摄像头当前帧图片
        :param cameraKey:  摄像头编号
        :return: [
                    flag:  判断是否检测到人体，flag为True表示检测到人体，flag为False表示未检测到人体
                    orig_im:  摄像头当前帧图片
                    image_id:  用时间戳生成的图片编号
                    cameraKey:  摄像头编号
                 ]
        """

        flag = False
        image_id = ''

        CUDA = torch.cuda.is_available()
        num_classes = 80

        self.model.net_info["height"] = reso
        inp_dim = int(self.model.net_info["height"])
        assert inp_dim % 32 == 0
        assert inp_dim > 32

        if CUDA:
            self.model.cuda()

        img, orig_im, dim = self.prep_image(frame, inp_dim)
        im_dim = torch.FloatTensor(dim).repeat(1, 2)

        if CUDA:
            im_dim = im_dim.cuda()
            img = img.cuda()

        with torch.no_grad():
            output = self.model(Variable(img), CUDA)
        output = write_results(output, confidence, num_classes, nms=True, nms_conf=nms_thresh)

        im_dim = im_dim.repeat(output.size(0), 1)
        scaling_factor = torch.min(inp_dim / im_dim, 1)[0].view(-1, 1)

        output[:, [1, 3]] -= (inp_dim - scaling_factor * im_dim[:, 0].view(-1, 1)) / 2
        output[:, [2, 4]] -= (inp_dim - scaling_factor * im_dim[:, 1].view(-1, 1)) / 2

        output[:, 1:5] /= scaling_factor

        for i in range(output.shape[0]):
            output[i, [1, 3]] = torch.clamp(output[i, [1, 3]], 0.0, im_dim[i, 0])
            output[i, [2, 4]] = torch.clamp(output[i, [2, 4]], 0.0, im_dim[i, 1])

        person_matrix = []
        for i in range(output.shape[0]):
            detect_result = self.write(output[i], orig_im, self.classes, self.colors)
            if detect_result is not None:
                person_matrix.append(self.write(output[i], orig_im, self.classes, self.colors))

        if len(person_matrix) > 0:
            flag = True
            image_id = str(int(time.time()))

        return flag, orig_im, image_id, cameraKey


if __name__ == '__main__':
    cameraKey = ''
    person_detect = PersonDetect()
    frame = cv2.imread('person.jpg')
    person_detect.detect_person(frame, cameraKey)
    

