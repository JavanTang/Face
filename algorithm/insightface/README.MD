# 基于MTCNN的人脸检测算法，基于ArcFace的人脸识别算法
本模块基于开源的mxnet实现： [insightface](https://github.com/deepinsight/insightface)

## 使用说明
根据计算人脸向量相似度算法的不同，该模块目前实现了三个Engine。


相关资料:
1. [python 进程共享变量](https://www.google.com/search?q=python+%E8%BF%9B%E7%A8%8B%E5%85%B1%E4%BA%AB%E5%8F%98%E9%87%8F&oq=%E8%BF%9B%E7%A8%8B%E5%85%B1%E4%BA%AB&aqs=chrome.1.69i57j0l5.4947j0j7&sourceid=chrome&ie=UTF-8)

##### CosineSimilarityEngine
使用暴力计算（brute force）。算法复杂度o(n*m)
```py
import cv2
from insightface import CosineSimilarityEngine



engine = CosineSimilarityEngine(gpu_id=0)
engine.load_database('../database/origin', True)

frame = cv2.imread('your_img.jpg')
original_face_image, names, probabilities, boxes, points = engine.detect_recognize(frame, p_threshold=self.threshold, min_size=self.minsize)
```

##### CosineVoteEngine
使用投票的方式计算最近的一个人脸。（数据集中每个人有多张人脸数据可以使用）算法复杂度o(n*m)

```py
import cv2
from insightface import CosineSimilarityEngine

engine = CosineSimilarityEngine(top=5, gpu_id=0)
engine.load_database('../database/origin', True)

frame = cv2.imread('your_img.jpg')
original_face_image, names, probabilities, boxes, points = engine.detect_recognize(frame, p_threshold=self.threshold, min_size=self.minsize)
```

##### NearestNeighborsEngine (待完成)
使用sklean基于ball_tree, kd_tree的算法计算最相近的人脸 平均算法复杂度 o(m*log(n))

## 其他功能
##### 可视化识别结果
将检测到的人脸和识别结果显示在图片上
```py
processed_image = engine.visualize(self, image, names, probabilities, boxes, points)  # image是原始图片， names、probabilities、boxes 是detect_recognize返回的结果
```
