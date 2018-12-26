import os

import tornado.httpserver as httpserver

from tornado import ioloop
from tornado.web import Application
from tornado.options import define
from tornado.log import enable_pretty_logging

from app import ask
from app import debug
def make_app():
    settings = {
        'cookie_secret':'asdfkljlkj2l382432lk',
        'debug':True,
        "login_url": "/api/v1/user/load"
    }
    application = Application([
        (r'/rtsident/',ask.ASK),
        (r'/writepermit/',debug.ShowDebug), # 显示调试信息
    ],**settings)
    http_server = httpserver.HTTPServer(application)
    http_server.listen(8888)
    ioloop.IOLoop.current().start()

def main():
    make_app()

if __name__ == '__main__':
    main()