import os
from app import BaseHandle
from service_utils import file_operation

class ShowDebug(BaseHandle):
    def get(self):
        '''
        结束问答
        '''
        self.write(file_operation.open_file(os.path.abspath('..')+'/log/info').decode('utf-8').replace('\n','<br>'))