import sys
import logging
from datetime import datetime as dt
import time
import csv
import json
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
from awsiot import iotshadow
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
from uuid import uuid4

def on_get_shadow_accepted(response):
    if response:
        print(response)
    
def get_accepted_responses():
    print("Subscribing to Get responses...")
    get_accepted_subscribed_future, a = shadow_client.subscribe_to_get_named_shadow_accepted(
        request=iotshadow.GetNamedShadowSubscriptionRequest(shadow_name = shadow_name, thing_name = thing_name),
        qos=mqtt.QoS.AT_LEAST_ONCE,
        callback=on_get_shadow_accepted)
    get_accepted_subscribed_future.result()
    time.sleep(0.1)
    
ENDPOINT = "a5i03kombapo4-ats.iot.ap-southeast-1.amazonaws.com"
CLIENT_ID = "enviropluspi"
PATH_TO_CERTIFICATE = "/Users/ongwenhui/Desktop/certs/testcode/nbsiot/9972587da4767d10db7001fc18bab5b9124945c4762ebf246b6266e08352970b-certificate.pem.crt"
PATH_TO_PRIVATE_KEY = "/Users/ongwenhui/Desktop/certs/testcode/nbsiot/9972587da4767d10db7001fc18bab5b9124945c4762ebf246b6266e08352970b-private.pem.key"
PATH_TO_AMAZON_ROOT_CA_1 = "/Users/ongwenhui/Desktop/certs/testcode/nbsiot/root.pem"

thing_name = "WenhuiAWSthing"
shadow_name = "mqttnbs"

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
connected_future = mqtt_connection.connect()
shadow_client = iotshadow.IotShadowClient(mqtt_connection)
print("Connecting to {} with client ID '{}'...".format(
        ENDPOINT, CLIENT_ID))
connected_future.result()
# Make the connect() call
print("Connected!")

while True:
    get_accepted_responses()


