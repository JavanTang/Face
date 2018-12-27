import json
import tornado.web
import logging

# 基礎設定
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    handlers=[logging.FileHandler(os.path.abspath('.')+'/log/info', 'a+', 'utf-8'), ])

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

class BaseHandle(tornado.web.RequestHandler):

    # 覆盖这个函数用来确定当前用户
    def get_current_user(self):
        return self.get_secure_cookie("user")   #该函数用于查看是否验证 name 中的cookie

    def write_error(self,status_code,**kwargs):
        print(status_code)
        if status_code == 403 or 405:
            request = {
                'code':403,
                'msg':'对不起，你的参数提交有误。',
                'content':''
            }
            self.write(json.dumps(request,ensure_ascii=False))
        else:
            request = {
                'code':500,
                'msg':'',
                'content':''
            }
            self.write(json.dumps(request,ensure_ascii=False))