import os

from zimbalaka import celery
from zimbalaka.utils import zimit

@celery.task
def prepare_zim(title, articles):
    '''task that prepares the zim file'''
    zimfile = zimit(title, articles)
    return zimfile

@celery.task(ignore_result=True)
def delete_zim(zimfile):
    '''task to delete the folder'''
    os.remove(zimfile)
