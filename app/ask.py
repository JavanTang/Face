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
from tornado import gen
from app import BaseHandle
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor

from service_utils import clean_text
from service_utils import utils
from question_match import DialogueManager
import logging

# 基礎設定
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    handlers=[logging.FileHandler(os.path.abspath('.')+'/log/info', 'a+', 'utf-8'), ])

# 定義 handler 輸出 sys.stderr
console = logging.StreamHandler()
# 这里会输出的等级 https://docs.python.org/3/library/logging.html#levels
console.setLevel(logging.INFO)
# 設定輸出格式
# https://docs.python.org/3/library/logging.html#logging.Formatter
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
# handler 設定輸出格式
console.setFormatter(formatter)
# 加入 hander 到 root logger
logging.getLogger('').addHandler(console)
logger_nlu = logging.getLogger('交互日志')

store_info = {}


class ASK(BaseHandle):
    executor = ThreadPoolExecutor(20)

    @run_on_executor
    def run(self, question, unique_id):
        pass

        
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

