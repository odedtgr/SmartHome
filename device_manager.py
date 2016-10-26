import os
import pickle
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect


class DeviceManager:
    #add an mqtt instance to device manager, used for mqtt.publish
    def add_mqtt_client(self, mqtt):
        self.mqtt = mqtt


    def get_device_by_id(self, device_id):
        for device in self.devices:
            if device['id'] == device_id:
                return device
        return None


    def is_group_device(self, device):
        return device['name'] in self.group_devices


    def simple_devices(self):
        return [device for device in self.devices if not self.is_group_device(device)]


    def get_devices_by_type(self, device_type):
        return filter(lambda device: device['type'] == device_type and not self.is_group_device(device), self.devices)


    def update_simple_device(self, device, args):
        device_type = device['type']
        if device['mqtt'] == 'true':
            topic = self.mqtt.topic_pub
            self.mqtt.publish(topic, args['mode'])
        else:
            getattr(self.radio, 'update_%s' % device_type)(device['address'], device['number'], args)
        device['last_config'] = args


    def update_scheduler(self, scheduler):
        self.scheduler = scheduler
        self.save_scheduler()


    @staticmethod
    def get_simple_device_icon(device, args):
        if len(args.keys()) > 0:
            key = args.keys()[0]
            return '/img/device{}_{}_{}.png'.format(device['id'], key, args[key])
        return None


    def load_devices(self):
        try:
            if os.path.getmtime(self.devices_filename) > os.path.getmtime('settings.py'):
                f = open(self.devices_filename, 'r')
                self.devices = pickle.load(f)
                f.close()
        except Exception as ex:
            self.logger.info("Error loading devices file: " +  str(ex))


    def load_scheduler(self):
        try:
            if os.path.getmtime(self.scheduler_filename) > os.path.getmtime('settings.py'):
                f = open(self.scheduler_filename, 'r')
                self.scheduler = pickle.load(f)
                f.close()
        except Exception as ex:
            self.logger.info("Error loading scheduler file: " +  str(ex))


    def save_devices(self):
        f = open(self.devices_filename, 'w')
        pickle.dump(self.devices, f)
        f.close()


    def save_scheduler(self):
        f = open(self.scheduler_filename, 'w')
        pickle.dump(self.scheduler, f)
        f.close()


    def update_device(self, device_id, args):
        device = self.get_device_by_id(device_id)
        if self.is_group_device(device):
            for simple_device in self.get_devices_by_type(device['type']):
                self.update_simple_device(simple_device, args)
            device['last_config'] = args
        else:
            self.update_simple_device(device, args)
        self.save_devices()
        return device


    def get_status_icon(self, device, args):
        if self.is_group_device(device):
            devices = self.get_devices_by_type(device['type'])
            if devices:
                return DeviceManager.get_simple_device_icon(devices[0], args)
            return None
        else:
            return DeviceManager.get_simple_device_icon(device, args)


    def __init__(self, devices, scheduler, group_devices, devices_filename, scheduler_filename, logger, radio, socketio):
        self.devices = devices
        self.scheduler = scheduler
        self.group_devices = group_devices
        self.devices_filename = devices_filename
        self.scheduler_filename = scheduler_filename
        self.logger = logger
        self.socketio = socketio
        self.radio = radio
        self.radio.set_status_updater(StatusUpdater(self))
        self.radio.set_logger(logger)
        self.load_devices()
        self.load_scheduler()


class StatusUpdater:
    def __init__(self, device_manager):
        self.device_manager = device_manager

    def get_device_by_address(self, address, number):
        for device in self.device_manager.devices:
            if device.get('address') == address and device.get('number') == number:
                return device
        return None


    def update_device_status(self, device, status):
        for k, v in device['last_config'].items():
            if k not in status:
                status[k] = v
        device['last_config'] = status
        self.device_manager.save_devices()
        self.device_manager.socketio.emit('update_device', {'status': status, 'device': device})