'''
@Author: TangZhiFeng
@Data: 2019-01-04 
@LastEditors: TangZhiFeng
@LastEditTime: 2019-01-04 15:12:32
@Description: 大门异常检测
'''

import os
import sys
import json

current = os.path.dirname(__name__)
project = os.path.dirname(os.path.dirname(current))
sys.path.append(project)
from utils.image_base64 import array_to_file
from processes.nodes.diff_node import FrameDiffNode
from processes.nodes.recorder import CameraReader
from scenes import BaseEngineering, BaseScenesManage
from processes.nodes.recognizer import RealTimeRecognizer
from utils.time_utils import genera_stamp
from utils.socket_client import client
from utils.upload_image import batch_people_upload
from processes.nodes.recognizer import AbnormalDetectionRecognizer

class AbnormalSchoolGateEngineering(BaseEngineering):
    '''实时检测学校出入大门异常情况
    '''

    def __init__(self):
        real_time = True
        super(AbnormalSchoolGateEngineering, self).__init__(real_time)

    def build_data(self, i, data):
        return data

    def generater(self, data):
        '''返回示例{
            type:x
                //识别数据类型,1 为人员检测结果,非 1 为场景异常结果
                data:{
                    camera_id:xxxx,
                    //识别摄像头 id
                    scenario_id:xxx,
                    //场所 id
                    image_id:xxxxx ,
                    //图片识别时间戳
                    rule_id:xxxx
                    //匹配的异常规则
                }
            }
            
        Arguments:
            data {[obj]} -- 对象中含有我需要的数据,stay_too_long逗留，cluster聚集
        '''
        result = {
            'type': 1,
            'data': {},
            'stamp': genera_stamp(),
            'scene': 103  
        }
        result['data']['camera_id'] = data.chanel_id
        result['data']['scenario_id'] = data.chanel_id
        result['data']['recognition'] = data.names
        result['data']['stranger'] = []
        path = array_to_file(data.image_matrix, data.names)
        batch_people_upload(path,data.chanel_id,data.names,result['stamp'])
        client.send(json.dumps(result, ensure_ascii=False))


class RealTimeSchoolGateScene(BaseScenesManage):
    '''实时校门检测
    '''

    def init_node(self):
        camera = CameraReader()
        realtime_abnormal = AbnormalDetectionRecognizer()
        diff = FrameDiffNode(1)
        diff.init_node()
        camera.init_node(
            ['rtsp://admin:admin12345@192.168.0.141:554/Streaming/Channels/101'], [1], 10, "123")
        realtime_abnormal.init_node()
        
        self.nodes.append(camera)
        self.nodes.append(diff)
        self.nodes.append(realtime_abnormal)
        self.manage = AbnormalSchoolGateEngineering()
        



if __name__ == "__main__":
    rt_scene = RealTimeSchoolGateScene()
    rt_scene.start()
