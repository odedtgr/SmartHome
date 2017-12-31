class Settings:
    release = "https://cdn.rawgit.com/odedtgr/SmartHome/1.6/static/"

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

    MQTT_BROKER = '127.0.0.1'
    MQTT_TOPIC_SUB = "HomeWise/from/"
    MQTT_TOPIC_PUB = "HomeWise/to/"
    HOMEKIT_NAME = "homekit"

    MQTT_PORT = 1883

    RADIO_CLASS	= 'Radio'
    FRAME_ID = 'A'
    GROUP_DEVICES = ['ALL SHUTTERS']

    DEVICES = [
       # {
       #      'id':           0,
       #      'name': 	    'Temperature',
       #      'type': 	    'temperature',
       #      'address':      '\x00\x04',
       #      'number':       2,
       #      'last_config':  {'Temp':0}
       #  },
	    {
            'id':           0,
            'name': 	    'Living room window',
            'type': 	    'shutterNew',
            'address':      '\x00\x05',
            'number':       1,
            'last_config':  {'mode': '100'}
        },
	    {
            'id':           1,
            'name': 	    'Bedroom window',
            'type': 	    'shutterNew',
            'address':      '\x00\x04',
            'number':       1,
            'last_config':  {'mode': '100'}
        },
        {
            'id':           2,
            'name': 	    'Living room Air Conditioner',
            'type': 	    'air_conditioner',
            'address':      '\x00\x06',
            'number':       1,
            'last_config':  {'fan': '1', 'on_off': 'false', 'temp': '25', 'mode': 'cool'}
        },
        {   'id':           3,
            'name': 	    'Rooms Air Conditioner',
            'type': 	    'air_conditioner',
            'address':      '\x00\x06',
            'number':       2,
            'last_config':  {'fan': '1', 'on_off': 'false', 'temp': '25', 'mode': 'cool'}
        },
        {
            'id':           4,
            'name': 	    'Water Heater',
            'type': 	    'boiler',
            'address':      '\x00\x07',
            'number':       1,
            'last_config':  {'mode': '0', 'Temp': '0'}
        },
        {
            'id': 5,
            'name': 'Water temperature',
            'type': 'boiler_temperature',
            'address': '\x00\x07',
            'number': 2,
            'last_config': {'Temp': '0'}
        },
        {
            'id':           6,
            'name': 	    'Twins room window',
            'type': 	    'shutterNew',
            'address':      '\x00\x02',
            'number':       1,
            'last_config':  {'mode': '100'}
        },
        {
            'id':           7,
            'name': 	    'TV Light',
            'type': 	    'light',
            'protocol':     'mqtt',
            'address':      'WiFiSwitch-9f-d6-53',
            'number':       1,
            'last_config':  {'device_on': 'false'}
        },
        {
            'id': 8,
            'name': 'TV',
            'show_in_devices' : 'false',
            'type': 'samsung_tv',
            'protocol': 'api',
            'address': '192.168.1.40',
            'mac':'5C:49:7D:1C:E3:BB',
            'number': 1,
            'last_config': {'key': 'KEY_POWER'}
        }

    ]

    SCHEDULER = [

    ]
	
    SCENARIOS = [
        {'name' : 'Close living room',
            'tasks':[
                {
                'name': 'Living Room Shutter',
                'args' : {'mode' : '0'}
                },
                {
                'name': 'Test Light',
                'args': {'device_on': 'false'}
                },
                {
                    'name': 'TV',
                    'args': {'key': 'KEY_POWER'}
                }

            ]
        },
        {'name': 'Open all windows',
             'tasks': [
                {
                 'name': 'Living Room Shutter',
                 'args': {'mode': '100'}
                },
                {
                 'name': 'Bedroom Shutter',
                 'args': {'mode': '100'}
                },
                {
                 'name': 'Twins room Shutter',
                 'args': {'mode': '100'}
                }

            ]
         }
    ]