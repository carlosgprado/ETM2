#
# Flask-SocketIO server
# Websockets in Flask! :)
#

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'CbkcAJSBKSAGcASBcsADaSI$&!R%$EASSA'
socketio = SocketIO(app)

connected_clients = 0
understanding = 100
delta = 5

@app.route('/')
def index():
	return render_template('index.html')

@socketio.on('my event yes', namespace = '/mom')
def cb_yes(message):
	""" This will send the information back to 
		the connected client """
	global understanding

	understanding += delta
	if understanding > 100:
		understanding = 100

	emit('my response', {'u': understanding, 'c': connected_clients}, broadcast = True)

@socketio.on('my event no', namespace = '/mom')
def cb_no(message):
	""" This will, as the name suggests, sent the 
		information back to every connected client """
	global understanding

	understanding -= delta
	if understanding < 0:
		understanding = 0

	emit('my response', {'u': understanding, 'c': connected_clients}, broadcast = True)

@socketio.on('connect', namespace = '/mom')
def cb_connect():
	""" We will keep track of connected clients """
	global connected_clients

	print('Client connected')
	connected_clients += 1
	emit('my response', {'u': understanding, 'c': connected_clients}, broadcast = True)

@socketio.on('my disconnect event', namespace = '/mom')
def cb_disconnect(m):
	global connected_clients

	print('Client disconnected')
	connected_clients -= 1
	emit('my response', {'u': understanding, 'c': connected_clients}, broadcast = True)



if __name__ == '__main__':
	print('Starting Websocket Server...')
	socketio.run(app, host = "0.0.0.0", port = 8888)
