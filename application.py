from __future__ import absolute_import, unicode_literals
from flask import Flask, render_template, request, redirect, url_for
from flask import jsonify
import json
import os
from celery_ import make_celery


app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = "amqp://localhost//"
app.config['CELERY_RESULT_BACKEND'] = "rpc://"

celery_app = make_celery(app)

#initialise webdriver options
executable_path = os.getenv('GECKODRIVER_PATH')
firefox_binary = os.getenv('FIREFOX_BIN')


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
    from task_search import search
    
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    task = search.delay(start_date, end_date, earning, executable_path, firefox_binary)
    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  task_id=task.id)}


@app.route('/crossreference', methods=['GET'])
def get_datas():
    from task_crossreference import crossreference
    
    task = crossreference.delay(earning, executable_path, firefox_binary)  
    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  task_id=task.id)}
    
@app.route('/status/<task_id>')
def taskstatus(task_id):
    from task_search import search
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
        app.run() 