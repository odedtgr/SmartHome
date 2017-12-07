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

        if device_address[0:len("homekit")]=="homekit":
            slash_pos = device_address.index('/')
            device_address = device_address[slash_pos+1:len(device_address)]
            device = self.status_updater.get_device_by_name(device_address, 1)
            if device is not None:
                device_id = device['id']
                # convert the string to dict
                status = json.dumps(msg.payload)
                status = json.loads(status)
                status = ast.literal_eval(status)
                if status is not None:
                    device_type = device['type']
                    if device_type == 'shutterNew':
                        status = {"mode": str(status)}
                    elif device_type == 'boiler':
                        status = {"mode": str(status)}

                    self.device_manager.update_device(device_id, status, False)

        else:
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


    def __init__(self, broker, port, topic_sub, topic_pub, homekit_name, device_manager, logger):
        client = mqtt.Client()
        client.status_updater = StatusUpdater(device_manager)
        client.device_manager = device_manager
        client.on_message = MQTT.on_message
        self.client = client
        self.broker = broker
        self.port = port
        self.topic_sub = topic_sub
        self.topic_pub = topic_pub
        self.homekit_name = homekit_name
        self.logger = logger
        self.stop_event = None

        MQTT.connect_to_broker(self.client, self.broker, self.topic_sub, self.port)
        device_manager.add_mqtt_client(self)
        #MQTT.publish(self,'HomeWise/out', 'out message')

	def set_status_updater(self, status_updater):
		self.status_updater = status_updater