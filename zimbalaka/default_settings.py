# The default settings is for the **development**
# NOTE You **MUST** change this before running production

DEBUG = True
SECRET_KEY = 'development key'

# Celery conf when using REDIS as broker
# NOTE Change this if you want to use a different broker
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
