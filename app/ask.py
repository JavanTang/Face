'''
@Author:    唐志峰
@Function:  2018/3/19
'''
import datetime
import json
import time
import requests
import tornado
import hashlib
import os
import sys
from tornado import gen
from app import BaseHandle
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor

current = os.path.dirname(__name__)
sys.path.append(os.path.dirname(current))

from exception.write_permit_exception import 

logger_nlu = logging.getLogger('交互日志')

class WritePermit(BaseHandle):
    '''实时识别继续写入.
    
    Arguments:
        BaseHandle {BaseHandle} -- 面部识别的基类 
    '''

    executor = ThreadPoolExecutor(20)

    @run_on_executor
    def run(self, queue, code):
        if code == 1:
            # TODO 在这里改变算法是否需要继续写入
        else:
            return write_permit_exception.WritePermiteCodeError('Code not equal 1')

    @gen.coroutine
    def post(self):
        
        pass

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Headers", "content-type")
        self.set_header("Access-Control-Allow-Methods", "POST,GET,OPTIONS")


class EstablishConnection(BaseHandle):
    def post(self):
        pass

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Headers", "content-type")
        self.set_header("Access-Control-Allow-Methods", "POST,GET,OPTIONS")

