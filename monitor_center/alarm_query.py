#coding=utf-8
from tornado.options import define, options
from tornado.ioloop import PeriodicCallback
from tornado.web import RequestHandler,HTTPError
from tornado.gen import coroutine, Return
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
import json
import time
import datetime
from concurrent.futures import ThreadPoolExecutor
from alarm_collect import MONITOR_INDEX, ALARMS_CACHE
from mail import MailEgine

thread_pool = ThreadPoolExecutor(10)

@coroutine
def mail_egine_scan():
    yield thread_pool.submit(MailEgine.mail_scan_work)

def get_alarms(server_cluster, cluster_type):
    index = '%s-%s' %(server_cluster, MONITOR_INDEX)
    k = '%s-%s' %(index, cluster_type)
    alarms =  ALARMS_CACHE.get(k, {})
    return alarms


