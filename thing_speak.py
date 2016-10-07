import httplib, urllib
from settings import Settings
import datetime


def ThingSpeak_update(temperature, rh):
    params = urllib.urlencode({'field1': temperature,
                               'field2': rh,
                               'key': Settings.THING_SPEAK_KEY})  # use your API key generated in the thingspeak channels for the value of 'key'
    headers = {"Content-typZZe": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    conn = httplib.HTTPConnection("api.thingspeak.com:80")
    try:
        conn.request("POST", "/update", params, headers)
        response = conn.getresponse()
        print "[{}] -".format(datetime.datetime.now()), "ThingSpeak POST: ", temperature, ", ", rh, ",Response: ", response.status, response.reason

        data = response.read()
        conn.close()
    except:
        print "[{}] -".format(datetime.datetime.now()), "ThingSpeak POST failed"

