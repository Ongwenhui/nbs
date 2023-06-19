try:
    from ltr559 import LTR559
    ltr559 = LTR559()
except ImportError:
    import ltr559

from enviroplus import gas
import logging
from datetime import datetime as dt
import time
import csv
import json
import requests

# gpsusb retrieves the latitude and longitude from the gps receiver
import gpsusb

'''
AWS stuff
'''
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder

# AWS definitions

ENDPOINT = "a5i03kombapo4-ats.iot.ap-southeast-1.amazonaws.com"
CLIENT_ID = "enviropluspi"
PATH_TO_CERTIFICATE = "datalogging2/examples/certificates/8fe7b27e3f68b573b56f42001dbb5406cd8630a484ad0509144631cde31dc6f6-certificate.pem.crt"
PATH_TO_PRIVATE_KEY = "datalogging2/examples/certificates/8fe7b27e3f68b573b56f42001dbb5406cd8630a484ad0509144631cde31dc6f6-private.pem.key"
PATH_TO_AMAZON_ROOT_CA_1 = "datalogging2/examples/certificates/root.pem"
TOPIC = "test/dataloggingwithgps"

# AWS

# Spin up resources
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
# Future.result() waits until a result is available
connect_future.result()
print("Connected!")
# Publish message to server desired number of times.
print('Enviro+ Air Quality Datalogging')

MESSAGE = "test message"
mqtt_connection.publish(topic=TOPIC, payload=json.dumps(MESSAGE), qos=mqtt.QoS.AT_LEAST_ONCE)

data = {}