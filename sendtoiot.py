import sys


import logging
from datetime import datetime as dt
import time
import csv
import json
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder

for value in values:
    print(value)
ID = values[0]
onoff = values[1]
unixtime = str(dt.now())
dict = {"ID": ID, "onoff" : onoff, "unixtime": unixtime}
print(dict)

ENDPOINT = "a5i03kombapo4-ats.iot.ap-southeast-1.amazonaws.com"
CLIENT_ID = "enviropluspi"
PATH_TO_CERTIFICATE = "9972587da4767d10db7001fc18bab5b9124945c4762ebf246b6266e08352970b-certificate.pem.crt"
PATH_TO_PRIVATE_KEY = "9972587da4767d10db7001fc18bab5b9124945c4762ebf246b6266e08352970b-private.pem.key"
PATH_TO_AMAZON_ROOT_CA_1 = "root.pem"
TOPIC = "test/nbs"

event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=ENDPOINT,
            cert_filepath=PATH_TO_CERTIFICATE,
            pri_key_filepath=PATH_TO_PRIVATE_KEY,
            client_bootstrap=client_bootstrap,
            ca_filepath=PATH_TO_AMAZON_ROOT_CA_1,
            client_id=CLIENT_ID,
            clean_session=False,
            keep_alive_secs=6
            )
print("Connecting to {} with client ID '{}'...".format(
        ENDPOINT, CLIENT_ID))
# Make the connect() call
connect_future = mqtt_connection.connect()
connect_future.result()
print("Connected!")
# Publish message to server desired number of times.
mqtt_connection.publish(topic=TOPIC, payload=json.dumps(dict), qos=mqtt.QoS.AT_LEAST_ONCE)
print('done')
