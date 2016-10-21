from threading import Thread
import paho.mqtt.client as mqtt

class MQTT:

    @staticmethod
    def connect_to_broker(client, broker, topic,  port):

        client.connect(broker, port, 60)
        client.subscribe(topic)
        print("connected to broker. subscribed to "+str(topic))
        client.loop_forever()

    @staticmethod
    def on_message(self, userdata, msg):
        print(msg.topic+" "+str(msg.payload))

    def publish_1(client,topic):
        message="MQTT Client started on Raspberry Pi"
        print("publish data")
        client.publish(topic,message)


    def __init__(self, broker, port, topic_sub, logger):
        self = mqtt.Client()
        self.on_message = MQTT.on_message
        self.broker = broker
        self.port = port
        self.topic_sub = topic_sub
        self.logger = logger
        self.stop_event = None
        self.thread =  Thread(target=MQTT.connect_to_broker,args=(self, self.broker, self.topic_sub, self.port))
        self.thread.start()


