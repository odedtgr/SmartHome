import samsungctl
from wakeonlan import send_magic_packet
import time

class API_Manager:
    def send(self, device, args):
        if device['type'] == 'samsung_tv':
            if args['key'] == 'WOL':
                send_magic_packet(device['mac'], port=8001)

            else:
                config = {
                    "name": "samsungctl",
                    "description": "PC",
                    "id": "",
                    "host": "",
                    "port": 8001,
                    "method": "websocket",
                    "timeout": 1,
                }

                config['host'] = device['address']

                try:
                    with samsungctl.Remote(config) as remote:
                        remote.control(args['key'])
                except :
                    return

    def __init__(self, device_manager):
        device_manager.add_api_manager(self)