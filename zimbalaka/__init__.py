from flask import Flask
from celery import Celery

app = Flask(__name__)
app.config.from_object('zimbalaka.default_settings')
# app.config.from_envvar('ZIMBALAKA_SETTINGS') # used for loading production config

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

import zimbalaka.views
