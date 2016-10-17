#coding = utf-8
from tornado.httpclient import AsyncHTTPClient
import json
from tornado.gen import coroutine, Return
import urllib

URL = 'http://10.185.30.240:8888/alarm/api/addTask?token=0115e72e386b969613560ce15124d75a'

@coroutine
def send_sms(mobiles, content):
    receive_user_list = []
    http_client = AsyncHTTPClient()
    for users in mobiles:
        info_list = users.split(':')
        _receive = dict(username = info_list[0],
                        mobile = info_list[1])
        receive_user_list.append(_receive)
    _content = dict(data = content)
    _detail = dict(type = 'sms',
                  content = _content,
                  receive_user_list = receive_user_list)
    detail = [_detail]
    taskData = {
                'task': {
                   'name': 'gcp_mcluster_monitor',
                   'remark': 'Remark'
                },
                'detail': detail
    }
    url = '%s&taskData=%s' %(URL, json.dumps(taskData))
    yield http_client.fetch(url, raise_error = False)


PHONE_URL = 'http://ump.letv.cn:8080/alarm/voice'

@coroutine
def send_sms_and_phone(mobiles, content):
    token = 'ad21fd9b78c48d7ff367090eaad3e264'
    mobile = ','.join(mobiles)
    msg = content
    paras = dict(token=token, mobile=mobile,
                 msg=msg)
    phone_url = '%s?%s' %(PHONE_URL, urllib.urlencode(paras))
    http_client = AsyncHTTPClient()
    yield http_client.fetch(phone_url, raise_error = False)

