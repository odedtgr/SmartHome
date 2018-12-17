import os
import errno
import json
import pickle
from thing_speak import *
from flask import render_template

class Device:
    def __init__(self, device, device_manager):
        self.device_manager = device_manager
        self.name = device.get('name')
        self.id =  device.get('id')
        self.type = device.get('type')
        self.address = device.get('address')
        self.id = device.get('id')
        self.number = device.get('number') #in case several devices are on the same address (same radio)
        self.last_config = device.get('last_config')
        self.load_persistency()

        if 'protocol' in device:
            self.protocol = device.get('protocol')
        else:
            self.protocol = 'xbee'

        if 'protocol' in device:
            self.protocol = device.get('protocol')
        else:
            self.protocol = 'xbee'

        if 'show_in_devices' in device:
            self.show_in_devices = device.get('show_in_devices')
        else:
            self.show_in_devices = True

    def __str__(self):
        return self.name

    def set_config(self, args):
        #Sends a command to the device to set its current mode
        try:
            args = args.to_dict()
        except:
            args = args
        for k, v in self.last_config.items():
            if k not in args:
                args[k] = v

        if self.protocol == 'xbee':
            getattr(self.xbee, 'update_%s' % self.type)(self.address, self.number, args)
        elif self.protocol == 'mqtt':
            topic = self.device_manager.mqtt.topic_pub
            self.pub_topic = topic + self.name
            args_json_str = json.dumps(args)
            self.device_manager.mqtt.publish(self.pub_topic, args_json_str)


    def run_scheduler_task(self, task):
        self.set_config(task)


    def update_last_config(self, args):
        #if a config was sent from the device, update the last known status in object
        try:
            args = args.to_dict()
        except:
            args = args
        for k, v in self.last_config.items():
            if k not in args:
                args[k] = v
        self.last_config = args
        self.device_manager.socketio.emit('update_device', {'status': self.last_config, 'device_id': self.id, 'device_type': self.type})
        self.device_manager.mqtt.update_homebridge(self)


    def handle_message_from_device(self, status):
        if self.protocol == 'xbee':
            status = {'mode': str(ord(status['rf_data'][1]))}
        self.update_last_config(status)


    def render_scheduler_template(self, release):
        return render_template('{}.html'.format(self.type), device=self, show_device_label=False, release=release, context='scheduler' )


    def save_persistency(self):
        filename = os.getcwd() + "/persistency/" + self.name + ".txt"
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        f = open(filename, 'w')
        pickle.dump(self.last_config, f)
        f.close()


    def load_persistency(self):
        filename = os.getcwd() + "/persistency/" + self.name + ".txt"
        try:
            if os.path.getmtime(filename) > os.path.getmtime('settings.py'):
                f = open(filename, 'r')
                self.last_config = pickle.load(f)
                f.close()
        except Exception as ex:
            print"Device persistency file does not exist: " + str(ex)


    def get_device_status(self):
        return


    def handle_message_from_homekit(self, command, status):
        status = {"mode": str(status)}
        self.set_config(status)


#---------------------------ShutterNew----------------------------#
class ShutterNew(Device):
    def get_device_status(self):
        self.set_config({'mode':'get_device_status'})


#---------------------------SamsungTv----------------------------#
class SamsungTv(Device):
    def __init__(self, device, device_manager):
        Device.__init__(self, device, device_manager)
        self.mac = device.get('mac')


    def set_config(self, args):
        self.device_manager.api_manager.send(self, args)
        self.update_last_config(args)


    def handle_message_from_homekit(self, command, status):
        self.set_config(status)
#---------------------------BoilerTemperature----------------------------#
class BoilerTemperature(Device):
    def __init__(self, device, device_manager):
        Device.__init__(self, device, device_manager)


    def handle_message_from_device(self, data):
        temperature = float((ord(data['rf_data'][2]) << 8) | (ord(data['rf_data'][1]) << 0)) / float(256)
        status = {'Temp': str(temperature)}
        ThingSpeak_update_DS18B20(temperature)
        waterHeater = self.device_manager.get_device_by_name('Water Heater')
        waterHeater.update_last_config(status)
        self.update_last_config(status)

    def get_device_status(self):
        self.set_config({'mode': 'get_device_status'})


#---------------------------Boiler----------------------------#
class Boiler(Device):
    def __init__(self, device, device_manager):
        Device.__init__(self, device, device_manager)


    def handle_message_from_device(self, data):
        now = datetime.datetime.now()
        date = datetime.datetime.today().strftime('%Y-%m-%d')
        curr_hour = "{}:{}".format(str(now.hour).zfill(2), str(now.minute).zfill(2))
        mode = ord(data['rf_data'][1])
        status = {'mode': str(mode),
                  'time': curr_hour,
                  'date': date
                  }
        self.update_last_config(status)
        self.save_persistency()


    def get_device_status(self):
        self.set_config({'mode': 'get_device_status'})


    def run_scheduler_task(self, task):
        if task['target_temp'] != 'Off':
            task['mode'] = '6'
        self.set_config(task)


#---------------------------AirConditioner----------------------------#
class AirConditioner(Device):
    def __init__(self, device, device_manager):
        Device.__init__(self, device, device_manager)


    def handle_message_from_device(self, data):
        status = {'device_on': ('false' if data['rf_data'][1] == '\x01' else 'true')}
        self.update_last_config(status)


    def set_config(self, args):
        Device.set_config(self, args)
        self.update_last_config(args) #optimistic save config of AC controls: temperature, fan speed, mode
        self.save_persistency()


    def run_scheduler_task(self, task):
        device_on = self.last_config['device_on'] == 'true'
        if task['device_on'] != device_on:
            task['on_off-changed'] = True
        else:
            task['on_off-changed'] = False
            del task['device_on']
        if task['temp'] == '16':
            del task['temp']

        self.set_config(task)


    def get_device_status(self):
        Device.set_config(self, {'mode': 'get_device_status'})


    def handle_message_from_homekit(self, command, status):
        if command == 'setTargetTemperature':
            status = {"temp": str(status)}
            self.update_last_config(status)

        elif command == 'setTargetHeatingCoolingState':
            currently_on = self.last_config.get("device_on") == "true"
            desired_on = str(status) != '0'
            on_off_changed = 'true ' if desired_on == currently_on else 'false'
            status = {"on_off-changed": on_off_changed}
            if str(status) == '0':
                status = {"on_off-changed": on_off_changed}
            elif str(status) == '1':
                status = {"on_off-changed": on_off_changed, "mode": "heat"}
            else:
                status = {"on_off-changed": on_off_changed, "mode": "cool"}
            self.update_last_config(status)

        elif command == 'setOn':
            currently_on = self.last_config.get("device_on") == "true"
            desired_on = str(status) != '0'
            on_off_changed = False if desired_on == currently_on else True
            status = {"on_off-changed": on_off_changed}

        self.set_config(status)


#---------------------------Light----------------------------#
class Light(Device):
    def handle_message_from_homekit(self, command, status):
        status = {"device_on": "true"} if status else {"device_on": "false"}
        self.set_config(status)
