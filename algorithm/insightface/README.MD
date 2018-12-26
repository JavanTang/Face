# 人脸对比

**FaceComtrast对象**

初始化：

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

