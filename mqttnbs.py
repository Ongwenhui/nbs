'''
Important notes: soundlooper() -> keeps playmasker() running
playmasker() -> plays selected masker from predictions
'''

import json
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
#from PIL import Image
from io import BytesIO
import numpy as np
import sounddevice as sd 
import soundfile as sf
import time 
import queue
import sys
import threading
import math
import csv
import pandas as pd
import random
from pydub import AudioSegment
import keyboard
import sys
import tty
import termios
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder

varymaskers = False
MEOW = False

calibjsonpath = "/home/pi/mqtt_client/calib.json"

def interpolate(masker,gain):
    f = open(calibjsonpath, "r")
    # calib = f.read()
    # print(calib)
    calib = json.load(f)
    # # calib = json.loads(f.read())
    keepgoing = True
    counter = 0
    chosengain = 0
    while keepgoing == True:
        currval = abs(gain - calib[masker][counter])
        if counter < (len(calib[masker])-1):
            nextval = abs(gain - calib[masker][counter + 1])
        else: 
            nextval = abs(gain - calib[masker][0])
        if nextval >= currval:
            keepgoing = False
            chosengain = calib[masker][counter]
        if counter < (len(calib[masker])-1):
            counter += 1
        else:
            counter = 0
    if counter>0: 
        finaldb = counter -1 + 46
    else:
        finaldb = 46+37

    # print("chosengain = {}".format(chosengain))
    # print("counter -1 = {}".format(counter -1))
    return finaldb

def readcsv(csvfile):
    calibgains = {}
    with open(csvfile, 'r') as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        for row in csvreader:
            entrycount = 0
            currmasker = ""
            nextgain = 0
            for entry in row:
                if entrycount == 0:
                    calibgains[entry] = {}
                    currmasker = entry
                elif entrycount != 0 and (entrycount % 2) != 0:
                    nextgain = float(entry)
                elif entrycount != 0 and (entrycount % 2) == 0:
                    calibgains[currmasker][str(int(round(float(entry))))] = nextgain 
                entrycount += 1
    return calibgains

calibgains = readcsv('/home/pi/mqtt_client/Calibrations_final_speaker.csv')

# mqttENDPOINT = "a5i03kombapo4-ats.iot.ap-southeast-1.amazonaws.com"
# mqttCLIENT_ID = "AIMEGET"
# mqttcertfolder = "/home/pi/mqtt_client/certs/"
# mqttPATH_TO_CERTIFICATE = mqttcertfolder + "c86008d5f6f3eb115159777ba9da6c0b97bfdf2309c15020c8d1d2747e4f6bdc-certificate.pem.crt"
# mqttPATH_TO_PRIVATE_KEY = mqttcertfolder + "c86008d5f6f3eb115159777ba9da6c0b97bfdf2309c15020c8d1d2747e4f6bdc-private.pem.key"
# mqttPATH_TO_AMAZON_ROOT_CA_1 = mqttcertfolder + "AmazonRootCA1.pem"
# mqttTOPIC = "amss/prediction"
# mqttRANGE = 20

