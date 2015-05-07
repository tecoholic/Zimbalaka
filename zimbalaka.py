from flask import Flask, request, render_template, url_for, \
        send_file, jsonify, make_response, send_from_directory
from celery import Celery

from utils import zimit

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.use_x_sendfile = True

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@celery.task
def prepare_zim(title, articles):
    '''task that prepares the zim file'''
    zimfile = zimit(title, articles)
    return zimfile

@celery.task
def delete_tmp_folder(zimfile):
    '''task to delete the folder'''
    pass

@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        task = prepare_zim.delay(request.form['title'], request.form['list'])
        return make_response( jsonify(status="started", task=task.id), 202 )

@app.route("/status/<task_id>")
def status(task_id):
    task = prepare_zim.AsyncResult(task_id)
    if task.state == 'SUCCESS':
        return jsonify({
            "status" : "success"
            })
    return jsonify({ "status" : "pending" })

@app.route("/download/<task_id>/<filename>")
def download(task_id,filename):
    task = prepare_zim.AsyncResult(task_id)
    if task.state != 'SUCCESS':
        return "Unavailable! Task ID: "+task_id
    return send_file(task.result)



if __name__ == "__main__":
    app.debug = True
    app.run()
