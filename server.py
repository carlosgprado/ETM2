#
# Flask-SocketIO server
# Websockets in Flask! :)
#

from flask import Flask, render_template, request, url_for, redirect
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, login_user, current_user


app = Flask(__name__, static_url_path = '/static')
login_manager = LoginManager()
login_manager.init_app(app)
socketio = SocketIO(app)

# Mock DB
users = {'user@mail.com': {'pw': 'secret'}}
connected_clients = 0
understanding = 100
delta = 5


class User(UserMixin):
	pass


@login_manager.user_loader
def user_loader(email):
	if email not in users:
		return False

	user = User()
	user.id = email
	return user

@login_manager.request_loader
def request_loader(request):
	email = request.form.get('email')
	if email not in users:
		return False

	user = User()
	user.id = email

	# NEVER do something like this in a real application! :)
	user.is_authenticated = request.form['pw'] == users[email]['pw']

	return user

@app.route('/')
def index():
	if current_user:
		return render_template('index.html')
	else:
		return redirect(url_for('login'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
	global connected_clients

	if request.method == 'GET':
		return """
			<form action='login' method = 'POST'>
			<input type='text' name='email' id='email' placeholder='email'></input>
			<input type='password' name='pw' id='pw' placeholder='password'></input>
			<input type='submit' name='submit'></input>
			</form> """

	email = request.form['email']
	if email in users:
		if request.form['pw'] == users[email]['pw']:
			user = User()
			user.id = email
			login_user(user)
			connected_clients += 1
			return redirect(url_for('index'))

	return 'Failed login'

@socketio.on('my event yes', namespace = '/mom')
def cb_yes(message):
	""" This will send the information back to
		the connected client """
	global understanding

	if not current_user.is_authenticated:
		return redirect(url_for('login'))

	understanding += ((delta + 0.0) / (connected_clients + 1))
	if understanding > 100:
		understanding = 100

	emit('my response', {'u': understanding, 'c': connected_clients}, broadcast = True)

@socketio.on('my event no', namespace = '/mom')
def cb_no(message):
	""" This will, as the name suggests, sent the
		information back to every connected client """
	global understanding

	if not current_user.is_authenticated:
		return redirect(url_for('login'))

	understanding -= ((delta + 0.0) / (connected_clients + 1))
	if understanding < 0:
		understanding = 0

	emit('my response', {'u': understanding, 'c': connected_clients}, broadcast = True)

@socketio.on('connect', namespace = '/mom')
def cb_connect():
	""" We will keep track of connected clients """
	if not current_user.is_authenticated:
		return redirect(url_for('login'))

	print('Client connected')
	emit('my response', {'u': understanding, 'c': connected_clients}, broadcast = True)

@socketio.on('my disconnect event', namespace = '/mom')
def cb_disconnect(m):
	global connected_clients

	print('Client disconnected')
	connected_clients -= 1
	emit('my response', {'u': understanding, 'c': connected_clients}, broadcast = True)



if __name__ == '__main__':

	app.config['SECRET_KEY'] = 'PUTWHATEVERSECRETHERE'

	print('Starting Websocket Server...')
	socketio.run(app, host = "0.0.0.0", port = 8888)
