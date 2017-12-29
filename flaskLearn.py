import logging
import time
from logging.handlers import TimedRotatingFileHandler

from flask import Flask, request, render_template, Markup, session, redirect, url_for, make_response, abort

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wentjiang'

server_log = TimedRotatingFileHandler('server.log','D')
server_log.setLevel(logging.DEBUG)
server_log.setFormatter(logging.Formatter('%(asctime)s % (levelname)s: %(message)s'))

error_log = TimedRotatingFileHandler('error.log','D')
error_log.setLevel(logging.DEBUG)
error_log.setFormatter(logging.Formatter('%(asctime)s: %(message)s [in %(pathname)s:%(lineno)d]'))

app.logger.addHandler(server_log)
app.logger.addHandler(error_log)

@app.route('/')
def index():
    if 'user' in session:
        return 'hello %s' % session['user']
    else:
        return redirect(url_for('login'),302)

@app.route('/user/<int:user_id>')
def get_user(user_id):
    return 'user ID: %d' % user_id

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['user'] == 'admin':
            session['user'] = request.form['user']
            response = make_response('Admin login successfully!')
            response.set_cookie('login_time',time.strftime('%Y-%m-%d %H:%M:%S'))
            return response
        else:
            return 'no such user!'
    if 'user' in session:
        login_time = request.cookies.get('login_time')
        response = make_response('Hello %s, you logged in on %s' % (session['user'], login_time))
        return response
    else:
        title = request.args.get('title','Default')
        response = make_response(render_template('login.html',title=title),200)
        response.headers['key'] = 'value'
        return response

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect(url_for('login'))

@app.route('/error')
def error():
    abort(404)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'),404

if __name__ == '__main__':
    app.run(host='127.0.0.1', debug=True)

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=400):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code

@app.errorhandler(InvalidUsage)
def invalid_usage(error):
    response = make_response(error.message)
    response.status_code = error.status_code
    return response

@app.route('/exception')
def exception():
    app.logger.debug('Enter exception method')
    app.logger.error('403 error happened')
    raise InvalidUsage('No privilege to access the resource', status_code=403)