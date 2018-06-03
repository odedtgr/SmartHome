import paho.mqtt.client as mqtt
import json
import ast
from device_manager import StatusUpdater as StatusUpdater


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
        message = msg.topic
        slash_pos = message.index('/')
        message = message[slash_pos + 1:len(message)]
        slash_pos = message.index('/')
        message = message[slash_pos + 1:len(message)]
        device_name = message

        if message.find(self.homekit_name)==0:
            slash_pos = message.index('/')
            message = message[slash_pos + 1:len(message)]
            slash_pos = message.index('/')
            command = message[slash_pos+1:len(message)]
            device_name = message[0:slash_pos]
            device = self.status_updater.get_device_by_name(device_name)

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

                    elif device_type == 'light':
                        if status :
                            status = {"device_on":"true"}
                        else:
                            status = {"device_on": "false"}

                    elif device_type == 'air_conditioner':
                        if command == 'setTargetTemperature':
                            status = {"temp": str(status)}


                        elif command == 'setTargetHeatingCoolingState':
                            currently_on = device['last_config'].get("on_off") == "true"
                            desired_on = str(status) != '0'
                            on_off_changed = 'true'
                            if desired_on == currently_on:
                                on_off_changed = 'false'

                            if str(status) == '0':
                                status = {"on_off-changed":on_off_changed}
                            elif str(status) == '1':
                                status = {"on_off-changed":on_off_changed, "mode":"heat"}
                            else :
                                status = {"on_off-changed":on_off_changed, "mode": "cool"}

                        elif command == 'setOn':
                            currently_on = device['last_config'].get("on_off") == "true"
                            desired_on = str(status) != '0'
                            on_off_changed = 'true'
                            if desired_on == currently_on:
                                on_off_changed = 'false'
                            status = {"on_off-changed": on_off_changed}

                    for k, v in device['last_config'].items():
                        if k not in status:
                            status[k] = v

                    self.device_manager.update_device(device_id, status, False)


        else:
            device = self.status_updater.get_device_by_name(device_name)

            if device is not None:
                if device['type'] == 'light':
                    #convert the string to dict
                    status = json.dumps(msg.payload)
                    status = json.loads(status)
                    status = ast.literal_eval(status)
                if status is not None:
                    self.status_updater.update_device_status(device, status)


    def publish(self,topic, payload):
        self.client.publish(topic,payload, qos=2)

    def update_homebridge(self, device):
        device_name = device['name']
        if device['type'] == 'shutterNew':
            val = device['last_config'].get('mode')
            payload = '{"val":"' + val + '"}'
            topic = 'statusCurrentPosition'
            str_to_publish = self.topic_pub + self.client.homekit_name + '/' + device['name'] + '/' + topic
            self.client.publish(str_to_publish, payload)

            payload = '{"val":"0"}'
            topic = 'statusPositionState'
            str_to_publish = self.topic_pub + self.client.homekit_name + '/' + device['name'] + '/' + topic
            self.client.publish(str_to_publish, payload)

        if device['type'] == 'boiler':
            val = device['last_config'].get('mode')
            if val != '0':
                val = '4'
            payload = '{"val":"' + val + '"}'
            topic = 'statusOn'
            str_to_publish = self.topic_pub + self.client.homekit_name + '/' + device['name'] + '/' + topic
            self.client.publish(str_to_publish, payload)

            val = device['last_config'].get('Temp')
            val = float(val)
            val = val * 9 / 5 + 32
            val = str(val)
            payload = '{"val":"' + val + '"}'
            topic = 'statusTemperature'
            str_to_publish = self.topic_pub + self.client.homekit_name + '/' + device['name'] + '/' + topic
            self.client.publish(str_to_publish, payload)

        if device['type'] == 'air_conditioner':
            if device['last_config'].get('on_off') == 'false':
                payload = '{"val":"0"}'
            else:
                payload = '{"val":"1"}'
            topic = 'statusOn'
            str_to_publish = self.topic_pub + self.client.homekit_name + '/' + device['name'] + '/' + topic
            self.client.publish(str_to_publish, payload)

            if device['last_config'].get('on_off') == 'false':
                val = '0'
            elif device['last_config'].get('mode') == 'heat':
                val = '1'
            else:
                val = '2'
            payload = '{"val":' + val + '}'
            topic = 'statusTargetHeatingCoolingState'
            str_to_publish = self.topic_pub + self.client.homekit_name + '/' + device['name'] + '/' + topic
            self.client.publish(str_to_publish, payload)

            val = device['last_config'].get('temp')
            payload = '{"val":' + val + '}'
            topic = 'statusTargetTemperature'
            str_to_publish = self.topic_pub + self.client.homekit_name + '/' + device['name'] + '/' + topic
            self.client.publish(str_to_publish, payload)

        if device['type'] == 'light':
            if device['last_config'].get('device_on') == 'true':
                payload = '{"val":"1"}'
            else:
                payload = '{"val":"0"}'
            topic = 'statusOn'
            str_to_publish = self.topic_pub + self.client.homekit_name + '/' + device['name'] + '/' + topic
            self.client.publish(str_to_publish, payload)


    def __init__(self, broker, port, topic_sub, topic_pub, homekit_name, device_manager, logger):
        client = mqtt.Client()
        client.topic_sub = topic_sub
        client.homekit_name = homekit_name
        client.status_updater = StatusUpdater(device_manager)
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
        #MQTT.publish(self,'HomeWise/out', 'out message')