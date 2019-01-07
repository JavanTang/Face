'''
@Author: TangZhiFeng
@Data: 2019-01-06
@LastEditors: TangZhiFeng
@LastEditTime: 2019-01-07 18:18:04
@Description: 专注度识别
'''
import numpy as np
import time 

class Forcus(object):
    '''这是一个进程的专注度
    '''

    def __init__(self, camera2box, look):
        '''初始化
        
        Arguments:
            camera2box {dict} -- 多进程需要共享的dict
            look {进程锁} -- 多进程的LOOK
        '''

        self.camera2box = camera2box
        self.look = look

    def get_forcus(self, camera_id, names, points):
        '''获取专注度
        
        Arguments:
            camera_id {str} -- 设备id
            names {list} -- 识别人员id的list
            box {numpy.array} -- 人员的
        '''

        last = self.camera2box[camera_id]
        box = points.reshape(-1, 5, 2)
        # 这里是把数据进行更新
        updata = last
        for i in range(len(names)):
            name = names[i]
            # 这里会记录每一次的更新时间
            if name in updata:
                updata[name]['updata_time'] = time.time()
                updata[name]['box'] = box[i]    
            else:
                updata[name] = {}
                updata[name]['updata_time'] = time.time()
                updata[name]['box'] = box[i]
        # 更新的时候加上锁，确保进程安全
        self.look.acquire()
        self.camera2box[camera_id] = updata
        self.look.release()
        current = {name[i]:points[i] for i in range(len(names))}
        _result = self.__calculation(current,last, names)
        return _result

    def __point_distance(self, last_point, current_point):
        '''两点的距离

        Arguments:
            last_point {numpy} -- 上一次的所有点
            current_point {numpy} -- 当前的点

        Returns:
            int -- 两点的欧氏距离
        '''

        result = np.linalg.norm(last_point-current_point)
        print(result)
        return result

    def __calculation(self, current, last, names):
        _forcus = []
        for name in names:
            if name in last:
                box_current = current[name]
                box_last = last[name]
                current_mouth_eye_dis = self.__point_distance(
                    box_current[0], box_current[1]) + self.__point_distance(box_current[0], box_current[3])
                last_mouth_eye_dis = self.__point_distance(box_last[0], box_last[1]) + self.__point_distance(box_last[0], box_last[3])
                zoom = last_mouth_eye_dis / current_mouth_eye_dis
                point_point_dis = self.__point_distance(box_current * zoom, box_last)
                move_proportion = point_point_dis / last_mouth_eye_dis
                print('name:'+name+';focus:'+str(move_proportion))
                _forcus.append(move_proportion)
        # TODO 这里要把_forcus进行处理
        return _forcus