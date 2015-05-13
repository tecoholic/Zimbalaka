import os
import redis
from celery.utils.log import get_task_logger
import logging

from zimbalaka import celery
from zimbalaka.utils import zimit

class CLogger:
    def __init__(self, uid):
        self.r = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.uid = uid

    def log(self, record):
        self.r.set( 'task:{0}:log'.format(self.uid), record)

    def count(self, percent):
        self.r.set('task:{0}:count'.format(self.uid), percent)

@celery.task(bind=True)
def prepare_zim(self, title, articles, lang):
    '''task that prepares the zim file'''
    c = CLogger( self.request.id )
    zimfile = zimit(title, articles, lang, c)
    return zimfile

@celery.task(ignore_result=True)
def delete_zim(zimfile):
    '''task to delete the folder'''
    os.remove(zimfile)
