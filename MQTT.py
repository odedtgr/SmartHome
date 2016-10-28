import paho.mqtt.client as mqtt
import json
import ast
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
                #convert the string to dict
                status = json.dumps(msg.payload)
                status = json.loads(status)
                status = ast.literal_eval(status)
            if status is not None:
                self.status_updater.update_device_status(device, status)

    def publish(self,topic, payload):
        self.client.publish(topic,payload)


    def __init__(self, broker, port, topic_sub, topic_pub, device_manager, logger):
        client = mqtt.Client()
        client.status_updater = StatusUpdater(device_manager)
        client.on_message = MQTT.on_message
        self.client = client
        self.broker = broker
        self.port = port
        self.topic_sub = topic_sub
        self.topic_pub = topic_pub
        self.logger = logger
        self.stop_event = None

        MQTT.connect_to_broker(self.client, self.broker, self.topic_sub, self.port)
        device_manager.add_mqtt_client(self)
        #MQTT.publish(self,'HomeWise/out', 'out message')

	def set_status_updater(self, status_updater):
		self.status_updater = status_updater