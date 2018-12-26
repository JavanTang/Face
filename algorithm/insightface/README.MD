# 基于MTCNN的人脸检测算法，基于ArcFace的人脸识别算法
本模块基于开源的mxnet实现： [insightface](https://github.com/deepinsight/insightface)

## 使用说明
根据计算人脸向量相似度算法的不同，该模块目前实现了三个Engine。

## 模块说明
1. 摄像头的映射关系. (list:哪些摄像头需要进行人脸对比)
2. 是否实时识别.(默认为False)
3. 触发的回调函数.(函数包含的内容:{result:[人员1,人员2,人员n...],camera_id:xxx,scene:2}),在实时识别为False的情况下,可以把回调函数设置为None.

函数方法:

1. 设置是否支持实时识别.
2. 添加摄像头.
3. 减少摄像头.
4. 处理一帧的数据,并将数据放入redis,在这里要判断是否可以放入redis.
5. 暂停放入redis.
6. 允许放入redis.

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
original_face_image, names, probabilities, boxes = engine.detect_recognize(frame, p_threshold=self.threshold, min_size=self.minsize)
```

##### CosineVoteEngine
使用投票的方式计算最近的一个人脸。（数据集中每个人有多张人脸数据可以使用）算法复杂度o(n*m)

```py
import cv2
from insightface import CosineSimilarityEngine

engine = CosineSimilarityEngine(top=5, gpu_id=0)
engine.load_database('../database/origin', True)

frame = cv2.imread('your_img.jpg')
original_face_image, names, probabilities, boxes = engine.detect_recognize(frame, p_threshold=self.threshold, min_size=self.minsize)
```

##### NearestNeighborsEngine (待完成)
使用sklean基于ball_tree, kd_tree的算法计算最相近的人脸 平均算法复杂度 o(m*log(n))

## 其他功能
##### 可视化识别结果
将检测到的人脸和识别结果显示在图片上
```py
processed_image = engine.visualize(self, image, names, probabilities, boxes)  # image是原始图片， names、probabilities、boxes 是detect_recognize返回的结果
```
