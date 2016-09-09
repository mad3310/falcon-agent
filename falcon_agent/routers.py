#coding=utf-8
from handlers import AlarmsQueryHandler

urls = [
    (r'/alarms/query/(\w+)', AlarmsQueryHandler),
]
