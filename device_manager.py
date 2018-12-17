import os
import pickle
from time import sleep
import json
from werkzeug.datastructures import ImmutableMultiDict
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
import device_class

class DeviceManager:
    #add an mqtt instance to device manager, used for mqtt.publish
    def add_xbee(self, xbee):
        for device in self.devices_list:
            if device.protocol == 'xbee':
                device.xbee = xbee


    def add_mqtt_client(self, mqtt):
        self.mqtt = mqtt


    # add an mqtt instance to device manager, used for mqtt.publish
    def add_api_manager(self, api_manager):
        self.api_manager = api_manager


    def get_device_by_id(self, device_id):
        for device in self.devices_list:
            if device.id == device_id:
                return device
        return None


    def get_device_by_name(self, device_name):
        for device in self.devices_list:
            if device.name == device_name:
                return device
        return None


    def get_devices_status(self):
        for device in self.devices_list:
            device.get_device_status()
            sleep(0.300)


    def update_scheduler(self, scheduler):
        self.scheduler = scheduler
        self.save_scheduler()

#TODO: Move to scheduler.py
    def load_scheduler(self):
        try:
            if os.path.getmtime(self.scheduler_filename) > os.path.getmtime('settings.py'):
                f = open(self.scheduler_filename, 'r')
                self.scheduler = pickle.load(f)
                f.close()
        except Exception as ex:
            self.logger.info("Error loading scheduler file: " +  str(ex))


    def save_scheduler(self):
        f = open(self.scheduler_filename, 'w')
        pickle.dump(self.scheduler, f)
        f.close()


    def __init__(self, devices, scheduler, scheduler_filename, logger, socketio):
        self.devices = devices
        self.scheduler = scheduler
        self.scheduler_filename = scheduler_filename
        self.logger = logger
        self.socketio = socketio
        self.load_scheduler()
        self.devices_list = []
        for device in devices:
            deviceType = device.get('type')
            if not deviceType in dir(device_class): #check if class exist for device type, if not used Device class
                deviceType = 'Device'
            deviceClass = getattr(device_class, deviceType)
            self.devices_list.append(deviceClass(device, self))


        # TODO: object oriented
        #self.device_manager.mqtt.update_homebridge(device)