import serial
import datetime
from xbee import XBee
from thing_speak import *
from pushover import *


def calc_ac_message(args, logger):
    message = '111000' # prefix
    message += ('01' if args['on_off-changed'] == 'true' else '10') # on_off
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

    #logger.info("data={}".format(data))
    return data



class Radio:
    def __init__(self):
        self.serial_port = serial.Serial('/dev/ttyAMA0', 19200)
        self.xbee = XBee(self.serial_port, callback=self.handle_received_data)


    def handle_received_data(self, data):
        if 'source_addr' in data and 'rf_data' in data:
            device = self.status_updater.get_device_by_address(data['source_addr'], ord(data['rf_data'][0]))
            rf_data = '\\'.join(x.encode('hex') for x in data['rf_data'])
            print "[{}] - Receiving data from {}: {}, rssi:{} dBm".format(datetime.datetime.now(), device['name'], rf_data, -ord(data['rssi']))
            if device is not None:
                if device['type'] == 'shutter':
                    status = {'mode' : str(ord(data['rf_data'][1]))}
                if device['type'] == 'shutterNew':
                    status = {'mode' : str(ord(data['rf_data'][1]))}
                if device['type'] == 'temperature':
                    temperature = float(ord(data['rf_data'][1])*256+ord(data['rf_data'][2]))/10
                    rh = float(ord(data['rf_data'][3])*256+ord(data['rf_data'][4]))/10
                    status = {'Temp' : str(temperature), 'Rh' : str(rh)}
                    ThingSpeak_update(temperature, rh)
                if device['type'] == 'boiler':
                    now = datetime.datetime.now()
                    date = datetime.datetime.today().strftime('%Y-%m-%d')
                    curr_hour = "{}:{}".format(str(now.hour).zfill(2), str(now.minute).zfill(2))
                    mode = ord(data['rf_data'][1])
                    status = {'mode' : str(mode),
                              'time' : curr_hour,
                              'date' : date
                              }
                if device['type'] == 'air_conditioner':
                    status = {'on_off' : ('false' if data['rf_data'][1] == '\x01' else 'true') }
                if status is not None:
                    self.status_updater.update_device_status(device, status)

    def close(self):
        self.xbee.halt()
        self.serial_port.close()


    def update_shutter(self, addr, device_number, args):
        shutter_options = {'100': '\x01',
                           '0': '\x02',
                           'pause': '\x03',
                           '25': '\x04',
                           '50': '\x05',
                           '75': '\x06',
                           }
        data = shutter_options[args['mode']]
        self.xbee.send('tx',
                       frame_id='A',
                       dest_addr=addr,
                       options='\x00',
                       data=(chr(device_number)+data))


    def update_shutterNew(self, addr, device_number, args):
        data = "\x02" if args['mode'] == 'pause' else ("\x01" + chr(int(args['mode'])))
        self.xbee.send('tx',
                       frame_id='A',
                       dest_addr=addr,
                       options='\x00',
                       data=(chr(device_number)+data))

    def update_boiler(self, addr, device_number, args):
        data = chr(int(args['mode']))
        self.xbee.send('tx',
                       frame_id='A',
                       dest_addr=addr,
                       options='\x00',
                       data=(chr(device_number)+data))

    def update_temperature(self, addr, device_number, args):
        data = 0


    def update_air_conditioner(self, addr, device_number, args):
        data = calc_ac_message(args, self.logger)
        self.xbee.send('tx',
                       frame_id='A',
                       dest_addr=addr,
                       options='\x00',
                       data=(chr(device_number)+chr(1)+data))


    def set_status_updater(self, status_updater):
        self.status_updater = status_updater


    def set_logger(self, logger):
        self.logger = logger


class DummyRadio:
    def __init__(self):
        print "Starting DummyRadio..."

    def close(self):
        self.logger.info("Bye Bye")

    def update_shutter(self, addr, device_number, args):
        self.logger.info("shutter={},{} args={}".format(addr, device_number, args))

    def update_shutterNew(self, addr, device_number, args):
        self.logger.info("shutterNew={},{} args={}".format(addr, device_number, args))

    def update_air_conditioner(self, addr, device_number, args):
        self.logger.info("air conditioner={},{}, args={}".format(addr, device_number, args))
        calc_ac_message(args, self.logger)

    def set_status_updater(self, status_updater):
        self.status_updater = status_updater

    def set_logger(self, logger):
        self.logger = logger