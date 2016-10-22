from threading import Thread
import paho.mqtt.client as mqtt
from device_manager import StatusUpdater as StatusUpdater

class MQTT:

    @staticmethod
    def connect_to_broker(client, broker, topic,  port):

        client.connect(broker, port, 60)
        client.subscribe(topic)
        print("connected to broker. subscribed to "+str(topic))
        client.loop_start()

    @staticmethod
    def on_message(self, userdata, msg):
        print(msg.topic+" "+str(msg.payload))
        #get the device address from the topic by finding '/'  Ex HomeWise/test_device
        slash_pos = msg.topic.index('/')
        device_address = msg.topic[slash_pos+1:len(msg.topic)]
        device = self.status_updater.get_device_by_address(device_address, 1)

        if device is not None:
            if device['type'] == 'light':
                status = {'mode' : msg.payload}
            if status is not None:
                self.status_updater.update_device_status(device, status)

    def publish_1(client,topic):
        message="MQTT Client started on Raspberry Pi"
        print("publish data")
        client.publish(topic,message)


    def __init__(self, broker, port, topic_sub, device_manager, logger):
        self = mqtt.Client()
        self.on_message = MQTT.on_message
        self.broker = broker
        self.port = port
        self.topic_sub = topic_sub
        self.logger = logger
        self.stop_event = None
        self.status_updater = StatusUpdater(device_manager)
        MQTT.connect_to_broker(self, self.broker, self.topic_sub, self.port)

	def set_status_updater(self, status_updater):
		self.status_updater = status_updater