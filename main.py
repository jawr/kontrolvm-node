from flask import Flask, request, json, jsonify
from tasks.celery import celery
from tasks import installationdisk

app = Flask(__name__)

@app.route('/cmd/', methods=['POST'])
def index():
    if request.headers['Content-Type'] == 'application/json':
        # send a command
        if request.method == 'POST':
            url = request.json['url']
            path = request.json['path']
            task = installationdisk.download_file.delay(url, path)

            return task.id
    return error()

@app.route('/cmd/<task_id>/')
def cmd_status(task_id):
    task = celery.AsyncResult(task_id)
    return jsonify(task.result)

def error():
    resp = jsonify()
    resp.status_code = 405
    return resp

if __name__ == "__main__":
    app.debug = True
    app.run(host="127.0.0.1", port=5000)
