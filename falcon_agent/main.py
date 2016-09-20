#coding=utf-8
import tornado.ioloop
from tornado.web import Application as TornadoWebApplication
from tornado.options import define, options
from es_pack.resource import CommResource as es_res
from routers import urls
from alarm_collect import write_all_mysql_alarms
from mail import MailEgine

define('debug', default=False, help='debug', type=bool)
define('es_host', default='10.154.255.131:9200',
        help = 'es host')
define('http_port', default=8000, help='http_port', type=int)
define('matrix', default='http://10.154.238.20:8080',
        help = 'matrix host')
define('smtp_host', default='10.205.91.22', help = 'smtp host')
define('smtp_port', default=587, help = 'smtp port')
define('smtp_user', default='mcluster', help = 'smtp user')
define('smtp_passwd', default='Mcl_20140903!', help = 'smtp pass')
define('mailfrom', default='mcluster@letv.com', help = 'mail from')

@coroutine
def mail_egine_scan():
    yield thread_pool.submit(MailEgine.mail_scan_work)

def main():
    tornado.options.parse_command_line()
    es_res.connect(options.es_host)
    MailEgine.egine_fire_start(options.smtp_host,
                    options.smtp_port,
                    options.smtp_user,
                    options.smtp_passwd,
                    interval=60)

    app = TornadoWebApplication(urls,
                debug=options.debug)
    app.listen(options.http_port)
    tornado.ioloop.PeriodicCallback(
        write_all_mysql_alarms,
        60000).start()
    tornado.ioloop.PeriodicCallback(
        mail_egine_scan,
        60000).start()
    tornado.ioloop.IOLoop.instance().start()

