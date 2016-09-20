#coding = utf-8
from tornado.httpclient import AsyncHTTPClient
import json
from tornado.gen import coroutine, Return

URL = 'http://odin.letv.cn:8080/alarm/api/addTask?token=0115e72e386b969613560ce15124d75a'

@coroutine
def send_sms(mobiles, content):
    receive_user_list = []
    http_client = AsyncHTTPClient()
    for users in mobiles:
        info_list = users.split(':')
        _receive = dict(username = info_list[0],
                        mobile = info_list[1])
        receive_user_list.append(_receive)
    _detail = dict(type = 'sms',
                  content = content,
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

