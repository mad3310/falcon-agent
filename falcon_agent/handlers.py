#coding=utf-8
from tornado.web import RequestHandler,HTTPError
from alarm_query import get_alarms
from tornado.gen import coroutine, Return
import logging

class AlarmsQueryHandler(RequestHandler):

    @coroutine
    def get(self, server_cluster):
        ret = {}
        try:
            alarms = yield get_alarms(server_cluster)
            ret['alarms'] = alarms
        except Exception as e:
            logging.error(e, exc_info=True)
            ret['alarms'] = 'agent failed'
        self.finish(ret)

