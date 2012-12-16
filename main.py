from flask import Flask, request, json, jsonify

app = Flask(__name__)

@app.route('/cmd/', methods=['POST', 'GET'])
def index():
    if request.headers['Content-Type'] == 'application/json':
        # send a command
        if request.method == 'POST':
            return "JSON Message POST: " + json.dumps(request.json)
        # check a command status
        elif request.method == 'GET':
            return "JSON Message GET: " + json.dumps(request.json)

    resp = jsonify()
    resp.status_code = 405
    return resp

if __name__ == "__main__":
    app.debug = True
    app.run(host="127.0.0.1", port=5000)
