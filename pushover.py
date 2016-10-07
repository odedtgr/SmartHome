import httplib, urllib
from settings import Settings
import datetime

def pushover_update(title, message, priority):
    conn = httplib.HTTPSConnection("api.pushover.net:443")

    try:
        conn.request("POST", "/1/messages.json",
                     urllib.urlencode({
                         "token": Settings.PUSHOVER_TOKEN,
                         "user": Settings.PUSHOVER_USER,
                         "title": title,
                         "message": message,
                         "priority": priority,
                         "retry": "30",
                         "expire": "360",
                         "url" : "http://oded.noip.me:8000",
                         "url_title": "HomeWise"
                     }), {"Content-type": "application/x-www-form-urlencoded"})
        response = conn.getresponse()
        print "[{}] -".format(datetime.datetime.now()), "Pushover POST: ", title, ", ", message, ", Response: ", response.status, response.reason
        data = response.read()
        conn.close()
    except:
        print "[{}] -".format(datetime.datetime.now()), "Pushover POST Failed"

