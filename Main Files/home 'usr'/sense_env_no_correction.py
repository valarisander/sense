#!/usr/bin/python

from sense_hat import SenseHat
#The AWSIOT from/import is only needed if you are using the MQTT protocol
#from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient 
from requests.utils import DEFAULT_CA_BUNDLE_PATH;
import time
import os
import urllib2
import requests
import base64
import logging
import argparse
import json

#data recording for averages
SENSE_ATTEMPT = 3
temp_running_total = 0
humi_running_total = 0
press_running_total = 0

#pixel display configuration
sense = SenseHat()
sense.set_rotation(90)
deco = (155, 000, 155)
teco = (255, 000, 000)
heco = (000, 000, 255)
peco = (000, 255, 000)

#data recording block for base data.
for count in range(SENSE_ATTEMPT):
    humi = round(sense.get_humidity(),2)
    time.sleep(0.1)
    humi_running_total += humi
    #print("Humidity: %s %%rH" % humi)
    temp = round(sense.get_temperature(),2)
    time.sleep(0.1)
    temp_running_total += temp
    #print("Temperature: %s C" %temp)
    press = round(sense.get_pressure(),2)
    time.sleep(0.1)
    press_running_total += press
    #print("Pressure: %s Millibars" %press)

#finding the average reading to self-check for bad reading
    #display the avg_records
ave_temp = temp_running_total/SENSE_ATTEMPT
#temp_string = str(round(ave_temp, 2))
temp_string = "ave_temp:"+ str(round(ave_temp,2))
#sense.show_message(temp_string, text_colour=teco)

ave_humi = humi_running_total/SENSE_ATTEMPT
#humi_string = str(round(ave_humi, 2))
humi_string = "ave_humi:"+ str(round(ave_humi,2))
#sense.show_message(humi_string, text_colour=heco)

ave_press = press_running_total/SENSE_ATTEMPT
#press_string = str(round(ave_press, 2))
press_string = "ave_pres:"+ str(round(ave_press,2))
#sense.show_message(press_string, text_colour=peco)

#display record sending notice
sense.show_message("SENDING", text_colour=deco)

#format data for record sending
dbtemp= "%.1f" %temp
dbhumi="%.1f" %humi
dbpres= "%.1f" %press

##call to server for SQL insert##
url = ("http://"website/ip address":81/add_data.php?temp="+dbtemp+"&humi="+dbhumi+"&pres="+dbpres)
username = 'username'
password = 'password'
print(requests.get(url, auth=(username, password)).content)
class PreemptiveBasicAuthHandler(urllib2.HTTPBasicAuthHandler):
    def http_request(self, req):
        url = req.get_full_url()
        realm = None
        user, pw = self.passwd.find_user_password(realm, url)
        if pw:
            raw = "%s:%s" % (user, pw)
            auth = 'Basic %s' % base64.b64encode(raw).strip()
            req.add_unredirected_header(self.auth_header, auth)
        return req
    https_request = http_request
auth_handler = PreemptiveBasicAuthHandler()
auth_handler.add_password(
    realm=None, # default realm.
    uri=url,
    user=username,
    passwd=password)
opener = urllib2.build_opener(auth_handler)
urllib2.install_opener(opener)



##End of sense_env operational script##


##This rest of this sript is for publishing to the choosen MQTT topic and is not needed for the my sql updates to work##

##########################################################################################################################
##MQTT heartbeat##
sense_data=(temp_string,humi_string,press_string)

##AWS supplied script, modified to publish data once per cycle,##
AllowedActions = ['both', 'publish', 'subscribe']

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic:")
    print(message.topic)
    print("--------------\n\n")

# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub",
                    help="Targeted client id")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="sdk/test/Python", help="Targeted topic")
parser.add_argument("-m", "--mode", action="store", dest="mode", default="both",
                    help="Operation modes: %s"%str(AllowedActions))
parser.add_argument("-M", "--message", action="store", dest="message", default=sense_data,
                    help="Message to publish")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
port = args.port
useWebsocket = args.useWebsocket
clientId = args.clientId
topic = args.topic

if args.mode not in AllowedActions:
    parser.error("Unknown --mode option %s. Must be one of %s" % (args.mode, str(AllowedActions)))
    exit(2)

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
    parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    parser.error("Missing credentials for authentication.")
    exit(2)

# Port defaults
if args.useWebsocket and not args.port:  # When no port override for WebSocket, default to 443
    port = 443
if not args.useWebsocket and not args.port:  # When no port override for non-WebSocket, default to 8883
    port = 8883

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
if args.mode == 'both' or args.mode == 'subscribe':
    myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)
time.sleep(2)

# Publish to the mqtt topic
if args.mode == 'both' or args.mode == 'publish':
        message = {}
        message['message'] = args.message
        messageJson = json.dumps(message)
        myAWSIoTMQTTClient.publish(topic, messageJson, 1)
        if args.mode == 'publish':
            print('Published topic %s: %s\n' % (topic, messageJson))
##End of Code##