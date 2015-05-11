import redis

from zimbalaka import app
from zimbalaka.tasks import prepare_zim, delete_zim

from flask import request, render_template, url_for, \
        send_file, jsonify, make_response, send_from_directory

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
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    msgkey = 'task:{0}:log'.format(task_id)
    countkey = 'task:{0}:count'.format(task_id)
    if task.state == 'SUCCESS':
        r.delete(msgkey, countkey)
        return jsonify( {"status" : "success"} )
    elif task.state == 'PENDING':
        return jsonify( {"status" : "pending"} )
    elif task.state == 'STARTED':
        msg = r.get(msgkey)
        count = r.get(countkey)
        return jsonify({ "status" : "started",
            "msg" : msg,
            "count" : count
            })
    elif task.state == 'RETRY':
        return jsonify({ "status" : "retry" })
    else:
        msg = r.get(msgkey)
        r.delete(msgkey, countkey)
        return jsonify({ "status" : "failure", "msg" : msg })

@app.route("/download/<task_id>/<filename>")
def download(task_id,filename):
    task = prepare_zim.AsyncResult(task_id)
    if task.state != 'SUCCESS':
        return "Unavailable! Task ID: "+task_id
    res = task.result
    delete_zim.apply_async([res], countdown=3540)
    try:
        return send_file(res)
    except IOError:
        return 'The file you have requested has been deleted from the server. Zim files are stored only for 59 minutes.'

