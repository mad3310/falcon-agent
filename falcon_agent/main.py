#coding=utf-8
import tornado.ioloop
from tornado.web import Application as TornadoWebApplication
from tornado.options import define, options
from es_pack.resource import CommResource as es_res
from routers import urls
from alarm_collect import write_all_mysql_alarms

define('debug', default=False, help='debug', type=bool)
define('es_host', default='10.154.255.131:9200',
        help = 'es host')
define('http_port', default=8000, help='http_port', type=int)
define('matrix', default='http://10.154.238.20:8082',
        help = 'matrix host')

def main():
    tornado.options.parse_command_line()
    es_res.connect(options.es_host)
    app = TornadoWebApplication(urls,
                debug=options.debug)
    app.listen(options.http_port)
    tornado.ioloop.PeriodicCallback(
        write_all_mysql_alarms,
        12000).start()
    tornado.ioloop.IOLoop.instance().start()

