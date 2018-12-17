import serial, sys
from xbee import XBee
from thing_speak import *
from pushover import *


def calc_ac_message(args):
    message = '111000' # prefix
    message += ('01' if args['on_off-changed'] == True else '10') # on_off
    message += ('101001' if args['mode'] == 'cool' else '100110') # mode
    fan_options = {'1': '1010',
                   '2': '1001',
                   '3': '0110',
                   'A': '0101'
                   }
    message += fan_options[args['fan']] # fan
    message += '1010101010'
    temp_options = {'16': '10101001',
                    '17': '10100110',
                    '18': '10100101',
                    '19': '10011010',
                    '20': '10011001',
                    '21': '10010110',
                    '22': '10010101',
                    '23': '01101010',
                    '24': '01101001',
                    '25': '01100110',
                    '26': '01100101',
                    '27': '01011010',
                    '28': '01011001',
                    '29': '01010110',
                    '30': '01010101'
                    }
    message += temp_options[args['temp']] #temp
    message += '10101010101010101010101010101010100110'
    message += message + message
    message += '1111000000'
    #logger.info("message={}".format(message))

    data = ''
    while len(message) > 0:
        data += chr(int(message[:8],2))
        message = message[8:]
    return data


class Xbee:
    def __init__(self, device_manager):
        self.serial_port = serial.Serial('/dev/ttyAMA0', 19200)
        self.xbee = XBee(self.serial_port, callback=self.handle_received_data)
        device_manager.add_xbee(self)
        self.device_manager = device_manager


    def handle_received_data(self, data):
        if 'source_addr' in data and 'rf_data' in data:
            device = self.get_device_by_address(data['source_addr'], ord(data['rf_data'][0]))
            rf_data = '\\'.join(x.encode('hex') for x in data['rf_data'])

            if device is not None:
                print "[{}] - Receiving data from {}: {}, rssi:{} dBm".format(datetime.datetime.now(), device.name,
                    rf_data, -ord(data['rssi']))
                device.handle_message_from_device(data)

                if device['type'] == 'temperature':
                    temperature = float(ord(data['rf_data'][1])*256+ord(data['rf_data'][2]))/10
                    rh = float(ord(data['rf_data'][3])*256+ord(data['rf_data'][4]))/10
                    status = {'Temp' : str(temperature), 'Rh' : str(rh)}
                    ThingSpeak_update_DHT22(temperature, rh)


    def close(self):
        self.xbee.halt()
        self.serial_port.close()


    def update_Shutter(self, addr, device_number, args):
        Shutter_options = {'100': '\x01',
                           '0': '\x02',
                           'pause': '\x03',
                           '25': '\x04',
                           '50': '\x05',
                           '75': '\x06',
                           }
        data = Shutter_options[args['mode']]
        self.xbee.send('tx',
                       frame_id='A',
                       dest_addr=addr,
                       options='\x00',
                       data=(chr(device_number)+data))


    def update_ShutterNew(self, addr, device_number, args):
        if args['mode'] == 'pause':
            data = "\x02"
        elif args['mode'] == 'get_device_status':
            data = "\x00"
        else:
            data = "\x01" + chr(int(args['mode']))

        self.xbee.send('tx',
                       frame_id='A',
                       dest_addr=addr,
                       options='\x00',
                       data=(chr(device_number)+data))

    def update_Boiler(self, addr, device_number, args):
        if(args.has_key('mode')):
            if args['mode'] == 'get_device_status':
                data = "\x00"  #get status
            elif args['mode'] == '6':
                data = "\x01" + chr(int(args['mode'])) + chr(int(args['target_temp']))
            else:
                data = "\x01" + chr(int(args['mode'])) #set status
            self.xbee.send('tx',
                           frame_id='A',
                           dest_addr=addr,
                           options='\x00',
                           data=(chr(device_number)+data))

    def update_temperature(self, addr, device_number, args):
        data = 0

    def update_BoilerTemperature(self, addr, device_number, args):
        if (args.has_key('mode')):
            if args['mode'] == 'get_device_status':
                data = "\x00"  # get status
            self.xbee.send('tx',
                           frame_id='A',
                           dest_addr=addr,
                           options='\x00',
                           data=(chr(device_number) + data))

    def update_AirConditioner(self, addr, device_number, args):
        if args['mode'] == 'get_device_status':
            command = "\x00"
        else:
            command = "\x01"
        data = calc_ac_message(args)

        self.xbee.send('tx',
                       frame_id='A',
                       dest_addr=addr,
                       options='\x00',
                       data=(chr(device_number)+command+data))


    def get_device_by_address(self, address, number):
        for device in self.device_manager.devices_list:
            if device.address == address and device.number == number:
                return device
        return None