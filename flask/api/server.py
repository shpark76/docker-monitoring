import time
import redis
import pymysql
from random import random

from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson.json_util import dumps
from bson import json_util
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)
metrics.info("flask_app_info", "App Info, this can be anything you want", version="1.0.0")

cache = redis.Redis(host='redis', port=6379)

# custom metric to be applied to multiple endpoints
common_counter = metrics.counter(
    'flask_by_endpoint_counter', 'Request count by endpoints',
    labels={'endpoint': lambda: request.endpoint}
)

def get_hit_count():
    time.sleep(random() * 0.5)
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/', methods=['GET'])
@common_counter
def hello():
    count = get_hit_count()
    return 'Flask in a Docker!!! Hello World! I have been seen {} times.\n'.format(count)

@app.route('/foo', methods=['GET'])
@common_counter
def hello2():
    count = get_hit_count()
    return 'Flask in a Docker!!! Hello World! I have been seen {} times.\n'.format(count)

@app.route('/abc', methods=['GET'])
@common_counter
def hello3():
    count = get_hit_count()
    return 'Flask in a Docker!!! Hello World! I have been seen {} times.\n'.format(count)


@app.route('/collection/:collection_id"', methods=['GET'])
@common_counter
@metrics.counter(
    'flask_hit_cnt_collection', 'Number of invocations per collection', labels={
        'collection': lambda: request.view_args['collection_id'],
        'status': lambda resp: resp.status_code
    })
def hello_collection():
    count = get_hit_count()
    return 'Flask in a Docker!!! Hello World! I have been seen {} times.\n'.format(count)


# register additional default metrics
metrics.register_default(
    metrics.counter(
        'flask_by_path_counter', 'Request count by request paths',
        labels={'path': lambda: request.path}
    )
)

app.run(host='0.0.0.0', debug=True)

