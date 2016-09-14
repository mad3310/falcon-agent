#coding=utf-8
from tornado.options import define, options
from tornado.ioloop import PeriodicCallback
from tornado.web import RequestHandler,HTTPError 
from tornado.gen import coroutine, Return
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest
from es_pack.resource import CommResource as es_res
import json
import time
import datetime
from concurrent.futures import ThreadPoolExecutor
from alarm_collect import MONITOR_INDEX_IN_ES
thread_pool = ThreadPoolExecutor(10)

@coroutine
def get_alarms(server_cluster, cluster_type):
    index = '%s-%s-%s' %(server_cluster,
                  cluster_type, MONITOR_INDEX_IN_ES)
    alarms = yield thread_pool.submit(
                    es_res.retireve_resource,
                    index, None, cluster_type,
                    120)
    raise Return(alarms) 
