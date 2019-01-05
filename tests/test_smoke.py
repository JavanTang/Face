import cv2

from algorithm.fire_detection.smoke_detect import detect, get_default_model


class TestFireDetection(object):

    @staticmethod
    def test_smoke_detection():

        print('9999')

        sess, model = get_default_model()

        print('3333')
        cap = cv2.VideoCapture('../algorithm/fire_detection/fire.mp4')

        while True:
            res, frame = cap.read()

            if not res:
                break
            print(res)
            # frame = os.path.join(here, '../database/cache/smoke.png')
            # frame = cv2.imread(frame)

            flag, frame, cameraKey, image_id = detect(
                sess, model, frame, frame.shape[0], frame.shape[1], 10, '1')

            print(flag)


if __name__ == '__main__':
    TestFireDetection.test_smoke_detection()
