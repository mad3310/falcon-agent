#coding=utf-8
from tornado.web import RequestHandler,HTTPError
from alarm_query import get_alarms
from sms import send_sms
from tornado.gen import coroutine, Return
import logging
from mail import MailEgine
from tornado.options import define, options
from sms import send_sms
from concurrent.futures import ThreadPoolExecutor
import json

thread_pool = ThreadPoolExecutor(10)

class AlarmsQueryHandler(RequestHandler):

    @coroutine
    def _alarm_parse(self, alarms, mailto,
                    subject, sms_to):
        if len(alarms) == 0:
            raise Return(0) 
        content = {} 
        for alarm in alarms:
            content, serious, general = {}, [], []
            node_name = alarm['node_name']
            if alarm['serious']:
                content['serious'] = alarm['serious']
            if alarm['general']:
                content['general'] = alarm['general']
            if content:
                _subject = '%s_%s' %(node_name, subject)
                status = yield thread_pool.submit(
                            MailEgine.send_exception_email,
                            options.mailfrom, mailto, _subject,
                            json.dumps(content))
                if status: 
                    yield send_sms(sms_to, json.dumps(content))

    @coroutine
    def get(self, server_cluster,
            cluster_type):
        ret = {}
        _mailto = self.get_argument('mailto','liujiniu <liujinliu@le.com>')
        mailto = _mailto.split(',')
        _sms_to = _mailto = self.get_argument('smsto','liujinliu:18201190271')
        sms_to = _sms_to.split(',')
        try:
            alarms = yield get_alarms(server_cluster,
                            cluster_type)
            yield self._alarm_parse(alarms, mailto,
                    'ALERT OF %s ON %s' %(cluster_type, server_cluster),
                    sms_to)
            ret['alarms'] = alarms
        except Exception as e:
            logging.error(e, exc_info=True)
            ret['alarms'] = 'agent failed'
        self.finish(ret)

