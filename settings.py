class Settings:
    HOME_NAME = "Tagar"
    users = {"Oded":"Stamir47",
             "Maya":"Stamir47"}
    HOST = '0.0.0.0'
    PORT = 8000
    DEVICES_FILENAME = "devices.txt"
    SCHEDULER_FILENAME = "scheduler.txt"
    DEBUG = True
    scheduler_on = True

    PUSHOVER_TOKEN = "axmtczbsd59efkn72f8eab2gqj5cp8"
    PUSHOVER_USER = "u5gp6d5gahzggd6ifg14d3idmtm9ug"

    THING_SPEAK_KEY = 'GJR2UBQ6G8UDCKQL'

    MQTT_BROKER = 'localhost'
    MQTT_TOPIC_SUB = "HomeWise/#"
    MQTT_TOPIC_PUB = "HomeWise"

    MQTT_PORT = 1883

    RADIO_CLASS	= 'Radio'
    FRAME_ID = 'A'
    GROUP_DEVICES = ['ALL SHUTTERS']

    DEVICES = [
        {
            'id':           0,
            'name': 	    'Temperature',
            'type': 	    'temperature',
            'address':      '\x00\x04',
            'number':       2,
            'last_config':  {'Temp':0}
        },
	{
            'id':           1,
            'name': 	    'Living Room Shutter',
            'type': 	    'shutter',
            'address':      '\x00\x05',
            'number':       1,
            'last_config':  {'mode': '100'}
        },
	{
            'id':           2,
            'name': 	    'Bedroom Shutter',
            'type': 	    'shutterNew',
            'address':      '\x00\x04',
            'number':       1,
            'last_config':  {'mode': '100'}
        },
        {
            'id':           3,
            'name': 	    'Living Air Conditioner',
            'type': 	    'air_conditioner',
            'address':      '\x00\x06',
            'number':       1,
            'last_config':  {'fan': '1', 'on_off': 'false', 'temp': '25', 'mode': 'cool'}
        },
        {   'id':           4,
            'name': 	    'Rooms Air Conditioner',
            'type': 	    'air_conditioner',
            'address':      '\x00\x06',
            'number':       2,
            'last_config':  {'fan': '1', 'on_off': 'false', 'temp': '25', 'mode': 'cool'}
        },
        {
            'id':           5,
            'name': 	    'Water Heater',
            'type': 	    'boiler',
            'address':      '\x00\x03',
            'number':       1,
            'last_config':  {'mode': '0'}
        }
    ]

    SCHEDULER = [

    ]
	
