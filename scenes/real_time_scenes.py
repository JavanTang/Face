import os 
import sys
current = os.path.dirname(__name__)
project = os.path.dirname(current)
sys.path.append(project)
from scenes import BaseEngineering


from processes.nodes.recorder import CameraReader


class RealTimeRecognition(BaseEngineering):
    def __init__(self):
        real_time = True
        super(RealTimeRecognition, self).__init__(real_time)
    def generater(self, data):
        print('1')

if __name__ == "__main__":
    rtr = RealTimeRecognition()
    camera = CameraReader()
    camera.init_node(['/home/tangzhifeng/Desktoavi'],[1],40,"123")
    camera.run()
    rtr.add_algorithems(camera)
    rtr.run()
    print(camera.get())
