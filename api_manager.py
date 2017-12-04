import samsungctl
import time

config = {
    "name": "samsungctl",
    "description": "PC",
    "id": "",
    "host": "192.168.1.40",
    "port": 8001,
    "method": "websocket",
    "timeout": 3,
}




class API_Manager:
    def send(self, device, args):
        if device['type'] == 'samsung_tv':
            config = {
                "name": "samsungctl",
                "description": "PC",
                "id": "",
                "host": "",
                "port": 8001,
                "method": "websocket",
                "timeout": 0,
            }

            config['host'] = device['address']
            with samsungctl.Remote(config) as remote:
                remote.control(args['key'])

    def __init__(self, device_manager):
        device_manager.add_api_manager(self)