#!/usr/bin/python
import logging
import sys, os
import json
from threading import Thread
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from device_manager import *
from scheduler import Scheduler
from settings import *
from pushover import *
from MQTT import *
from api_manager import *
from scenario_manager import *

async_mode = 'threading'

app = Flask(__name__, static_folder='static', static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

@app.route("/")
def homepage():
    return devices()

@app.route("/devices")
def devices():
    if not is_loggedin():
        return redirect(url_for('login', return_to='devices'))
    the_devices = get_device_manager().devices
    return render_template('devices.html', devices=the_devices, show_device_label=True, show_status=True, scheduler_on=Settings.scheduler_on, release=Settings.release)

@app.route("/scheduler")
def scheduler():
    if not is_loggedin():
        return redirect(url_for('login', return_to='scheduler'))
    the_devices = get_device_manager().simple_devices()
    the_scheduler = get_device_manager().scheduler
    return render_template('scheduler.html', devices=the_devices, show_device_label=True, show_status=False, scheduler=the_scheduler, release=Settings.release)

@app.route("/scenarios")
def scenarios():
    if not is_loggedin():
        return redirect(url_for('login', return_to='devices'))
    the_devices = get_device_manager().devices
    return render_template('scenarios.html', SCENARIOS = Settings.SCENARIOS, release=Settings.release)


@socketio.on('my broadcast event', namespace='')
def update_device_websoc(message):
    if not is_loggedin():
        return redirect(url_for('login'))
    device_manager.update_device(int(message['device_id']), message['data'], True)

@app.route("/update_device/<int:device_id>", methods=['GET', 'POST'])
def update_device(device_id):
    if not is_loggedin():
        return redirect(url_for('login', return_to='devices'))
    device_manager.update_device(device_id, request.form, True)
    return json.dumps({'succeeded': True})

@app.route("/api/update_device/<username>/<password>/<int:device_id>")
def api_update_device(username, password, device_id):
    try:
        authenticate(username, password)
        device = device_manager.update_device(device_id, request.args, True)
        return render_template('api_ok.html', device_name=device['name'])
    except Exception, ex:
        return render_template('api_error.html', error_message=str(ex))

@app.route("/update_scheduler", methods=['GET', 'POST'])
def update_scheduler():
    if not is_loggedin():
        return json.dumps({'succeeded': False, 'message': 'Not Logged In.'})
    the_scheduler = json.loads(request.form['scheduler'])
    device_manager.update_scheduler(the_scheduler)
    scheduler.set(the_scheduler)
    return json.dumps({'succeeded': True})

@app.route("/execute_scenario/<scenario_name>", methods=['GET', 'POST'])
def execute_scenario(scenario_name):
    if not is_loggedin():
        return redirect(url_for('login', return_to='devices'))
    scenario_manager.execute_scenario(scenario_name)
    return json.dumps({'succeeded': True})


@app.route("/device_config_panel/<int:device_id>/<int:schedule_index>", methods=['GET', 'POST'])
def device_config_panel(device_id, schedule_index):
    if not is_loggedin():
        return json.dumps({'succeeded': False, 'message': 'Not Logged In.'})
    device = get_device_manager().get_device_by_id(device_id).copy()
    the_scheduler = get_device_manager().scheduler
    if schedule_index < len(the_scheduler) and the_scheduler[schedule_index]['device_id'] == device_id:
        device['last_config'] = the_scheduler[schedule_index]['config']
    else:
        device['last_config'] = dict()
    if(device['type']=='boiler'):
        return render_template('{}_scheduler.html'.format(device['type']), device=device, show_device_label=False, release=Settings.release)
    else:
        return render_template('{}.html'.format(device['type']), device=device, show_device_label=False, release=Settings.release)


@app.route("/new_schedule_item_panel/<int:schedule_index>", methods=['GET', 'POST'])
def new_schedule_item_panel(schedule_index):
    if not is_loggedin():
        return json.dumps({'succeeded': False, 'message': 'Not Logged In.'})

    schedule_item = {
        'enabled':      True,
        'device_id':    1,
        'day':          ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
        'hour':         '00:00',
    }
    return render_template('schedule_item.html', devices=get_device_manager().devices, schedule_item=schedule_item, schedule_index=schedule_index)


@app.route('/login/<return_to>', methods=['GET', 'POST'])
def login(return_to):
    if request.method == 'POST':
        try:
            authenticate(request.form['username'], request.form['password'])
            session['username'] = request.form['username']
            session.permanent = True
            return redirect(url_for(request.form['return_to']))
        except:
            flash('Wrong username or password.')
            pushover_update("HomeWise", "Failed Authentication attempt for: " +request.form['username'], "0")
            return redirect(url_for('login', return_to='devices'))
    else:
        return render_template('login.html', return_to=return_to)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login', return_to='devices'))

@app.errorhandler(Exception)
def all_exception_handler(error):
   pushover_update("Error:", error, "1")


def authenticate(username, password):
    if not (password == Settings.users[username]):
        raise Exception('Authentication Failed.')
    else:
        pushover_update("HomeWise", username+" is logged in", "0")


def is_loggedin():
    return session.get('username') is not None


def get_device_manager():
    return device_manager


app.secret_key = os.urandom(24)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.INFO)
radio = getattr(__import__('radio'), Settings.RADIO_CLASS)()
device_manager = DeviceManager(Settings.DEVICES,
                               Settings.SCHEDULER,
                               Settings.GROUP_DEVICES,
                               Settings.DEVICES_FILENAME,
                               Settings.SCHEDULER_FILENAME,
                               app.logger,
                               radio,
                               socketio)
mqtt = MQTT(Settings.MQTT_BROKER, Settings.MQTT_PORT, Settings.MQTT_TOPIC_SUB, Settings.MQTT_TOPIC_PUB, Settings.HOMEKIT_NAME, device_manager, app.logger)
api_manager = API_Manager(device_manager)
scheduler = Scheduler(device_manager.scheduler, Settings, device_manager, app.logger)
scenario_manager = Scenario_Manager(device_manager, Settings.SCENARIOS)



if __name__ == "__main__":
    pushover_update("HomeWise","Up and running","0")
    try:
        socketio.run(app, host=Settings.HOST, port=Settings.PORT, debug=Settings.DEBUG, use_reloader=False)
    except :
        pushover_update("HomeWise", "Allready runnung", "0")
        os._exit(1)
radio.close()