LOCATION_ID = 'PWP'
optimaldistance = 1 #Punggol MSCP
numofspeakers = 4
class soundplayer:
    def __init__(self):
        self.mqttENDPOINT="a5i03kombapo4-ats.iot.ap-southeast-1.amazonaws.com"
        self.mqttCLIENT_ID= "AIMEGET"
        self.mqttcertfolder="/home/pi/mqtt_client/certs/"
        self.mqttPATH_TO_CERTIFICATE = self.mqttcertfolder + "c86008d5f6f3eb115159777ba9da6c0b97bfdf2309c15020c8d1d2747e4f6bdc-certificate.pem.crt"
        self.mqttPATH_TO_AMAZON_ROOT_CA_1 = self.mqttcertfolder + "AmazonRootCA1.pem"
        self.mqttPATH_TO_PRIVATE_KEY=self.mqttcertfolder + "c86008d5f6f3eb115159777ba9da6c0b97bfdf2309c15020c8d1d2747e4f6bdc-private.pem.key"
        self.mqttTOPIC="amss/{}/prediction".format(LOCATION_ID)
        self.mqttRANGE=20
        self.currentdoa = 90
        self.MQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(self.mqttCLIENT_ID)
        self.MQTTClient.configureEndpoint(self.mqttENDPOINT, 8883)
        self.MQTTClient.configureCredentials(self.mqttPATH_TO_AMAZON_ROOT_CA_1, self.mqttPATH_TO_PRIVATE_KEY, self.mqttPATH_TO_CERTIFICATE)
        # self.msgdict = {'predictions': [{'rank': 1, 'id': 'bird_00075', 'gain': 0.01793866604566574, 'score': 0.47396957874298096}, {'rank': 2, 'id': 'bird_00075', 'gain': 0.020203232765197754, 'score': 0.47391098737716675}, {'rank': 3, 'id': 'bird_00075', 'gain': 0.02149977907538414, 'score': 0.47387757897377014}, {'rank': 4, 'id': 'bird_00069', 'gain': 0.05129025876522064, 'score': 0.4719516634941101}, {'rank': 5, 'id': 'bird_00075', 'gain': 0.10646381229162216, 'score': 0.47165820002555847}, {'rank': 6, 'id': 'bird_00069', 'gain': 0.10134433209896088, 'score': 0.4705403745174408}, {'rank': 7, 'id': 'bird_00025', 'gain': 0.0057005020789802074, 'score': 0.470207154750824}, {'rank': 8, 'id': 'bird_00069', 'gain': 0.15140660107135773, 'score': 0.46911484003067017}, {'rank': 9, 'id': 'bird_00025', 'gain': 0.08437956869602203, 'score': 0.46776485443115234}, {'rank': 10, 'id': 'bird_00071', 'gain': 0.06381088495254517, 'score': 0.4665457308292389}, {'rank': 11, 'id': 'bird_00069', 'gain': 0.25197258591651917, 'score': 0.46620792150497437}, {'rank': 12, 'id': 'bird_00046', 'gain': 0.07355550676584244, 'score': 0.46558114886283875}], 'base_score': 0.33999258279800415, 
        # 'doa': self.currentdoa, 'from': 'ntu-gazebo01', 'timestamp': 1654067860.26, 'base_spl': 68.10846120156562} if not MEOW else {'predictions': [{'rank': 1, 'id': 'meow', 'gain': 1, 'score': 0.47396957874298096}, {'rank': 2, 'id': 'meow', 'gain': 1, 'score': 0.47391098737716675}, {'rank': 3, 'id': 'meow', 'gain': 1, 'score': 0.47387757897377014}, {'rank': 4, 'id': 'meow', 'gain': 1, 'score': 0.4719516634941101}, {'rank': 5, 'id': 'meow', 'gain': 1, 'score': 0.47165820002555847}], 'base_score': 0.33999258279800415, 
        # 'doa': self.currentdoa, 'from': 'ntu-gazebo01', 'timestamp': 1654067860.26, 'base_spl': 68.10846120156562}
        self.fixedmasker = 'playing fixed masker = '
        self.msgdict = None
        self.currentmasker = "bird_00075" if not MEOW else "meow"
        self.maskerpath = "/home/pi/mqtt_client/maskers/"
        self.maskergain = 1.2
        self.gainweight = 1    
        self.maskerdiff =0.0001
        self.gainlimit = 1000
        self.weightedgain = 0
        self.buffersize = 20
        self.blocksize = 4096
        self.q = queue.Queue()#(maxsize=self.buffersize)
        self.q2 = queue.Queue()
        self.msgq = None
        self.msgqeval = None
        self.event = threading.Event()
        self.fadelength = 80
        self.maskercounter = 0
        self.currentmaskerorig = "bird_00075" if not MEOW else "meow"
        self.maskergainorig = 1
        self.doadiff = 20
        self.ambientspl = 68.1
        self.nexttrackmsg = 'playback starting...'
        self.beforeevaluationmsg = 'evaluation starting...'
        self.duringevaluationmsg = 'evaluation in progress, press any key to proceed to the next track.'
        self.endmsg = 'end of study'
        self.voicePromptGain = 0.1

    def insitucompensate(self, numofspeakers,distance):
        compensated = round(20*math.log10(distance) - 10*math.log10(numofspeakers))
        return compensated

    def insituMultiMaskercompensate(self, numofspeakers,distance,noOfMaskers):
        compensated = round(20*math.log10(distance) - 
                            10*math.log10(numofspeakers) -
                            20*math.log10(noOfMaskers))
        return compensated

    def spatialize(self, masker, angle, normalize=True, offset=-65, k=1.0):
        # masker.shape = (n_samples,)2
        # angle in degrees
        # offset in degrees
        
        # speaker locations assumed to be (RF, RB, LB, LF) i.e., (45, 135, 225, 315) deg
        # counting CW relative to the 0 deg line of the UMA
        # use offset to shift the speaker locations as needed
        
        '''
                0 deg
        [LF]----------[RF]
        |       ^       |
        |       |       |
        |     [UMA]     |
        |               |
        |               |
        [LB]----------[RB]
        
        
        e.g. if UMA is actually pointing at RF, then offset should be 45 deg
        i.e. set offset to negative of whereever UMA is pointing as if the UMA is pointing at 0 deg
        '''
            
        masker = np.squeeze(masker)
        
        anglerad = -np.deg2rad(angle + offset)
        x = k * np.cos(anglerad)
        y = k * np.sin(anglerad)
        
        lf = 1 + x + y # 1 + 1/2)
        lb = 1 - x + y
        rb = 1 - x - y
        rf = 1 + x - y

        # lf = 0
        # lb = 0
        # rb = 0
        # rf = 0

        
        gains = np.array([rb, lb, lf, rf])
        
        if normalize:
            gains = gains / np.sqrt(1 + 2*k*k)
    
        masker4c = masker[:, None] * gains[None, :] # (n_samples, 4)
        
        return masker4c        

    def msgcallback(self, client, userdata, message):
        print("GETTING PREDICTIONS FROM AWS")
        incomingmsg=json.loads(message.payload.decode('utf-8'))
        # self.q.put_nowait(incomingmsg)
        # self.q2.put_nowait(incomingmsg)
        self.msgq = incomingmsg
        print("Recommended Masker is: " + str(incomingmsg['predictions'][0]["id"]))
        print("Recommended Gain is: {} ({}dB)".format(incomingmsg['predictions'][0]["gain"], interpolate(incomingmsg['predictions'][0]["id"],incomingmsg['predictions'][0]["gain"])))
        print("BaseSPL is: {}".format(incomingmsg["base_spl"]))
        # data, fs = sf.read(msgdict['predictions'][0]["id"]+'.wav', dtype='float32')  
        # sd.play(data, fs, device=1)

    def playsilence(self):
        print('playing silence')
        silence, silencefs = sf.read(self.maskerpath + "bird_00075.wav", dtype='float32')
        sd.play(silence, silencefs)
        sd.wait()
        if switch == 1:
            pass

    def playmasker(self):
        print("playing masker")
        self.q = queue.Queue(maxsize=self.buffersize)
        newmasker = None
        newweightedgain = None
        newdoa = None
        self.msgdict = self.msgqeval
        
        #why q2?    
        if not self.q2.empty():
            self.msgdict = self.msgqeval
            self.ambientspl = self.msgdict["base_spl"]

        if self.msgdict != None: #If there is a prediction
            print("starting playback again")
            # maskercounter: to get index of the master from the dictionary, usually 0 for top masker
            print("masker counter=" + str(self.maskercounter))
            # if the masker to be played is not self.currentmasker, set self.maskergain to the gain of the masker to be played
            # self.currentmasker is set to bird_00075 by default
            if (self.msgdict['predictions'][self.maskercounter]["id"] != self.currentmasker) or (abs(self.msgdict['predictions'][self.maskercounter]["gain"]-self.maskergain)*self.gainweight>self.maskerdiff) or (abs(self.currentdoa - self.msgdict["doa"])>self.doadiff):
                self.maskergain = self.msgdict['predictions'][self.maskercounter]["gain"]
                # if self.maskergain (set in previous step) less than gainlimit (set at 1000)
                if self.maskergain*self.gainweight < self.gainlimit:
                    print("self.maskergain = {}".format(self.maskergain))
                    # print("self.msgdict['predictions'][self.maskercounter]['id']+'.wav' = {}".format(self.msgdict['predictions'][self.maskercounter]["id"]+'.wav'))
                    # print("round(self.ambientspl + 20*math.log10(self.maskergain)) = {}".format(round(self.ambientspl + 20*math.log10(self.maskergain))))
                    # calculate amssgain
                    amssgain = interpolate(self.msgdict['predictions'][self.maskercounter]["id"],self.maskergain) + self.insitucompensate(numofspeakers,optimaldistance)
                    # set amssgaint to min 45 and max 83
                    if amssgain >45 and amssgain <= 83:
                        pass
                    elif amssgain >83:
                        amssgain = 83
                    elif amssgain <46:
                        amssgain = 46
                    self.weightedgain = calibgains[self.msgdict['predictions'][self.maskercounter]["id"]+'.wav'][str(amssgain)]
                    print("self.weightedgain = {}".format(self.weightedgain))
                else:
                    self.weightedgain = self.gainlimit
                self.currentdoa = self.msgdict["doa"]
                # self.currentmaskerorig = self.currentmasker
        else:
            pass
        try:
            f, fs = sf.read(self.maskerpath + self.currentmasker +'.wav')
            data = self.spatialize(f*self.weightedgain, self.currentdoa)
            print(self.currentmasker)
            print("Playing at self.weightedgain = {}".format(self.weightedgain))
            compGain = math.pow(10,self.insitucompensate(numofspeakers,optimaldistance)/20)
            print('Compensated gain: {} dB'.format(20*math.log10(compGain)))
            sd.play(f*self.weightedgain*compGain, fs)
            sd.wait()
        except:
            pass
        if switch == 0:
            pass
      
    def streamcallback(self, outdata, frames, time, status):
        data = np.zeros((self.blocksize,1))
        assert frames == self.blocksize
        # if status.output_underflow:
        #     print('Output underflow: increase blocksize?', file=sys.stderr)
        #     raise sd.CallbackAbort
        assert not status
        # try:
        data = self.q.get_nowait()
        # except queue.Empty as e:
        #     raise sd.CallbackAbort from e
        if len(data) < len(outdata) and not self.q.empty():
            outdata[:len(data)] = data
            outdata[len(data):].fill(0)
            print("track ending")
            raise sd.CallbackStop
        else:
            outdata[:] = data


    def soundlooper(self):
        #wait for predictions to load first
        notprinted_flag = True
        while self.msgq == None:
            if notprinted_flag:
                print("Waiting for predictions")
                notprinted_flag = False
        print('predictions loaded')
        while True:
            if switch == 1:
                while True:
                    self.playmasker()    
                    if switch == 0:
                        break 
            if switch == 0:
                while True:
                    self.playsilence()
                    if switch == 1:
                        break


 
    def mqttlooper(self):
        while True:
            print("MQTTLOOPER RUNNING")
            self.MQTTClient.subscribeAsync(self.mqttTOPIC, 0,messageCallback = self.msgcallback)
            time.sleep(10)
    
