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
import logging
import base64

thread_pool = ThreadPoolExecutor(10)

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
WARNING_TIME_DIFF = 210
TIMEOUT_WARN = 'please check async api, the data is out of date!'
MONITOR_INDEX_IN_ES='cluster-monitor'
FETCH_ERR_HISTORY = {}
MAX_FETCH_ERR = 3
MATRIX_AUTH_URL = 'https://login.lecloud.com/nopagelogin?username=matrix&password=matrix' 
def _fetch_error_update(fetch_error):
    if not FETCH_ERR_HISTORY:
        for _node in fetch_error:
            FETCH_ERR_HISTORY[_node] = 1
    else:
        _his = set(FETCH_ERR_HISTORY.keys())
        for k in _his:
            if (not k in fetch_error) and \
               FETCH_ERR_HISTORY[k] < MAX_FETCH_ERR:
                del FETCH_ERR_HISTORY[k]
        for node_name in fetch_error:
            if FETCH_ERR_HISTORY.has_key(node_name):
                FETCH_ERR_HISTORY[node_name] += 1
            else:
                FETCH_ERR_HISTORY[node_name] += 1

def fetch_error_check():
    alarms, node_names = [], []
    for k, v in FETCH_ERR_HISTORY.items():
        _ret = dict(serious = {},
               general = {})
        if v >= MAX_FETCH_ERR:
            _ret['serious']['fetch_failed'] = 'calling failed'
            alarms.append(_ret)
            node_names.append(k)
    return dict(alarms=alarms, node_names=node_names)

def _write_alarm_to_es(alarms, node_names, server_cluster,
                       cluster_type = 'mysql'):
    index = '%s-%s-%s' %(server_cluster, cluster_type,
                        MONITOR_INDEX_IN_ES)
    es_res.record_resource_via_bulk(index, 
        node_names, cluster_type, alarms)

def _monitor_value_parse(resp):
    value = json.loads(resp.body)
    code = value['meta']['code']
    ret = dict(serious = {},
               general = {},
               nothing = {})
    if code != 200:
        return False, ret
    for _type in value['response']:
        for item in value['response'][_type]:
            _val = value['response'][_type][item]
            monitor_type_item = '%s.%s' %(_type, item)
            ret_code = _val['alarm']
            error_record = _val['error_record']
            message = _val['message']
            if error_record:
                error_record = ", error_record=%s" % str(error_record)
                message = '%s%s' %(message, str(error_record))
            create_time_str = _val['ctime']
            t = time.strptime(create_time_str, TIME_FORMAT)
            create_time = datetime.datetime(*t[:6])
            check_time = datetime.datetime.now()
            diff = (check_time-create_time).seconds
            if diff > WARNING_TIME_DIFF:
                ret['serious'][monitor_type_item] = TIMEOUT_WARN
            elif ret_code == 'tel:sms:email':
                ret['serious'][monitor_type_item] = message
            elif ret_code == 'sms:email':
                ret['general'][monitor_type_item] = message
            else:
                ret['nothing'][monitor_type_item] = message
    return True, ret

@coroutine
def get_status_of_target(targets):
    http_client = AsyncHTTPClient()
    resp, alarms, node_names, fetch_error = [], [], [], set()
    for target in targets:
        ip = target['ipAddr']
        user = target['adminUser']
        passwd  = target['adminPassword']
        uri = 'http://%s:8888/mcluster/status' %ip
        _tmp = http_client.fetch(uri, method = 'GET',
                raise_error = False,
                follow_redirects=True,
                auth_username = user,
                auth_password = passwd,
                allow_nonstandard_methods=True)
        resp.append(_tmp)
    ret = yield resp
    for i in range(len(targets)):
        node_name = targets[i]['clusterName']
        _resp = ret[i]
        if _resp.error:
            fetch_error.add(node_name)
        else: 
            flag, alarm_info = _monitor_value_parse(_resp)
            if not flag:
                fetch_error.add(node_name)
            else:
                node_names.append(node_name)
                alarms.append(alarm_info)
    _fetch_error_update(fetch_error)
    raise Return(dict(alarms=alarms, node_names=node_names))

@coroutine
def _get_matrix_auth(http_client):
    auth_uri = MATRIX_AUTH_URL
    resp = yield http_client.fetch(auth_uri, raise_error=False)
    if resp.error:
        logging.error('request for auth failed')
        raise Return({})
    auth = json.loads(resp.text) 
    raise Return(auth)

@coroutine
def _get_all_cluster():
    http_client = AsyncHTTPClient()
    auth = yield _get_matrix_auth()
    uri = '%s/api/hcluster' %options.matrix
    req = HTTPRequest(uri, follow_redirects=True,
                    allow_nonstandard_methods=True,
                    client_id = auth['client'],
                    client_secret = auth['client_secret'])
    resp = yield http_client.fetch(req, raise_error=False)
    if resp.error:
        logging.error('request for all hcluster fail')
        raise Return([])
    else:
        ret = map(lambda x:x['id'], json.loads(resp.text))
        raise Return(ret)

@coroutine
def _get_all_mysql(server_id)
    http_client = AsyncHTTPClient()
    auth = yield _get_matrix_auth()
    uri = '%s/db/containers?hclusterId=%d' %(options.matrix,
                                             int(server_id))
    req = HTTPRequest(uri, follow_redirects=True,
                    allow_nonstandard_methods=True,
                    client_id = auth['client'],
                    client_secret = auth['client_secret'])
    resp = yield http_client.fetch(req, raise_error=False)
    if resp.error:
        logging.error('request for all hcluster fail')
        raise Return([])
    else:
        ret = json.loads(resp.text)
        raise Return(ret)

@coroutine
def write_alarms(server_cluster, targets, cluster_type = 'mysql'):
    status_ret = yield get_status_of_target(targets)
    status_ret_fetch_err = fetch_error_check()
    alarms, node_names = status_ret['alarms'], status_ret['node_names']
    alarms_fetch_err, node_names_fetch_err = \
       status_ret_fetch_err['alarms'], status_ret_fetch_err['node_names']
    #TODO
    #need check is there deleted nodes, and those nodes should not
    #record alarm
    #call http://127.0.0.1:8082/db/containers?hclusterId={server_cluster}

    yield thread_pool.submit(_write_alarm_to_es, alarms, node_names,
                               server_cluster, cluster_type)
    yield thread_pool.submit(_write_alarm_to_es, alarms_fetch_err,
                            node_names_fetch_err, server_cluster,
                            cluster_type)

@coroutine
def write_all_mysql_alarms():
    # call the matrix method http://127.0.0.1:8082/api/hcluster
    # to get all the servers, and store it to server_cluster
    # server_cluster = '48'
    server_clusters = yield _get_all_cluster()
    for server_cluster in server_clusters:
        # call http://127.0.0.1:8082/db/containers?hclusterId=48
        # to get all the ip of the server cluster
        #targets = [dict(ipAddr='10.185.81.79',
        #               clusterName='25_for_qa_test_ljl',
        #               adminPassword='root',
        #               adminUser='root')]
        targets = yield _get_all_mysql(server_cluster)
        try:
            yield write_alarms(server_cluster, targets, 'mysql')
        except Exception as e:
        logging.error(e, exc_info=True)

