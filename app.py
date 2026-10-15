import os
from flask import Flask, request, jsonify, send_from_directory
from redis.exceptions import RedisError
from memory import Memory

app = Flask(__name__, static_folder=None)
app.config['MAX_CONTENT_LENGTH'] = 4096

def memory():
    tenant=request.headers.get('X-Demo-Tenant','demo')
    if tenant not in ('demo','other'):
        raise ValueError('Only synthetic demo tenants are allowed.')
    return Memory(tenant)

@app.errorhandler(ValueError)
def invalid(e):
    return jsonify(error=str(e)),400

@app.errorhandler(RedisError)
def unavailable(e):
    # Fail closed; never return a stale cached answer or disclose connection details.
    return jsonify(error='FalkorDB unavailable. No answer or action was produced.'),503

@app.get('/')
def home():
    return send_from_directory(os.path.dirname(__file__),'index.html')

@app.get('/api/state')
def state():
    return jsonify(memory().snapshot())

@app.post('/api/reset')
def reset():
    return jsonify(memory().reset())

@app.post('/api/remember')
def remember():
    data=request.get_json() or {}
    fid=memory().remember(data.get('value'),data.get('source'))
    return jsonify(id=fid)

@app.post('/api/plan')
def plan():
    return jsonify(memory().plan())

@app.post('/api/handoff')
def handoff():
    return jsonify(memory().handoff())

if __name__=='__main__':
    app.run(host='127.0.0.1',port=int(os.getenv('PORT','8080')))