def iotlooper():
    while True:
        iotClient.subscribeAsync(TOPIC, 0,messageCallback = customcallback)
   
def is_key_pressed():
    tty.setraw(sys.stdin.fileno())
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key != ''

sp = soundplayer()

sp.MQTTClient.connectAsync()
print("connected to mqtt")
ENDPOINT = "a5i03kombapo4-ats.iot.ap-southeast-1.amazonaws.com"
CLIENT_ID = "enviropluspi"
PATH_TO_CERTIFICATE = "certs/9972587da4767d10db7001fc18bab5b9124945c4762ebf246b6266e08352970b-certificate.pem.crt"
PATH_TO_PRIVATE_KEY = "certs/9972587da4767d10db7001fc18bab5b9124945c4762ebf246b6266e08352970b-private.pem.key"
PATH_TO_AMAZON_ROOT_CA_1 = "certs/root.pem"
TOPIC = "test/nbs"
iotClient = AWSIoTPyMQTT.AWSIoTMQTTClient('nbsiot')
iotClient.configureEndpoint(ENDPOINT, 8883)
iotClient.configureCredentials(PATH_TO_AMAZON_ROOT_CA_1, PATH_TO_PRIVATE_KEY, PATH_TO_CERTIFICATE)
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

def customcallback(client, userdata, message):
    incomingmsgs=json.loads(message.payload.decode('utf-8'))
    payloadstr = str(incomingmsgs)
    splitpayload = payloadstr.split('onoff')
    global switch
    switch = int(splitpayload[1][3])
    print(switch)
    
iotClient.connectAsync()
print("Connected to test/nbs")
switch = 0

settings = termios.tcgetattr(sys.stdin)

mqtt_thread = threading.Thread(
        target=sp.mqttlooper,
        name="mqtt",
        args=(),
        daemon=True,
    )

soundlooper_thread = threading.Thread(
        target=sp.soundlooper,
        name="soundlooper",
        args=(),
        daemon=True,
    )

iot_thread = threading.Thread(target = iotlooper,name = iotlooper, args=(), daemon=True)

iot_thread.start()
mqtt_thread.start()
soundlooper_thread.start()
soundlooper_thread.join()
mqtt_thread.join()
iot_thread.join()
# sp.MQTTClient.subscribeAsync(sp.mqttTOPIC, 0,messageCallback = sp.msgcallback)
# sp.playmasker()
