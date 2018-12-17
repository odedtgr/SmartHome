import paho.mqtt.client as mqtt
import json
import ast

class MQTT:

    @staticmethod
    def connect_to_broker(client, broker, topic,  port):

        client.connect(broker, port, 60)
        client.subscribe(topic, qos=2)
        print("connected to broker. subscribed to "+str(topic))
        client.loop_start()

    @staticmethod
    def on_message(self, userdata, msg):
        print(msg.topic+" "+str(msg.payload))
        #get the device address from the topic by finding '/'  Ex HomeWise/test_device
        message = msg.topic.split('/')
        source_device_name = message[2]

        # convert the string to dict
        status = json.dumps(msg.payload)
        status = json.loads(status)
        status = ast.literal_eval(status)

        if source_device_name == self.homekit_name:
            homekit_device_name = message[3]
            command = message[4]
            device = self.device_manager.get_device_by_name(homekit_device_name)

            if device is not None:
                if status is not None:
                    device.handle_message_from_homekit(command, status)

        else:
            device = self.device_manager.get_device_by_name(source_device_name)
            if device is not None:
                device.handle_message_from_device(status)


    def publish(self,topic, payload):
        self.client.publish(topic,payload, qos=2)

    def update_homebridge(self, device):
        if device.type == 'ShutterNew':
            val = device.last_config.get('mode')
            payload = '{"val":"' + val + '"}'
            topic = 'statusCurrentPosition'
            str_to_publish = self.topic_pub + self.client.homekit_name + '/' + device.name + '/' + topic
            self.client.publish(str_to_publish, payload)

            payload = '{"val":"0"}'
            topic = 'statusPositionState'
            str_to_publish = self.topic_pub + self.client.homekit_name + '/' + device.name + '/' + topic
            self.client.publish(str_to_publish, payload)

        if device.type == 'Boiler':
            val = device.last_config.get('mode')
            if val != '0':
                val = '4'
            payload = '{"val":"' + val + '"}'
            topic = 'statusOn'
            str_to_publish = self.topic_pub + self.client.homekit_name + '/' + device.name + '/' + topic
            self.client.publish(str_to_publish, payload)

            val = device.last_config.get('Temp')
            val = float(val)
            val = val * 9 / 5 + 32
            val = str(val)
            payload = '{"val":"' + val + '"}'
            topic = 'statusTemperature'
            str_to_publish = self.topic_pub + self.client.homekit_name + '/' + device.name + '/' + topic
            self.client.publish(str_to_publish, payload)

        if device.type == 'AirConditioner':
            if device.last_config.get('device_on') == 'false':
                payload = '{"val":"0"}'
            else:
                payload = '{"val":"1"}'
            topic = 'statusOn'
            str_to_publish = self.topic_pub + self.client.homekit_name + '/' + device.name + '/' + topic
            self.client.publish(str_to_publish, payload)

            if device.last_config.get('device_on') == 'false':
                val = '0'
            elif device.last_config.get('mode') == 'heat':
                val = '1'
            else:
                val = '2'
            payload = '{"val":"' + val + '"}'
            topic = 'statusCurrentHeatingCoolingState'
            str_to_publish = self.topic_pub + self.client.homekit_name + '/' + device.name + '/' + topic
            self.client.publish(str_to_publish, payload)

            val = device.last_config.get('temp')
            payload = '{"val":"' + val + '"}'
            topic = 'statusTargetTemperature'
            str_to_publish = self.topic_pub + self.client.homekit_name + '/' + device.name + '/' + topic
            self.client.publish(str_to_publish, payload)

        if device.type == 'Light':
            if device.last_config.get('device_on') == 'true':
                payload = '{"val":"1"}'
            else:
                payload = '{"val":"0"}'
            topic = 'statusOn'
            str_to_publish = self.topic_pub + self.client.homekit_name + '/' + device.name + '/' + topic
            self.client.publish(str_to_publish, payload)


    def __init__(self, broker, port, topic_sub, topic_pub, homekit_name, device_manager, logger):
        client = mqtt.Client()
        client.topic_sub = topic_sub
        client.homekit_name = homekit_name
        client.device_manager = device_manager
        client.on_message = MQTT.on_message
        self.client = client
        self.broker = broker
        self.port = port
        self.topic_sub = topic_sub
        self.topic_pub = topic_pub
        self.logger = logger
        self.stop_event = None

        topic_sub = self.topic_sub +'#'

        MQTT.connect_to_broker(self.client, self.broker, topic_sub, self.port)
        device_manager.add_mqtt_client(self)