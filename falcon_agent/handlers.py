#coding=utf-8
from tornado.web import RequestHandler,HTTPError
from alarm_query import get_alarms
from sms import 
from tornado.gen import coroutine, Return import logging
from mail import MailEgine
from tornado.options import define, options
from sms import send_sms

thread_pool = ThreadPoolExecutor(10)

class AlarmsQueryHandler(RequestHandler):

    @coroutine
    def _alarm_parse(self, alarms, mailto,
                    subject, sms_to):
        if len(alarms) == 0:
            raise Return(0)
        serious, general = [], []
        for alarm in alarms:
            if alarms['serious'].has_key('timestamp'):
                del alarms['serious']['timestamp']
            if alarms['general'].has_key('timestamp'):
                del alarms['general']['timestamp']
            serious.append(alarms.get('serious',{}))
            general.append(alarms.get('general',{}))
        content = dict(serious = serious, general = general)
        status = yield thread_pool.submit(MailEgine.send_exception_email,
              options.mailfrom, mailto, subject, json.dumps(content))
        if status: 
            yield send_sms(sms_to, json.dumps(content))

    @coroutine
    def get(self, server_cluster,
            cluster_type):
        ret = {}
        _mailto = self.get_argument('mailto','liujinliu@le.com')
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

