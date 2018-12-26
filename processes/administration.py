'''
@Author: TangZhiFeng
@Data: 2018-12-26
@LastEditors: TangZhiFeng
@LastEditTime: 2018-12-26 18:20:02
@Description: 识别算法的控制模块
'''
import threading


class Administration(threading.Thread):
    '''识别人脸算法控制中心
    '''

    def __init__(self, back_func, queue):
        '''初始化控制中心
        
        Arguments:
            back_func {func} -- 回调函数,这里需要result是识别的学号list,camera_id是设备编号.
            queue {queue} -- 队列 
        '''
        super(Administration, self).__init__()
        self.back_func = back_func
        self.queue = queue

    def run(self):
        '''运行线程
        '''

        print("Administration Thread has been started.")
        while(True):
            try:
                if self.queue.qsize() > 10:
                    print("Queue size of %s is greater than 10. %d." %
                        (self.__class__.__name__, self.queue.qsize()))
                params = self.queue.get()
                result = params.get('result')
                camera_id = params.get('camera_id')
                self.back_func(result=result,camera_id=camera_id)
            except Exception as e:
                print(e)
                continue
