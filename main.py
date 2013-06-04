#!/usr/bin/python
from flask import Flask, request, json, jsonify
from tasks.celery import celery
from tasks import installationdisk
from tasks import iptables
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-p", "--port", dest="port", default=5000, 
    help="Port to listen on", type="int")
parser.add_option("-l", "--listen", dest="listen", default="10.10.10.1", 
    help="Address to listen on", type="string")

app = Flask(__name__)

@app.route('/cmd/', methods=['POST'])
def index():
    if request.headers['Content-Type'] == 'application/json':
        # send a command
        if request.method == 'POST':
            print request.json
            task = None
            command = request.json['command']
            args = request.json['args']

            if command == "installationdisk_download":
                task = installationdisk.download_file.delay(args['url'],
                    args['path'])

            elif command == "installationdisk_list":
                print command
                task = installationdisk.list_files.delay(args['path'])

            elif command == "installationdisk_delete":
                task = installationdisk.delete_file.delay(args['path'])

            elif command == "check":
                resp = jsonify()
                resp.status_code = 200
                return resp

            elif command == "network_track_ip":
               return iptables.track_ip(args['ip'])

            elif command == "network_check_all": 
                (rx, tx) = iptables.check_all()
                ret = {}
                if rx and tx:
                    ret['rx'] = {}
                    ret['rx']['packets'] = rx[0]
                    ret['rx']['bytes'] = rx[1]
                    ret['tx'] = {}
                    ret['tx']['packets'] = tx[0]
                    ret['tx']['bytes'] = tx[1]
                return jsonify(ret)

            elif command == "network_check_ip": 
                (rx, tx) = iptables.check_ip(args['ip'])
                ret = {}
                if rx and tx:
                    ret['rx'] = {}
                    ret['rx']['packets'] = rx[0]
                    ret['rx']['bytes'] = rx[1]
                    ret['tx'] = {}
                    ret['tx']['packets'] = tx[0]
                    ret['tx']['bytes'] = tx[1]
                else:
                    ret['error'] = 'Unable to get stats for IP'
                return jsonify(ret)

            elif command == "network_remove_ip":
                resp = jsonify(iptables.remove_ip(args['ip']))
                resp.status_code = 200
                return resp

            if task: return task.id
    return error()

@app.route('/cmd/status/<task_id>/')
def cmd_status(task_id):
    task = celery.AsyncResult(task_id)
    ret = {}
    ret['state'] = task.state
    if task.state == 'PROGRESS' or task.state == 'SUCCESS':
        print task.result
        ret['args'] = task.result
    return jsonify(ret)

@app.route('/cmd/abort/<task_id>/')
def cmd_abort(task_id):
    task = celery.AsyncResult(task_id)
    task.revoke(terminate=True)
    return jsonify({'state': 'ABORTED'})

def error():
    resp = jsonify()
    resp.status_code = 405
    return resp

if __name__ == "__main__":
    (options, args) = parser.parse_args()
    app.debug = True
    app.run(host=options.listen, port=options.port)
