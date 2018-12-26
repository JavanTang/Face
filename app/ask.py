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
manager = DialogueManager()

store_info = {}

def request_node(url, remark, data='None', method='POST'):
    '''请求中间节点

    Arguments:
        url {str} -- 网站url
        data {json or dict} -- 请求数据 (default: {'None'})
        remark {str} -- 对请求的描述

    Keyword Arguments:
        method {str} -- 请求方式 (default: {'POST'})
    '''
    result = None
    start_time = time.time()
    try:
        logger_nlu.info('%s,%s->%s)，请求data的值为：%s' %
                        (remark, method, url, str(data)))
        if method == 'POST':
            result = requests.post(url, data=data)
        else:
            result = requests.get(url)

        end_time = time.time()
        logger_nlu.info('%s: %s，耗时：%d' %
                        (remark, result.text, int(end_time-start_time)))
    except Exception:
        logging.error('%s %s %s请求错误' % (remark, url, method))
    return result

def package(unique_id, waiting=None, fin=None, forwarding=None, complete=None, code=None, package=None):
    '''
    打包
    '''
    # 添加一些必要的字段
    user_id = store_info[unique_id]['id']
    tel = store_info[unique_id]['tel']
    city = store_info[unique_id]['city']
    call_tile = store_info[unique_id]['calltime']
    if package is None:
        _package = manager.get_pack(unique_id, tel)
    else:
        _package = package
    _package['tel'] = tel
    _package['city'] = city
    _package['id'] = user_id
    _package['calltime'] = call_tile
    if not waiting is None:
        _package['waiting'] = waiting
    if not fin is None:
        _package['fin'] = fin
    if not forwarding is None:
        _package['forwarding'] = forwarding
    if not complete is None:
        _package['complete'] = complete
    if not code is None:
        _package['status'] = code
    # 新鲜的补丁，之后这里可能有坑 TODO
    if len(_package['ask-stamp']) == 1 and len(_package['answer-stamp']) == 0 and _package['status'] == 7:
        _package['status'] = 6

    result = {'json': _package}
    json_result = json.dumps(result, ensure_ascii=False)
    result = request_node('http://47.98.140.93:9006/api/store/askAI?json=%s' %
                              json.dumps(_package, ensure_ascii=False),'打包操作',method='GET')
    return result.text


def ai_hang_up(unique_id, status):
    '''
    AI主动挂机
    '''
    def key_map(status):
        '''添加映射关系

        Arguments:
            status {int} -- 传入的状态码

        Returns:
            int -- 映射之后对应的cut_type
        '''

        if status in [2]:
            cut_type = 1
        if status in [1]:
            cut_type = 3
        if status in [4, 7]:
            cut_type = 2
        return cut_type
    start_time = time.time()
    cut_type = key_map(status)
    _package = manager.get_pack(unique_id, store_info[unique_id]['tel'])
    data = {
        'id': store_info[unique_id]['id'],
        'tel': store_info[unique_id]['tel'],
        'a_cut': utils.get_current_time_str(),
        'ask-content':json.dumps(_package['ask-content'],ensure_ascii=False),
        'answer-content':json.dumps(_package['answer-content'],ensure_ascii=False),
        'cut_type': cut_type
    }
    result = request_node('http://47.98.140.93:9006/api/aCut','AI主动挂机',data)
    result = result.text
    result = json.loads(result)
    
    if 'fin' in result:
        return package(unique_id, fin=result['fin'], complete=result['complete'],package = _package)
    else:
        if result['cut_type'] is '2':
            if status == 4:
                return package(unique_id, code=4, package = _package)
            if status == 7:
                return package(unique_id, code=2, package = _package)
        return package(unique_id,package=_package)


def ai_forwarding(unique_id):
    '''
    转人工
    '''
    start_time = time.time()
    data = {
        'id': store_info[unique_id]['id'],
        'tel': store_info[unique_id]['tel'],
        'forwarding': utils.get_current_time_str(),
    }
    result = request_node('http://47.98.140.93:9006/api/forwarding','转人工操作',data)
    result = json.loads(result.text)
    package(unique_id, waiting=result['waiting'],
            forwarding=data['forwarding'])


class ASK(BaseHandle):
    '''
    表 9:转发节点后台向 AI 处理后台转发的问答数据格式,同表 3
    {
    build:sha2(48),
    ask:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    }
    '''
    executor = ThreadPoolExecutor(20)

    @run_on_executor
    def run(self, question, unique_id):
        response = manager.chat(question, unique_id)
        status_code = int(manager.get_status_code(unique_id))
        logger_nlu.info('传入参数： status_code->%d   question->%s' %
                        (status_code, question))
        if status_code in [1, 4, 7]:
            ai_hang_up(unique_id, status_code)
        if status_code in [3, 5]:
            ai_forwarding(unique_id)
        response = {'build': unique_id, 'answer': response,
                    'id': store_info[unique_id]['id']}
        return response

    @gen.coroutine
    def post(self):
        '''
        开始问答
        '''
        question = self.get_argument('ask')
        unique_id = self.get_argument('build')
        logger_nlu.info('ASK')
        response = yield self.run(question, unique_id)
        logger_nlu.info(response)
        self.write(json.dumps(response, ensure_ascii=False))

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Headers", "content-type")
        self.set_header("Access-Control-Allow-Methods", "POST,GET,OPTIONS")


class EstablishConnection(BaseHandle):
    '''
    建立连接，对应表 7:转发节点后台向 AI 处理后台转发的“建立 AI 服务请求”数据格式
    '''

    def test(self, paramter_id):
        test_result = {'id': paramter_id, 'build': utils.generate_sha48(
            (str(time.time())+'AI')[:48].encode()), 'complete': utils.get_current_time_str()}
        return json.dumps(test_result, ensure_ascii=False)

    def post(self):
        # 11-23号修改文档
        paramter_id = self.get_argument("id")
        paramter_tel = self.get_argument("tel")
        paramter_city = self.get_argument("city")
        # 十一月二十六号 多加一个字段 calltime，需要在打包的时候将这个字段加入进去
        paramter_calltime = self.get_argument("calltime")

        build = utils.generate_sha48((str(time.time())+'AI').encode())[:48]
        build_time = utils.get_current_time_str()

        store_info[build] = {'id': paramter_id,
                             'tel': paramter_tel, 'city': paramter_city, 'calltime': paramter_calltime}
        ask = manager.chat('万年不变第一条请求', build)

        response = {
            'id': paramter_id,
            'tel': paramter_tel,
            'city': paramter_city,
            'build': build,
            'build-time': build_time,
            'ask': ask,
        }
        response = json.dumps(response, ensure_ascii=False)

        logger_nlu.info('EstablishConnection')
        logger_nlu.info(response)
        self.write(response)

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Headers", "content-type")
        self.set_header("Access-Control-Allow-Methods", "POST,GET,OPTIONS")


class HangUp(BaseHandle):
    '''
    用户挂机操作
    表 11:转发节点向 AI 处理后台转发的问答流程中挂机通知,同表 5
    '''

    def post(self):
        paramter_id = self.get_argument("id")
        paramter_tel = self.get_argument("tel")
        paramter_u_cut = self.get_argument("u_cut")
        # 寻找id，强制符合文档,后期维护有问题 TODO
        for k, v in store_info.items():
            if paramter_id == v['id']:
                paramter_id = k
                break

        manager.hang_up(paramter_id)
        package(paramter_id, code=7)
        # 由 APP 后台发出，给转发节点，转发节点收到后给 200；  所以这里不用返回

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Headers", "content-type")
        self.set_header("Access-Control-Allow-Methods", "POST,GET,OPTIONS")
