from __future__ import absolute_import, unicode_literals
from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify
import json
import os
from celery_ import make_celery


app = Flask(__name__)

app.config['CELERY_BROKER_URL'] = 'pyamqp://rabbitmq:rabbitmq@rabbit//'
app.config['result_backend'] = "rpc://"
app.config['broker_pool_limit'] = 1
app.config['broker_heartbeat'] = None
app.config['worker_prefetch_multiplier'] = 1
app.config['worker_concurrency'] = 1



celery_app = make_celery(app)


#global variables
earning = {}
earning['ticker'] = []
earning['date'] = []
earning['time']= []


@app.route('/')
def acceuil():    
    return render_template('acceuil.html')


@app.route('/search', methods=['POST'])
def process():
    from tasks import search
    
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    earning['ticker'].clear()
    earning['date'].clear()
    earning['time'].clear()
    task = search.delay(start_date, end_date, earning)
    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  task_id=task.id)}


@app.route('/crossreference', methods=['POST'])
def get_datas():
    datas = request.form.get('tickers')
    tickers_list = datas.split("<br>")
 
    from tasks import crossreference
    
    task = crossreference.delay(tickers_list)  
    return jsonify({}), 202, {'Location': url_for('referencestatus',
                                                  task_id=task.id)}
    
@app.route('/status/<task_id>')
def taskstatus(task_id):
    from tasks import search
    task = search.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 0,
            'message': 'Pending...'
        }
        
    elif task.state != 'FAILURE':
        # if it returns None
        if task.info is None:
            response = {
                'state': 'FAILURE',
                'current': 0,
                'total': 0,
                'message' : "An error occured"
            }
        else:
            response = {
                'state': task.state,
                'current': task.info['current'],
                'total': task.info['total'],
                'message': task.info['message'],
            }
            if 'result' in task.info:
                response['result'] = task.info['result']
            
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 0,
            'total': 0,
            'message': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

@app.route('/status/<task_id>')
def referencestatus(task_id):
    from tasks import crossreference
    task = crossreference.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 0,
            'message': 'Pending...'
        }
        
    elif task.state != 'FAILURE':
        # if it returns None
        if task.info is None:
            response = {
                'state': 'FAILURE',
                'current': 0,
                'total': 0,
                'message' : "An error occured"
            }
        else:
            response = {
                'state': task.state,
                'current': task.info['current'],
                'total': task.info['total'],
                'message': task.info['message'],
            }
            if 'result' in task.info:
                response['result'] = task.info['result']
            
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 0,
            'total': 0,
            'message': str(task.info),  # this is the exception raised
        }
    return jsonify(response)

if __name__ == "__main__": 
        app.run(host='0.0.0.0') 