import serial
from xbee import XBee     
def handle_data(data): print "receiving data {}".format(data)

serial_port = serial.Serial('/dev/ttyAMA0', 9600)
xbee = XBee(serial_port, callback=handle_data)
xbee.send('tx', frame_id='A', dest_addr='\x00\x02', options='\x00', data=(chr(1)+'\x00'))

#xbee.halt()
#serial_port.close()


