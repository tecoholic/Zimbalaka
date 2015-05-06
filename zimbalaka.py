from flask import Flask, request, render_template, url_for, \
        send_file

from utils import zimit

app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')

if __name__ == "__main__":
    app.debug = True
    app.run()
