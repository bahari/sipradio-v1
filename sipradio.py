#############################################################################################################
# File:        sipradio.py
# Description: Program for RoIP Interface Computer (RIC) by integrating legacy radio over IP using SIP
#              implementation.
#              ----------------------------------------------------------------------------------------------
# Notes      : Major, Minor and Revision notes:
#              ----------------------------------------------------------------------------------------------
#              Major    - Software major number will counting up each time there is a major changes on the 
#                         software features. Minor number will reset to '0' and revision number will reset
#                         to '1' (on each major changes). Initially major number will be set to '1'
#              Minor    - Software minor number will counting up each time there is a minor changes on the
#                         software. Revision number will reset to '1' (on each minor changes).
#              Revision - Software revision number will counting up each time there is a bug fixing on the
#                         on the current major and minor number.
#              ----------------------------------------------------------------------------------------------
#              Current Features & Bug Fixing Information
#              ----------------------------------------------------------------------------------------------
#              001      - SIP client functionality where the daemon will register to ASTERISK server with 
#                         a unique call ID/user name stored inside sip.conf at the server side.
#              002      - Filter a call IN based on call ID whitelist stored locally inside sipradioCont.list.
#              003      - Reject a call for a call ID that not exist inside sipradioCont.list.
#              004      - Manage PTT request comes from a remote caller. Manual PTT request are in a format
#                         of SIP message or DTMF tone.
#              005      - REST Web API functionality. Hosting REST Web API for current controller status, 
#                         VOX setting parameters and SIP configuration.
#              006      - Communicate with RoIP Interface HAT (RIH) via serial communication and GPIO 
#                         interfacing for VOX configuration and PTT functionalities. 
#              007      - For PTT request, the daemon will trigger a GPIO once it received a PTT request from
#                         a remote caller. The GPIO will interface with RIH internal circuit for radio PTT
#                         activation.
#              008      - For PTT mode selection, the daemon will trigger a GPIO once it received a new
#                         configuration update request via REST Web API from a remote web client. The GPIO
#                         will interface with RIH internal circuit for PTT mode selection:
#
#                         Mode 1 - Both VOX and PTT control operation, where in case the VOX are not properly
#                                  functioning, PTT control can still be initiated manually.
#                         Mode 2 - Always in VOX operating conditions.
#                         Mode 3 - Always in manuall PTT operating conditions.
#
#              009      - For VOX parameter configuration, the daemon will send a command protocol along with
#                         a necessary data to RIH via a serial communication once it received a new 
#                         configuration update request via REST Web API from a remote web client. 
#                         The configuration parameter are consists of:
#
#                         a - PTT delay analog input delay division factor.
#                             Experimental configuration range - 1 to 5.
#                         b - VOX PTT delay addition factors.
#                             Experimental configuration range - 2 to 99.
#                         c - VOX threshold analog input multiplication factor.
#                             Experimental configuration range - ???
#                         d - VOX threshold analog addition factor.
#                             Experimental configuration range - 1 to 99.
#                         e - VOX total delay.
#                             Experimental configuration range - 2 to 99.
#                         f - VOX total threshold.
#                             Experimental configuration range - 70 to 99.
#                         g - VOX controller current mode.
#                             Mode 1 - Hardware configuration mode (Manual).
#                             Mode 2 - Software configuration mode (Automatic).
#
#              0010     - Monitor RIH current status by sending ALIVE command to the controller via serial 
#                         communication. 
#              0011     - Add after request response to handle Cross-Origin (CORS) problem upon web client 
#                         request.
#              0012     - Change configuration file name to - sipradioCnfg.conf, sipradioCont.list,
#                         voxradioCnfg.conf.
#              0013     - Add a SSL certificate to make sure REST web API can support HTTPS request.
#              0014     - Add a sampling method for receiving DTMF character '#'. To eliminate receiving
#                         multiple DTMF character '#' in one time.
#              0015     - Standardized nested 'if' statement without bracket.
#              0016     - Rename class from 'HFRadioSIPclient' to 'radioSIPclient'.
#              0017     - Rename variable from room to chat_room for sending PTT SIP message. Some how
#                         the PTT SIP message still can be send eventhough the variable name room are not exist.
#              0018     - Get the valid current call status (self.current_call), and use the variable instance to
#                         set the call to none each time the call is terminated.
#              0019     - Add macro for incoming call/message filtering (filter or NOT filter).
#              0020     - Add macro for secure (https) or insecure (http) REST web API.
#              0021     - Add retrieve current RIC configuration each time received PUT statement from
#                         dispatcher web server.
#              0022     - Change the ALIVE LED blinking sequence. LED ON and OFF state are based on the
#                         PTT time out counter setting divided by 2.
#              0023     - Change the wrong JSON return value at voxconfig. This caused dispatcher web client
#                         error during parsing the data to variable element.
#              0024     - Add a python dictionary list of data for Intercom functionalities.
#              0025     - Create intercom configuration data (icomradioCnfg.conf) that can be configured and read
#                         during daemon load.
#              0026     - Add a script logic to read Intercom configuration data each time daemon load.
#                         This data will be pass to the global variable for other processing logic.
#              0027     - Modified the current python script to include Intercom flag to all logic relating with RoIP mode.
#              0028     - Add a script logic to update daemon status python data dictionary with the new intercom
#                         attributes status.
#              0029     - Add a script logic to check SIP registration process after daemon SIP registration
#                         attempt during Intercom mode. This is important to make sure Intercom join
#                         group process are properly executed.
#              0030     - Add a script logic to check all current Intercom status in order to make sure the Intercom
#                         process are still in tact and connected:
#                         -> Check for Intercom call state end.
#                         -> Check for Intercom call state error.
#                         -> Check for Intercom call state connected.
#              0031     - Add a script logic to initiate call to the intercom group.
#              0032     - Add a script logic to check the error occur during initiate call process to the intercom group.
#              0033     - Add a script logic to execute call attempt process if the daemon accidentally drop a call
#                         to the Intercom group.
#              0034     - Add a script logic to monitor the Intercom group connectivity and initiate back
#                         a call to the intercom group with a prescribed delay. This is to make sure a
#                         connectivity to the intercom group are always in tact and connected.
#  
#              ----------------------------------------------------------------------------------------------   
# Author : Ahmad Bahari Nizam B. Abu Bakar.
#
# Version: 1.0.6
# Version: 1.1.1 - Add NEW feature [0019,0020,0021]. Please refer above description
# Version: 1.1.2 - Bug fixing item [0023]. Please refer above description
# Version: 1.2.1 - Add NEW feature [0024,0025,0026,0027,0028,0029,0030,0031,0032,0033,0034]. Please refer above description
#
# Date   : 24/06/2019 (INITIAL RELEASE DATE)
#          UPDATED - 29/09/2019
#          UPDATED - 03/09/2019
#          UPDATED - 07/09/2019
#          UPDATED - 15/09/2019
#          UPDATED - 03/10/2019
#          UPDATED - 25/01/2020
#          UPDATED - 16/03/2020 - 1.1.1
#          UPDATED - 16/03/2020 - 1.1.2
#          UPDATED - 20/08/2021 - 1.2.1
#
#############################################################################################################

import linphone
import logging
import logging.handlers
import sys
import os
import signal
import time
import thread
import serial
import RPi.GPIO as GPIO

# REST API library
from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)
            
# Setup log file
path = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger()
logger.setLevel(logging.INFO)
#logfile = logging.handlers.TimedRotatingFileHandler('/tmp/sipHFradio.log', when="midnight", backupCount=3)
logfile = logging.handlers.TimedRotatingFileHandler('/tmp/sipradio.log', when="midnight", backupCount=3)
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
logfile.setFormatter(formatter)
logger.addHandler(logfile)

# Setup GPIO 
GPIO.setmode(GPIO.BCM)
# GPIO4 for PTT activation
GPIO.setup(4, GPIO.OUT)
# GPIO17 for ALIVE indicator - Optional GPIO6
#GPIO.setup(17, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
# GPIO12 for PTT mode selection
GPIO.setup(12, GPIO.OUT)

# Initialize GPIO4 for PTT activation
GPIO.output(4, GPIO.LOW)
# Initialize GPIO12 for PTT mode selection
GPIO.output(12, GPIO.LOW)

# Retrieve daemon configuration
# Configuration parameter
# 1 - SIP registrar username
# 2 - SIP registrar password
# 3 - Asterisk server IP address
# 4 - MIC enable
# 5 - PTT enable
# 6 - Audio enable
# 7 - Audio multicast enable

# Global declaration
sipUserName  = ''    # SIP registrar username
sipPswd      = ''    # SIP registrar password
asteriskIP   = ''    # Asterisk server IP address
micSet       = ''    # MIC setting
pttToVal     = ''    # PTT time out value
pttMode      = ''    # PTT control mode of operation
micEnDis     = False # MIC enable or disable
pttSet       = ''    # PTT setting
pttEnDis     = False # PTT enable or disable
audioSet     = ''    # Audio setting
audioEnDis   = False # Audio enable or disable
audMultSet   = ''    # Audio muticast setting
audMultEnDis = False # Audio multicast enable or disable
callStatus   = ''    # Current RIC call status
currCallId   = ''    # 

pttCnt       = 0     # PTT sampling counter
lengthStr    = 0     # String manipulation length
pttTOcnt     = 0     # PTT time out counter
ledBlnkCnt   = 0     # Alive LED blinking counter
pttTimeOut   = 0     # PTT time out value from config file
pttModeOper  = 0     # PTT mode of operation value from config file
dtmfSmplCnt  = 0     # DTMF character '#' sampling counter
dtmfRx       = False # Receive DTMF character '#'
DTMFMETHOD   = True  # DTMF logic new method

pttRx        = False
wdog         = False
ledEn        = False
callconn     = False
pttIsON      = False

voxStatus      = ''  # Current VOX controller status
delayaindiv    = ''  # VOX PTT delay analog input delay division factor
pDelayaindiv   = ''  # Previous value for VOX PTT delay analog input delay division factor
delayvaladd    = ''  # VOX PTT delay addition factor
pDelayvaladd   = ''  # Previous value for VOX PTT delay addition factor
threshmultp    = ''  # VOX threshold analog input multiplication factor
pThreshmultp   = ''  # Previous value for VOX threshold analog input multiplication factor
threshadd      = ''  # VOX threshold analog input addition factor
pThreshadd     = ''  # Previous value for VOX threshold analog input addition factor
delayvalue     = ''  # VOX total delay
pDelayvalue    = ''  # Previous value for VOX total delay
thresholdvalue = ''  # VOX total threshold
pThresvalue    = ''  # Previous value for VOX total threshold
voxMode        = ''  # VOX controller current mode
pVoxMode       = ''  # Previous value for VOX controller current mode

sendCmdType    = 0   # VOX command type to send
commBusy    = False  # Communication still active between RIC and VOX during configuring process
macCallFilt = False  # Macro definition for call list filtering
macSecInSec = False  # Macro definition for option between http and https

siplist     = []     # SIP contact list

icomSet       = ''     # Intercom features enable/disable string
icomLoc       = ''     # Intercom group location
icomExtId     = ''     # Intercom extension ID
sipIcomAddr   = ''     # Intercom group full SIP address
icomEnaDis    = False  # Intercom features enable/disable flag
strtJoinIcom  = False  # Initiate call to intercom group flag
registStat    = False  # Regitration to server flag
strtTmrJoin   = False  # Join intercom delay flag
icomToRoIP    = False  # Revert setting back from intercom to RoIP
retryJoinIcom = 0      # Intercom join attempt counter
joinIcomCnt   = 0      # Intercom reconnection delay counter

# Check for call list filtering macro
if (len(sys.argv) > 1):
    for x in sys.argv:
        # Optional macro if we want to filter incoming call
        if(x == "CALLFILTER"):
            macCallFilt = True
        # Optional macro if we want to enable https
        elif (x == "SECURE"):
            macSecInSec = True
            
# Config data - load default data first
sipConfigData=[
    {
        'id' : '000',
        'sipusername' : '1002',
        'sippassword' : '1234',
        'asteriskip' : '192.168.8.101',
        'pttset' : 'TRUE',
        'micset' : 'TRUE',
        'audioset' : 'TRUE',
        'audmultset' : 'TRUE',
        'pttto' : '60',
        'pttmode' : '1'
    }
]

# VOX setting data - load default vox data first
voxParamData=[
    {
        'id' : '000',
        'delayaindiv' : '5',
        'delayvaladd' : '2',
        'threshmultp' : '0.8',
        'threshadd' : '70',
        'delayvalue' : '95',
        'thresholdvalue' : '267',
        'mode' : 'Mode 2'
    }
]

# Intercom setting data - load default intercom data first
icomParamData=[
    {
        'id' : '000',
        'icomset' : 'FALSE',
        'icomloc' : 'NA',
        'icomextid' : 'NA'
    }
]

# Daemon status data
daemonStat=[
    {
        'id' : '000',
        'callstatus' : 'LISTENING',
        'pttstatus' : 'OFF',
        'pttmode' : 'Mode 1',
        'voxmode' : 'Mode 2',
        'voxstatus' : 'OFFLINE',
        'intercom' : 'DISABLE',
        'intercomstatus' : 'OFFLINE',
        'currcallid' : 'NO'
    }
]

# String manipulation
def mid(s, offset, amount):
    return s[offset - 1:offset + amount - 1]

# Open daemon configuration file
#file = open("/etc/conf.d/sipHFradio/sipHFradioCnfg.conf", "r")
file = open("/etc/conf.d/sipradio/sipradioCnfg.conf", "r")

# Retrieve SIP username
sipUserName = file.readline()
lengthStr = len(sipUserName)
sipUserName = mid(sipUserName, 13, lengthStr - 13)

# Retrieve SIP password
sipPswd = file.readline()
lengthStr = len(sipPswd)
sipPswd = mid(sipPswd, 9, lengthStr - 9)

# Retrieve Asterisk IP
asteriskIP = file.readline()
lengthStr = len(asteriskIP)
asteriskIP = mid(asteriskIP, 12, lengthStr - 12)

# Retrieve PTT setting
pttSet = file.readline()
lengthStr = len(pttSet)
pttSet = mid(pttSet, 8, lengthStr - 8)

# Set PTT setting flag
if pttSet == 'TRUE':
    pttEnDis = True
else:
    pttEnDis = False

# Retrieve MIC setting
micSet = file.readline()
lengthStr = len(micSet)
micSet = mid(micSet, 8, lengthStr - 8)

# Set MIC setting flag
if micSet == 'TRUE':
    micEnDis = True
else:
    micEnDis = False

# Retrieve audio setting
audioSet = file.readline()
lengthStr = len(audioSet)
audioSet = mid(audioSet, 10, lengthStr - 10)

# Set audio setting flag
if audioSet == 'TRUE':
    audioEnDis = True
else:
    audioEnDis = False

# Retrieve multicast audio setting
audMultSet = file.readline()
lengthStr = len(audMultSet)
audMultSet = mid(audMultSet, 12, lengthStr - 12)

# Set multicast audio setting flag
if audMultSet == 'TRUE':
    audMultEnDis = True
else:
    audMultEnDis = False

# Retrive PTT time out value
pttToVal = file.readline()
lengthStr = len(pttToVal)
pttToVal = mid(pttToVal, 7, lengthStr - 7)

# PTT time out in integer value
pttTimeOut = int(pttToVal) 

# Retrieve PTT mode of operation
pttMode = file.readline()
lengthStr = len(pttMode)
pttMode = mid(pttMode, 9, lengthStr - 9)

# PTT mode of operation in integer value
pttModeOper = int(pttMode)

# Close config gile
file.close()

# Open VOX controller configuration file
#file = open("/etc/conf.d/sipHFradio/voxHFradioCnfg.conf", "r")
file = open("/etc/conf.d/sipradio/voxradioCnfg.conf", "r")

# Retrieve VOX PTT delay analog input delay division factor
delayaindiv = file.readline()
lengthStr = len(delayaindiv)
delayaindiv = mid(delayaindiv, 13, lengthStr - 13)

# Retrieve VOX PTT delay addition factor
delayvaladd = file.readline()
lengthStr = len(delayvaladd)
delayvaladd = mid(delayvaladd, 13, lengthStr - 13)

# Retrieve VOX threshold analog input multiplication factor
threshmultp = file.readline()
lengthStr = len(threshmultp)
threshmultp = mid(threshmultp, 13, lengthStr - 13)

# Retrieve VOX threshold analog input addition factor
threshadd = file.readline()
lengthStr = len(threshadd)
threshadd = mid(threshadd, 11, lengthStr - 11)

# Retrieve VOX total delay
delayvalue = file.readline()
lengthStr = len(delayvalue)
delayvalue = mid(delayvalue, 12, lengthStr - 12)

# Retrieve VOX total threshold
thresholdvalue = file.readline()
lengthStr = len(thresholdvalue)
thresholdvalue = mid(thresholdvalue, 16, lengthStr - 16)

# Retrieve VOX mode
voxMode = file.readline()
lengthStr = len(voxMode)
voxMode = mid(voxMode, 6, lengthStr - 6)

# Close config gile
file.close()

# Open intercom configuration file
file = open("/etc/conf.d/sipradio/icomradioCnfg.conf", "r")

# Retrieve intercom enable/disable flag
icomSet = file.readline()
lengthStr = len(icomSet)
icomSet = mid(icomSet, 9, lengthStr - 9)

# Set intercom enable/disable flag
if icomSet == 'TRUE':
    icomEnaDis = True
else:
    icomEnaDis = False

# Retrieve intercom group location
icomLoc = file.readline()
lengthStr = len(icomLoc)
icomLoc = mid(icomLoc, 9, lengthStr - 9)

# Retrieve intercom extension ID
icomExtId = file.readline()
lengthStr = len(icomExtId)
icomExtId = mid(icomExtId, 7, lengthStr - 7)

# Construct intercom group full sip address
sipIcomAddr = 'sip:' + icomExtId + '@' + asteriskIP

# Close config gile
file.close()

### For debugging purposes
##logger.info("DEBUG: Intercom Set: %s" % (icomSet))
##logger.info("DEBUG: Intercom Group: %s" % (icomLoc))
##logger.info("DEBUG: Intercom Extensions: %s" % (icomExtId))
##logger.info("DEBUG: Intercom SIP Address: %s" % (sipIcomAddr))
##sys.exit()

# Copy current VOX config file data to python config data format
# This config data will provide VOX info via REST API
# Client can edit this config data remotely
vox = [ voxX for voxX in voxParamData if (voxX['id'] == '000') ]
vox[0]['delayaindiv'] = delayaindiv
vox[0]['delayvaladd'] = delayvaladd
vox[0]['threshmultp'] = threshmultp
vox[0]['threshadd']   = threshadd
vox[0]['delayvalue']  = delayvalue
vox[0]['thresholdvalue']  = thresholdvalue

# Copy current intercom config file data to python config data format
# This config data will provide info via REST API
# Client can edit this config data remotely
icomCnfgData = [ icomCnfg for icomCnfg in icomParamData if (icomCnfg['id'] == '000') ]
icomCnfgData[0]['icomset'] = icomSet
icomCnfgData[0]['icomloc'] = icomLoc
icomCnfgData[0]['icomextid'] = icomExtId

# Current VOX controller mode
if voxMode == '1':
    vox[0]['mode']  = 'Mode 1'
else:
    vox[0]['mode']  = 'Mode 2'

# Check for PTT mode - Initialize the mode
# Hybrid PTT mode:
# Mode 1:
# When there is no PTT signal, PTT are in VOX mode
# When there is a PTT signal, PTT are in MANUAL mode

# Mode 2:
# Always in VOX PTT activation

# Mode 3:
# Always in MANUAL PTT activation

# Intercom mode:
# Always in intercom mode, and all functionalities related to RoIP
# will be disable, the current setting status will remain as
# previous except the intercom features will enable

# Intercom mode
if icomEnaDis == True:
    # PTT mode relay always ON
    GPIO.output(12, GPIO.HIGH)
    # PTT control will always ON 
    GPIO.output(4, GPIO.HIGH)
    
    # Update RIC daemon status REST API data
    # All the previous RoIP setting are not been changed in this daemon information status
    # Only RoIP functionalities are disable
    ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
    ric[0]['pttmode'] = 'Mode 3'
    # Current VOX controller mode
    if voxMode == '1':
        ric[0]['voxmode'] = 'Mode 1'
    else:
        ric[0]['voxmode'] = 'Mode 2'

    # Intercom current status set to enable
    ric[0]['intercom'] = 'ENABLE'
else:
    # Mode 1
    if pttModeOper == 1:
        # Initialize PTT mode relay OFF
        GPIO.output(12, GPIO.LOW)
        
        # Update RIC daemon status REST API data
        ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
        ric[0]['pttmode'] = 'Mode 1'
        # Current VOX controller mode
        if voxMode == '1':
            ric[0]['voxmode'] = 'Mode 1'
        else:
            ric[0]['voxmode'] = 'Mode 2'
    # Mode 2
    elif pttModeOper == 2:
        # PTT mode relay always OFF
        GPIO.output(12, GPIO.LOW)

        # Update RIC daemon status REST API data
        ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
        ric[0]['pttmode'] = 'Mode 2'
        # Current VOX controller mode
        if voxMode == '1':
            ric[0]['voxmode'] = 'Mode 1'
        else:
            ric[0]['voxmode'] = 'Mode 2'
    # Mode 3
    elif pttModeOper == 3:
        # PTT mode relay always ON
        GPIO.output(12, GPIO.HIGH)

        # Update RIC daemon status REST API data
        ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
        ric[0]['pttmode'] = 'Mode 3'
        # Current VOX controller mode
        if voxMode == '1':
            ric[0]['voxmode'] = 'Mode 1'
        else:
            ric[0]['voxmode'] = 'Mode 2'
        
# Copy current SIP config file data to python config data format
# This config data will provide info via REST API
# Client can edit this config data remotely
cnfgData = [ config for config in sipConfigData if (config['id'] == '000') ]
cnfgData[0]['sipusername'] = sipUserName
cnfgData[0]['sippassword'] = sipPswd
cnfgData[0]['asteriskip'] = asteriskIP
cnfgData[0]['pttset'] = pttSet
cnfgData[0]['micset'] = micSet
cnfgData[0]['audioset'] = audioSet
cnfgData[0]['audmultset'] = audMultSet
cnfgData[0]['pttto'] = pttToVal
cnfgData[0]['pttmode'] = pttMode

# Optional macro if we want to filter incoming call
# Load the contact list from text file list
if macCallFilt == True:
    # Open contact list, stored contact list in python list
    #file = open("/etc/conf.d/sipHFradio/sipHFradioCont.list", "r")
    file = open("/etc/conf.d/sipradio/sipradioCont.list", "r")
    # Retrieve SIP contact list from stored list
    for i in range(100):
        tempdata = file.readline()
        tempdata = tempdata.strip('\n') # Get rid of new line character
        # Initial state the list are emptied, add first data
        if siplist == '':
            # Data exist inside stored list
            if tempdata != '':
                siplist = [tempdata]
                tempdata = ''
            # NO data remain inside stored list
            else:
                break
        # Python list are not emptied, append the data
        else:
            # Data exist inside stored list
            if tempdata != '':
                siplist.append(tempdata)
                tempdata = ''
            # NO data remain inside stored list
            else:
                break
    # Close the file
    file.close()

# Initialize back daemon from intercom to RoIP mode
def initRoIpMode():
    global pttModeOper
    global voxMode
    global daemonStat

    # Diasble back PTT control signal
    GPIO.output(4, GPIO.LOW)
    
    # Mode 1
    if pttModeOper == 1:
        # Initialize PTT mode relay OFF
        GPIO.output(12, GPIO.LOW)
        
        # Update RIC daemon status REST API data
        ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
        ric[0]['pttmode'] = 'Mode 1'
        # Current VOX controller mode
        if voxMode == '1':
            ric[0]['voxmode'] = 'Mode 1'
        else:
            ric[0]['voxmode'] = 'Mode 2'
    # Mode 2
    elif pttModeOper == 2:
        # PTT mode relay always OFF
        GPIO.output(12, GPIO.LOW)

        # Update RIC daemon status REST API data
        ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
        ric[0]['pttmode'] = 'Mode 2'
        # Current VOX controller mode
        if voxMode == '1':
            ric[0]['voxmode'] = 'Mode 1'
        else:
            ric[0]['voxmode'] = 'Mode 2'
    # Mode 3
    elif pttModeOper == 3:
        # PTT mode relay always ON
        GPIO.output(12, GPIO.HIGH)

        # Update RIC daemon status REST API data
        ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
        ric[0]['pttmode'] = 'Mode 3'
        # Current VOX controller mode
        if voxMode == '1':
            ric[0]['voxmode'] = 'Mode 1'
        else:
            ric[0]['voxmode'] = 'Mode 2'


### Serial communication port for VOX controller configuration
##serPort = "/dev/ttyUSB0"    # VOX controller detected serial port
##serPortBRate = 9600         # Serial communication baudrate
##
### Open serial communication port with VOX controller
##voxSerComm = serial.Serial(serPort, serPortBRate)
##voxSerComm.flushInput()

class radioSIPclient:
    def __init__(self, username='', password='', snd_capture=''):
        self.quit = False
        callbacks = {
            'call_state_changed': self.call_state_changed,
            'message_received': self.message_received,
        }
        
        # Configure the linphone core
        #logging.basicConfig(level=logging.INFO) # Logging setting without log files, for testing
        signal.signal(signal.SIGINT, self.signal_handler)
        linphone.set_log_handler(self.log_handler)
        self.core = linphone.Core.new(callbacks, None, None)
        self.core.max_calls = 1
        self.core.echo_cancellation_enabled = False
        self.core.video_capture_enabled = False
        self.core.video_display_enabled = False

        # Enable MIC/Audio IN
        global micEnDis
        self.core.mic_enabled = micEnDis

        self.core.firewall_policy = linphone.FirewallPolicy.PolicyUseIce

        # Initialize audio capture card
        if len(snd_capture):
            self.core.capture_device = snd_capture

        # Only enable PCMU (Ulaw) and PCMA (Alaw) audio codecs
        for codec in self.core.audio_codecs:
            if codec.mime_type == "PCMA" or codec.mime_type == "PCMU":
                self.core.enable_payload_type(codec, True)
            else:
                self.core.enable_payload_type(codec, False)

        # Register to VDG+ Asterisk server
        global asteriskIP
        self.configure_sip_account(username, password, asteriskIP)

    # Daemon termination signal handler
    def signal_handler(self, signal, frame):
        self.core.terminate_all_calls()
        self.quit = True

    # Print daemon log events, also retrieve DTMF character
    def log_handler(self, level, msg):
        global pttCnt
        global pttEnDis
        global pttRx
        global pttTOcnt
        global callconn
        global pttModeOper
        global dtmfRx
        global dtmfSmplCnt
        global DTMFMETHOD
        global icomEnaDis
        global registStat
        global strtTmrJoin
                
        method = getattr(logging, level)
        method(msg)

        # Check for PTT mode
        # Hybrid PTT mode:
        # Mode 1:
        # When there is no PTT signal, PTT are in VOX mode
        # When there is a PTT signal, PTT are in MANUAL mode

        # Mode 2:
        # Always in VOX PTT activation
        
        # Mode 3:
        # Always in MANUAL PTT activation

        # Intercom mode:
        # Always in intercom mode, and all functionalities related to RoIP
        # will be disable, the current setting status will remain as
        # previous except the intercom features will enable

        # RIC in the intercom mode
        if icomEnaDis == True:
            # Check for registration with asterisk server, start joining intercom process 
            if 'REGISTER' in msg and registStat == False:
                registStat = True
                strtTmrJoin = True

                logger.info("DEBUG_INTERCOM: Registered")
            
        # Received DTMF PTT signal only valid in none intercom mode
        else:
            # Manual PTT are available only in Mode 1 and 3
            if pttModeOper == 1 or pttModeOper == 3: 
                # Receive PTT command from remote IP phone
                # PTT command are initiate by '#' character
                if pttEnDis == True and callconn == True:
                    # New DTMF method
                    if DTMFMETHOD == True:
                        # Implement new receive dtmf signal logic
                        # sip daemon receive dtmf signal - Process a PTT at daemon monitor thread
                        # Process is done at daemon monitor thread
                        if msg == 'Receiving dtmf #.' and dtmfRx == False:
                            dtmfSmplCnt = 0
                            dtmfRx = True
                    # Existing DTMF method
                    else:
                        # sip daemon receive dtmf signal
                        if msg == 'Receiving dtmf #.':
                            pttCnt += 1
                            # Sample the signal
                            # ON PTT
                            if pttCnt == 2 and pttRx == False:
                                logger.info("DEBUG_DTMF_PTT: Receive PTT signal, ON PTT")
                                                
                                # Mode 1
                                if pttModeOper == 1:
                                    # Activate GPIO for PTT mode MANUAL
                                    GPIO.output(12, GPIO.HIGH)
                                    # Activate GPIO for PTT control
                                    GPIO.output(4, GPIO.HIGH)
                                # Mode 3
                                elif pttModeOper == 3:
                                    # Activate GPIO for PTT control
                                    GPIO.output(4, GPIO.HIGH)
                                pttRx = True
                                pttCnt = 0
                                pttTOcnt = 0

                                # Update RIC daemon status REST API data
                                ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                                ric[0]['pttstatus'] = 'ON'
                            # OFF PTT - Must be based on requestor (SIP client)
                            elif pttCnt == 2 and pttRx == True:
                                logger.info("DEBUG_DTMF_PTT: Receive PTT signal, OFF PTT")

                                # Mode 1
                                if pttModeOper == 1:
                                    # Deactivate GPIO for PTT control
                                    GPIO.output(4, GPIO.LOW)
                                    # Deactivate GPIO for PTT mode MANUAL
                                    GPIO.output(12, GPIO.LOW)
                                # Mode 3
                                elif pttModeOper == 3:
                                    # Deactivate GPIO for PTT control
                                    GPIO.output(4, GPIO.LOW)
                                pttRx = False
                                pttCnt = 0
                                pttTOcnt = 0

                                # Update RIC daemon status REST API data
                                ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                                ric[0]['pttstatus'] = 'OFF'
            # PTT in Mode 2 
            else:
                # sip daemon receive dtmf signal
                if msg == 'Receiving dtmf #.':
                    logger.info("DEBUG_DTMF_PTT: PTT are in VOX mode (Mode 2)")
    # Receive call
    def call_state_changed(self, core, call, state, message):
        global callconn
        global pttRx
        global pttCnt
        global audioEnDis
        global audMultEnDis
        global siplist
        global pttIsON
        global icomEnaDis
        global icomExtId
        global icomStatus
        global strtTmrJoin
        global icomToRoIP
        
        # RIC running in the intercom mode
        if icomEnaDis == True:
            # Intercom END in a normal way
            if state == linphone.CallState.End:
                logger.info("DEBUG_INTERCOM: Intercom DISCONNECTED")
                
                # Update RIC daemon status REST API data
                ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                ric[0]['callstatus'] = 'LISTENING'
                ric[0]['intercomstatus'] = 'OFFLINE'
                ric[0]['currcallid'] = 'NO'

                # Set intercom reconnect flag
                strtTmrJoin = True
                
            # Intercom END because of ERROR
            elif state == linphone.CallState.Error:
                logger.info("DEBUG_INTERCOM: Intercom DISCONNECTED")
                
                # Update RIC daemon status REST API data
                ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                ric[0]['callstatus'] = 'LISTENING'
                ric[0]['intercomstatus'] = 'OFFLINE'
                ric[0]['currcallid'] = 'NO'

                # Set intercom reconnect flag
                strtTmrJoin = True

            # Intercom CONNECTED
            elif state == linphone.CallState.Connected:
                logger.info("DEBUG_INTERCOM: Intercom CONNECTED")
                
                # Update RIC daemon status REST API data
                ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                ric[0]['callstatus'] = 'CONNECTED'
                ric[0]['intercomstatus'] = 'ONLINE'
                ric[0]['currcallid'] = icomExtId

                # Clear intercom reconnect flag
                strtTmrJoin = False

                # Set revert to RoIP mode flag if there is a web client request to change the
                # current intercom mode
                if icomToRoIP == False:
                    icomToRoIP = True
                
        # Normal RIC in the radio integration mode
        else:
            # Received incoming call state
            if state == linphone.CallState.IncomingReceived:
                # Retrieve the caller address
                calleradr = call.remote_address.as_string_uri_only()
                logger.info("DEBUG_CALL: Caller Address: %s" % (calleradr))

                # Optional macro if we want to filter incoming call
                # Start filter the incoming call
                if macCallFilt == True:
                    # Only accept a call within a contact list buffer
                    # Valid call
                    if calleradr in siplist:
                        logger.info("DEBUG_CALL: Its a VALID call")

                        params = core.create_call_params(call)

                        # Enable audio for SIP payload
                        params.audio_enabled = audioEnDis
                        
                        # Enable audio multicast for SIP payload
                        params.audio_multicast_enabled = audMultEnDis
                        
                        core.accept_call_with_params(call, params)

                        # Update RIC daemon status REST API data
                        ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                        ric[0]['currcallid'] = calleradr 
                        
                        #call.microphone_volume_gain = 0.98

                        self.current_call = call
                    # Invalid call
                    else:
                        logger.info("DEBUG_CALL: Its an INVALID call")
                        # Decline received call
                        core.decline_call(call, linphone.Reason.Declined)

                        # Update RIC daemon status REST API data
                        ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                        ric[0]['callstatus'] = 'LISTENING'
                        ric[0]['currcallid'] = 'NO'
                # Accept all incoming call, macro are not set
                else:
                    logger.info("DEBUG_CALL: Call ID is NOT filtered")

                    params = core.create_call_params(call)

                    # Enable audio for SIP payload
                    params.audio_enabled = audioEnDis
                        
                    # Enable audio multicast for SIP payload
                    params.audio_multicast_enabled = audMultEnDis
                        
                    core.accept_call_with_params(call, params)

                    # Update RIC daemon status REST API data
                    ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                    ric[0]['currcallid'] = calleradr 
                        
                    #call.microphone_volume_gain = 0.98

                    self.current_call = call
            # Call END in a normal way
            elif state == linphone.CallState.End:
                logger.info("DEBUG_CALL: Call END in normal way")
                callconn = False
                # Deactivate GPIO for PTT control, if previously ON
                if pttRx == True:
                    # Mode 1
                    if pttModeOper == 1:
                        # Deactivate GPIO for PTT control
                        GPIO.output(4, GPIO.LOW)
                        # Deactivate GPIO for PTT mode MANUAL
                        GPIO.output(12, GPIO.LOW)
                    # Mode 3
                    elif pttModeOper == 3:
                        # Deactivate GPIO for PTT control
                        GPIO.output(4, GPIO.LOW)
                    pttCnt = 0
                    pttRx = False
                    pttIsON = False
                    
                    logger.info("DEBUG_CALL: OFF PTT")
                # Update RIC daemon status REST API data
                ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                ric[0]['callstatus'] = 'LISTENING'
                ric[0]['currcallid'] = 'NO'
                ric[0]['pttstatus'] = 'OFF'

                self.current_call = None
            # Call END because of ERROR
            elif state == linphone.CallState.Error:
                logger.info("DEBUG_CALL: Call END because of ERROR")
                callconn = False
                # Deactivate GPIO for PTT control, if previously ON
                if pttRx == True:
                    # Mode 1
                    if pttModeOper == 1:
                        # Deactivate GPIO for PTT control
                        GPIO.output(4, GPIO.LOW)
                        # Deactivate GPIO for PTT mode MANUAL
                        GPIO.output(12, GPIO.LOW)
                    # Mode 3
                    elif pttModeOper == 3:
                        # Deactivate GPIO for PTT control
                        GPIO.output(4, GPIO.LOW)
                    pttCnt = 0
                    pttRx = False
                    pttIsON = False
                    
                    logger.info("DEBUG_CALL: OFF PTT")
                # Update RIC daemon status REST API data
                ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                ric[0]['callstatus'] = 'LISTENING'
                ric[0]['currcallid'] = 'NO'
                ric[0]['pttstatus'] = 'OFF'

                self.current_call = None
            # Call CONNECTED
            elif state == linphone.CallState.Connected:
                logger.info("DEBUG_CALL: Call CONNECTED")
                callconn = True

                # Update RIC daemon status REST API data
                ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                ric[0]['callstatus'] = 'CONNECTED'
            
    # Receive SIP message for PTT signal - Optional for tactical SIP client application
    def message_received(self, core, room, message):
        global siplist
        global pttIsON
        global callconn
        global pttEnDis
        global pttTOcnt
        global pttModeOper
        global icomEnaDis
        
        # Get the message sender SIP address
        msgfrom = message.from_address
        msgfrom = msgfrom.as_string_uri_only()
        # Display the sender SIP address
        logger.info("DEBUG_SIP_PTT: FROM ADDRESS: %s" % (msgfrom))

        # READ the message text
        msgtext = message.text
        # Display the READ text message 
        logger.info("DEBUG_SIP_PTT: MESSAGE TEXT: %s" % (msgtext))

        # Check for PTT mode
        # Hybrid PTT mode:
        # Mode 1:
        # When there is no PTT signal, PTT are in VOX mode
        # When there is a PTT signal, PTT are in MANUAL mode

        # Mode 2:
        # Always in VOX PTT activation
        
        # Mode 3:
        # Always in MANUAL PTT activation

        # Intercom mode:
        # Always in intercom mode, and all functionalities related to RoIP
        # will be disable, the current setting status will remain as
        # previous except the intercom features will enable

        # Received PTT signal SIP message only valid in none intercom mode
        if icomEnaDis == False:
            # Manual PTT are available only in Mode 1 and 3
            if pttModeOper == 1 or pttModeOper == 3:
                # PTT is enable and previously the call are connected
                if pttEnDis == True and callconn == True:
                    # Optional macro if we want to filter incoming msg
                    # Start filter the incoming call
                    if macCallFilt == True:
                        # Check whether the msg sender are in the list or not
                        # Valid contact and SIP call are connected
                        if msgfrom in siplist:
                            logger.info("DEBUG_SIP_PTT: VALID CONTACT: %s" % (msgfrom))

                            # Check for PTT signal through SIP message
                            # ON PTT
                            if msgtext == "PTT_ON":
                                # Currently no PTT events occur 
                                if pttIsON == False:
                                    logger.info("DEBUG_SIP_PTT: Receive PTT signal, ON PTT")
                                    logger.info("DEBUG_SIP_PTT: Send ON PTT command ACK")
                                    
                                    # Send ACK to sender
                                    chat_room = core.get_chat_room_from_uri(msgfrom)
                                    pttAckMsg = chat_room.create_message('PTT_ON_ACK')
                                    chat_room.send_chat_message(pttAckMsg)

                                    pttTOcnt = 0 # Reset back PTT GPIO checking counter

                                    # Mode 1
                                    if pttModeOper == 1:
                                        # Activate GPIO for PTT mode MANUAL
                                        GPIO.output(12, GPIO.HIGH)
                                        # Activate GPIO for PTT control
                                        GPIO.output(4, GPIO.HIGH)
                                    # Mode 3
                                    elif (pttModeOper == 3):
                                        # Activate GPIO for PTT control
                                        GPIO.output(4, GPIO.HIGH)
                                    pttIsON = True

                                    # Update RIC daemon status REST API data
                                    ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                                    ric[0]['pttstatus'] = 'ON'
                                # PTT is BUSY
                                else:
                                    logger.info("DEBUG_SIP_PTT: PTT is BUSY!")
                            # OFF PTT
                            elif msgtext == "PTT_OFF":    
                                # Previously has PTT events
                                if pttIsON == True:
                                    logger.info("DEBUG_SIP_PTT: Receive PTT signal, OFF PTT")
                                    logger.info("DEBUG_SIP_PTT: Send OFF PTT command ACK")

                                    pttTOcnt = 0 # Reset back PTT GPIO checking counter
                                    
                                    # Send ACK to sender
                                    chat_room = core.get_chat_room_from_uri(msgfrom)
                                    pttAckMsg = chat_room.create_message('PTT_OFF_ACK')
                                    chat_room.send_chat_message(pttAckMsg);

                                    # Mode 1
                                    if pttModeOper == 1:
                                        # Deactivate GPIO for PTT control
                                        GPIO.output(4, GPIO.LOW)
                                        # Deactivate GPIO for PTT mode MANUAL
                                        GPIO.output(12, GPIO.LOW)
                                    # Mode 3
                                    elif pttModeOper == 3:
                                        # Deactivate GPIO for PTT control
                                        GPIO.output(4, GPIO.LOW)
                                    pttIsON = False

                                    # Update RIC daemon status REST API data
                                    ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                                    ric[0]['pttstatus'] = 'OFF'
                    # No need to filter incoming msg
                    else:
                        # Check for PTT signal through SIP message
                        # ON PTT
                        if msgtext == "PTT_ON":
                            # Currently no PTT events occur 
                            if pttIsON == False:
                                logger.info("DEBUG_SIP_PTT: Receive PTT signal, ON PTT")
                                logger.info("DEBUG_SIP_PTT: Send ON PTT command ACK")
                                
                                # Send ACK to sender
                                chat_room = core.get_chat_room_from_uri(msgfrom)
                                pttAckMsg = chat_room.create_message('PTT_ON_ACK')
                                chat_room.send_chat_message(pttAckMsg)

                                pttTOcnt = 0 # Reset back PTT GPIO checking counter

                                # Mode 1
                                if pttModeOper == 1:
                                    # Activate GPIO for PTT mode MANUAL
                                    GPIO.output(12, GPIO.HIGH)
                                    # Activate GPIO for PTT control
                                    GPIO.output(4, GPIO.HIGH)
                                # Mode 3
                                elif (pttModeOper == 3):
                                    # Activate GPIO for PTT control
                                    GPIO.output(4, GPIO.HIGH)
                                pttIsON = True

                                # Update RIC daemon status REST API data
                                ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                                ric[0]['pttstatus'] = 'ON'
                            # PTT is BUSY
                            else:
                                logger.info("DEBUG_SIP_PTT: PTT is BUSY!")
                        # OFF PTT
                        elif msgtext == "PTT_OFF":    
                            # Previously has PTT events
                            if pttIsON == True:
                                logger.info("DEBUG_SIP_PTT: Receive PTT signal, OFF PTT")
                                logger.info("DEBUG_SIP_PTT: Send OFF PTT command ACK")

                                pttTOcnt = 0 # Reset back PTT GPIO checking counter
                                
                                # Send ACK to sender
                                chat_room = core.get_chat_room_from_uri(msgfrom)
                                pttAckMsg = chat_room.create_message('PTT_OFF_ACK')
                                chat_room.send_chat_message(pttAckMsg);

                                # Mode 1
                                if pttModeOper == 1:
                                    # Deactivate GPIO for PTT control
                                    GPIO.output(4, GPIO.LOW)
                                    # Deactivate GPIO for PTT mode MANUAL
                                    GPIO.output(12, GPIO.LOW)
                                # Mode 3
                                elif pttModeOper == 3:
                                    # Deactivate GPIO for PTT control
                                    GPIO.output(4, GPIO.LOW)
                                pttIsON = False

                                # Update RIC daemon status REST API data
                                ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                                ric[0]['pttstatus'] = 'OFF'
                        
            # PTT in Mode 2
            else:
                logger.info("DEBUG_SIP_PTT: PTT are in VOX mode (Mode 2)")    
     
    # Register to VDG+ Asterisk server
    def configure_sip_account(self, username, password, astIP):
        # Configure the SIP account
        proxy_cfg = self.core.create_proxy_config()

        sipParam = 'sip:' + username + '@' + astIP
        proxy_cfg.identity_address = self.core.create_address(sipParam)
        proxy_cfg.server_addr = 'sip:' + astIP + ';transport=udp'
        proxy_cfg.register_enabled = True
        
        self.core.add_proxy_config(proxy_cfg)
        auth_info = self.core.create_auth_info(username, None, password, None, None, astIP)
        self.core.add_auth_info(auth_info)

    # Loop - Check the intercom flag, and enter intercom room if initiated
    def run(self):
        global icomEnaDis
        global icomExtId
        global icomLoc
        global strtJoinIcom
        global retryJoinIcom
        global daemonStat
        global strtTmrJoin
        global icomToRoIP
        global sipIcomAddr
        global asteriskIP

        while not self.quit:
            # Enter the intercom room as a guest - Start call attempt to intercom room
            if icomEnaDis == True:
                if strtJoinIcom == True and retryJoinIcom <= 5:
                    try:
                        logger.info("DEBUG_INTERCOM: Try to joining intercom group....")

                        # Construct intercom group full sip address
                        sipIcomAddr = 'sip:' + icomExtId + '@' + asteriskIP

                        # Initialize call out parameter
                        params = self.core.create_call_params(None)
                        params.audio_enabled = True
                        #params.video_enabled = True
                        params.audio_multicast_enabled = False  # Set these = True if you want multiple
                        params.video_multicast_enabled = False  # people to connect at once.

                        address = linphone.Address.new(sipIcomAddr)
                        self.current_call = self.core.invite_address_with_params(address, params)
                    
                        # Error during initiate outgoing call to the intercom group
                        if None is self.current_call:
                            # Update RIC daemon status REST API data
                            ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                            ric[0]['callstatus'] = 'LISTENING'
                            ric[0]['intercomstatus'] = 'OFFLINE'
                            ric[0]['currcallid'] = 'NO'
                            ric[0]['intercom'] = 'DISABLE'

                            strtTmrJoin = True
                            retryJoinIcom += 1

                            logger.info("DEBUG_INTERCOM: Error joining intercom group!")
                            logger.info("DEBUG_INTERCOM: Retry....")
                        else:
                            # PTT mode relay always ON
                            GPIO.output(12, GPIO.HIGH)
                            # PTT control will always ON 
                            GPIO.output(4, GPIO.HIGH)
                            
                            # Update RIC daemon status REST API data
                            ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                            ric[0]['callstatus'] = 'CONNECTED'
                            ric[0]['intercomstatus'] = 'ONLINE'
                            ric[0]['currcallid'] = icomExtId
                            ric[0]['intercom'] = 'ENABLE'

                            retryJoinIcom = 0

                            logger.info("DEBUG_INTERCOM: Joining intercom group [%s - %s] successful" % (icomExtId, icomLoc))

                            # Set revert to RoIP mode flag if there is a web client request to change the
                            # current intercom mode
                            if icomToRoIP == False:
                                icomToRoIP = True

                        strtJoinIcom = False
                    except:
                        # Update RIC daemon status REST API data
                        ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                        ric[0]['callstatus'] = 'LISTENING'
                        ric[0]['intercomstatus'] = 'OFFLINE'
                        ric[0]['currcallid'] = 'NO'
                        ric[0]['intercom'] = 'DISABLE'

                        strtTmrJoin = True
                        retryJoinIcom += 1

                        logger.info("DEBUG_INTERCOM: Error joining intercom group!")
                        logger.info("DEBUG_INTERCOM: Retry....")

                # Reboot RIC after 5 attempt reconnecting process
                elif retryJoinIcom == 5:
                    logger.info("DEBUG_INTERCOM: Restart RIC daemon....")

                    # Terminate intercom connection before reboot process
                    self.core.terminate_all_calls()
                    # Start reboot RIC daemon

            # Change mode to the normal RoIP mode
            else:
                # Terminate all intercom connection and revert to default RoIP mode
                if icomToRoIP == True:
                    logger.info("DEBUG_INTERCOM: Change mode to default RoIP mode")

                    # Terminate intercom connection
                    self.core.terminate_all_calls()
                    # Initialize back all necessary variables
                    strtJoinIcom = False
                    strtTmrJoin = False
                    retryJoinIcom = 0

                    # Update RIC daemon status REST API data
                    ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                    ric[0]['callstatus'] = 'LISTENING'
                    ric[0]['intercomstatus'] = 'OFFLINE'
                    ric[0]['currcallid'] = 'NO'
                    ric[0]['intercom'] = 'DISABLE'

                    # Initialize back the daemon to the RoIP mode
                    initRoIpMode()
                    
                    icomToRoIP = False
                    
            self.core.iterate()
            time.sleep(0.03)

# Get current RIC status
# Example command to send:
# http://192.168.101.1:5000/ricinfo
@app.route('/ricinfo', methods=['GET'])
def getRicInfoDb():
    return jsonify({'RICInfo' : daemonStat})

# Get current VOX controller setting
# Example command to send:
# http://192.168.101.1:5000/voxconfig
@app.route('/voxconfig', methods=['GET'])
def getVoxConfigData():
    return jsonify({'voxconfig': voxParamData})

# Get current intercom setting
# Example command to send:
# http://192.168.101.1:5000/voxconfig
@app.route('/icomconfig', methods=['GET'])
def getIcomConfigData():
    return jsonify({'intercomconfig': icomParamData})

# Update setting for intercom group
# Example command to send:
# curl -i -H "Content-type: application/json" -X PUT -d "{\"icomset\":\"true\"}" http://192.168.101.1:5000/icomconfig/000
@app.route('/icomconfig/<cnfgid>', methods=['PUT'])
def updateIcomConfig(cnfgid):
    global icomSet
    global icomLoc
    global icomExtId
    global icomEnaDis
    global strtTmrJoin
    global icomToRoIP
    
    tempIcomEn = ''
    tempIcomLoc = ''
    tempIcomExtId = ''
    
    iCnfg = [ iCnfgG for iCnfgG in icomParamData if (iCnfgG['id'] == cnfgid) ]
    # Update intercom config - Intercom enable/disable
    if 'icomset' in request.json:
        tempIcomEn = request.json['icomset']

        # Update intercom enable/disable parameter
        if tempIcomEn != 'RETRIEVE':
            # Open intercom config file
            file = open("/etc/conf.d/sipradio/icomradioCnfg.conf", "w")

            # Update config data
            iCnfg[0]['icomset'] = request.json['icomset']
            icomSet = iCnfg[0]['icomset']
            
            # Create new text file for a new data
            tmpIcomSet = 'ICOMSET:'
            tmpIcomSet = tmpIcomSet + icomSet + '\n'
            file.write(tmpIcomSet)

            # Copy the rest (no update) data
            tmpIcomLoc = 'ICOMLOC:'
            tmpIcomLoc = tmpIcomLoc + icomLoc + '\n'
            file.write(tmpIcomLoc)

            tmpIcomExtId = 'EXTID:'
            tmpIcomExtId = tmpIcomExtId + icomExtId + '\n'
            file.write(tmpIcomExtId)

            # Update global intercom enable/disable flag
            # Enable intercom mode
            if icomSet == 'TRUE':
                icomEnaDis = True
                if icomToRoIP == False:
                    strtTmrJoin = True
            # Disable intercom mode
            else:
                icomEnaDis = False

            # Close the file
            file.close()

    # Update intercom config - Intercom group/name
    elif 'icomloc' in request.json:
        tempIcomLoc = request.json['icomloc']

        # Update intercom group location/name
        if tempIcomLoc != 'RETRIEVE':
            # Open intercom config file
            file = open("/etc/conf.d/sipradio/icomradioCnfg.conf", "w")

            # Update config data
            iCnfg[0]['icomloc'] = request.json['icomloc']
            icomLoc = iCnfg[0]['icomloc']
            
            # Copy the rest (no update) data
            tmpIcomSet = 'ICOMSET:'
            tmpIcomSet = tmpIcomSet + icomSet + '\n'
            file.write(tmpIcomSet)

            # Create new text file for a new data
            tmpIcomLoc = 'ICOMLOC:'
            tmpIcomLoc = tmpIcomLoc + icomLoc + '\n'
            file.write(tmpIcomSet)

            tmpIcomExtId = 'EXTID:'
            tmpIcomExtId = tmpIcomExtId + icomExtId + '\n'
            file.write(tmpIcomExtId)

            # Close the file
            file.close()

    # Update intercom config - Intercom group extensions id
    elif 'icomextid' in request.json:
        tempIcomExtId = request.json['icomextid']

        # Update intercom group extension id
        if tempIcomExtId != 'RETRIEVE':
            # Open intercom config file
            file = open("/etc/conf.d/sipradio/icomradioCnfg.conf", "w")

            # Update config data
            iCnfg[0]['icomextid'] = request.json['icomextid']
            icomExtId = iCnfg[0]['icomextid']
            
            # Copy the rest (no update) data
            tmpIcomSet = 'ICOMSET:'
            tmpIcomSet = tmpIcomSet + icomSet + '\n'
            file.write(tmpIcomSet)

            # Copy the rest (no update) data
            tmpIcomLoc = 'ICOMLOC:'
            tmpIcomLoc = tmpIcomLoc + icomLoc + '\n'
            file.write(tmpIcomLoc)

            # Create new text file for a new data
            tmpIcomExtId = 'EXTID:'
            tmpIcomExtId = tmpIcomExtId + icomExtId + '\n'
            file.write(tmpIcomExtId)

            # Close the file
            file.close()

    return jsonify({'intercomconfig': iCnfg})

# Update setting for VOX controller configuration
# Example command to send:
# curl -i -H "Content-type: application/json" -X PUT -d "{\"delayaindiv\":\"1002\"}" http://192.168.101.1:5000/voxconfig/000
@app.route('/voxconfig/<cnfgid>', methods=['PUT'])
def updateVoxConfigData(cnfgid):
    global delayaindiv
    global pDelayaindiv
    global delayvaladd
    global pDelayvaladd
    global threshmultp
    global pThreshmultp
    global threshadd
    global pThreshadd
    global delayvalue
    global pDelayvalue
    global thresholdvalue
    global pThresvalue
    global voxMode
    global pVoxMode
    global sendCmdType
    global commBusy

    tempDlyInpDiv = ''
    tempDlyInpAdd = ''
    tempThresMultp = ''
    tempThresAdd = ''
    tempDlyVal = ''
    tempThresVal = ''
    tempMode = ''
    
    # Communication between RIC and VOX controller are still in configuring mode
    if commBusy == False:
        vCnfg = [ vCnfgG for vCnfgG in voxParamData if (vCnfgG['id'] == cnfgid) ]
        # Update VOX config - PTT delay analog input delay division factor
        if 'delayaindiv' in request.json:
            tempDlyInpDiv = request.json['delayaindiv']
            
            if tempDlyInpDiv != 'RETRIEVE':
                # Open VOX config file
                #file = open("/etc/conf.d/sipHFradio/voxHFradioCnfg.conf", "w")
                file = open("/etc/conf.d/sipradio/voxradioCnfg.conf", "w")

                # Update config data
                vCnfg[0]['delayaindiv'] = request.json['delayaindiv']

                pDelayaindiv = delayaindiv # Copy previous value as a backup if configuring VOX controller failed
                delayaindiv = vCnfg[0]['delayaindiv']
                            
                # Create new text file for a new data
                dlyAinDiv = 'DELAYAINDIV:'
                dlyAinDiv = dlyAinDiv + delayaindiv + '\n'
                file.write(dlyAinDiv)

                # Copy the rest (no update) data
                dlyValAdd = 'DELAYVALADD:'
                dlyValAdd = dlyValAdd + delayvaladd + '\n'
                file.write(dlyValAdd)

                thrMultp = 'THRESHMULTP:'
                thrMultp = thrMultp + threshmultp + '\n'
                file.write(thrMultp)

                thrAdd = 'THRESHADD:'
                thrAdd = thrAdd + threshadd + '\n'
                file.write(thrAdd)

                dlyVal = 'DELAYVALUE:'
                dlyVal = dlyVal + delayvalue + '\n'
                file.write(dlyVal)

                thrVal = 'THRESHOLDVALUE:'
                thrVal = thrVal + thresholdvalue + '\n'
                file.write(thrVal)

                voXmode = 'MODE:'
                voXmode = voXmode + voxMode + '\n'
                file.write(voXmode)

                # Close the file
                file.close()

                # Send command to VOX controller
                sendCmdType = 1
        # Update VOX config - VOX PTT delay addition factor
        elif 'delayvaladd' in request.json:
            tempDlyInpAdd = request.json['delayvaladd']

            if tempDlyInpAdd != 'RETRIEVE':
                # Open VOX config file
                #file = open("/etc/conf.d/sipHFradio/voxHFradioCnfg.conf", "w")
                file = open("/etc/conf.d/sipradio/voxradioCnfg.conf", "w")
                
                # Copy the rest (no update) data
                dlyAinDiv = 'DELAYAINDIV:'
                dlyAinDiv = dlyAinDiv + delayaindiv + '\n'
                file.write(dlyAinDiv)

                # Update config data
                vCnfg[0]['delayvaladd'] = request.json['delayvaladd']

                pDelayvaladd = delayvaladd # Copy previous value as a backup if configuring VOX controller failed
                delayvaladd = vCnfg[0]['delayvaladd']
                            
                # Create new text file for a new data
                dlyValAdd = 'DELAYVALADD:'
                dlyValAdd = dlyValAdd + delayvaladd + '\n'
                file.write(dlyValAdd)

                # Copy the rest (no update) data....continues
                thrMultp = 'THRESHMULTP:'
                thrMultp = thrMultp + threshmultp + '\n'
                file.write(thrMultp)

                thrAdd = 'THRESHADD:'
                thrAdd = thrAdd + threshadd + '\n'
                file.write(thrAdd)

                dlyVal = 'DELAYVALUE:'
                dlyVal = dlyVal + delayvalue + '\n'
                file.write(dlyVal)

                thrVal = 'THRESHOLDVALUE:'
                thrVal = thrVal + thresholdvalue + '\n'
                file.write(thrVal)

                voXmode = 'MODE:'
                voXmode = voXmode + voxMode + '\n'
                file.write(voXmode)

                # Close the file
                file.close()

                # Send command to VOX controller
                sendCmdType = 2
        # Update VOX config - VOX threshold analog input multiplication factor
        elif 'threshmultp' in request.json:
            tempThresMultp = request.json['threshmultp']

            if tempThresMultp != 'RETRIEVE':
                # Open VOX config file
                #file = open("/etc/conf.d/sipHFradio/voxHFradioCnfg.conf", "w")
                file = open("/etc/conf.d/sipradio/voxradioCnfg.conf", "w")

                # Copy the rest (no update) data
                dlyAinDiv = 'DELAYAINDIV:'
                dlyAinDiv = dlyAinDiv + delayaindiv + '\n'
                file.write(dlyAinDiv)

                dlyValAdd = 'DELAYVALADD:'
                dlyValAdd = dlyValAdd + delayvaladd + '\n'
                file.write(dlyValAdd)

                # Update config data
                vCnfg[0]['threshmultp'] = request.json['threshmultp']

                pThreshmultp = threshmultp # Copy previous value as a backup if configuring VOX controller failed
                threshmultp = vCnfg[0]['threshmultp']
                            
                # Create new text file for a new data
                thrMultp = 'THRESHMULTP:'
                thrMultp = thrMultp + threshmultp + '\n'
                file.write(thrMultp)

                # Copy the rest (no update) data....continues
                thrAdd = 'THRESHADD:'
                thrAdd = thrAdd + threshadd + '\n'
                file.write(thrAdd)

                dlyVal = 'DELAYVALUE:'
                dlyVal = dlyVal + delayvalue + '\n'
                file.write(dlyVal)

                thrVal = 'THRESHOLDVALUE:'
                thrVal = thrVal + thresholdvalue + '\n'
                file.write(thrVal)

                voXmode = 'MODE:'
                voXmode = voXmode + voxMode + '\n'
                file.write(voXmode)

                # Close the file
                file.close()

                # Send command to VOX controller
                sendCmdType = 3
        # Update VOX config - VOX threshold analog input addition factor
        elif 'threshadd' in request.json:
            tempThresAdd = request.json['threshadd']

            if tempThresAdd != 'RETRIEVE':
                # Open VOX config file
                #file = open("/etc/conf.d/sipHFradio/voxHFradioCnfg.conf", "w")
                file = open("/etc/conf.d/sipradio/voxradioCnfg.conf", "w")

                # Copy the rest (no update) data
                dlyAinDiv = 'DELAYAINDIV:'
                dlyAinDiv = dlyAinDiv + delayaindiv + '\n'
                file.write(dlyAinDiv)

                dlyValAdd = 'DELAYVALADD:'
                dlyValAdd = dlyValAdd + delayvaladd + '\n'
                file.write(dlyValAdd)

                thrMultp = 'THRESHMULTP:'
                thrMultp = thrMultp + threshmultp + '\n'
                file.write(thrMultp)

                # Update config data
                vCnfg[0]['threshadd'] = request.json['threshadd']

                pThreshadd = threshadd # Copy previous value as a backup if configuring VOX controller failed
                threshadd = vCnfg[0]['threshadd']
                            
                # Create new text file for a new data
                thrAdd = 'THRESHADD:'
                thrAdd = thrAdd + threshadd + '\n'
                file.write(thrAdd)

                # Copy the rest (no update) data....continues
                dlyVal = 'DELAYVALUE:'
                dlyVal = dlyVal + delayvalue + '\n'
                file.write(dlyVal)

                thrVal = 'THRESHOLDVALUE:'
                thrVal = thrVal + thresholdvalue + '\n'
                file.write(thrVal)

                voXmode = 'MODE:'
                voXmode = voXmode + voxMode + '\n'
                file.write(voXmode)

                # Close the file
                file.close()

                # Send command to VOX controller
                sendCmdType = 4
        # Update VOX config - VOX total delay
        elif 'delayvalue' in request.json:
            tempDlyVal = request.json['delayvalue']

            if tempDlyVal != 'RETRIEVE':
                # Open VOX config file
                #file = open("/etc/conf.d/sipHFradio/voxHFradioCnfg.conf", "w")
                file = open("/etc/conf.d/sipradio/voxradioCnfg.conf", "w")

                # Copy the rest (no update) data
                dlyAinDiv = 'DELAYAINDIV:'
                dlyAinDiv = dlyAinDiv + delayaindiv + '\n'
                file.write(dlyAinDiv)

                dlyValAdd = 'DELAYVALADD:'
                dlyValAdd = dlyValAdd + delayvaladd + '\n'
                file.write(dlyValAdd)

                thrMultp = 'THRESHMULTP:'
                thrMultp = thrMultp + threshmultp + '\n'
                file.write(thrMultp)

                thrAdd = 'THRESHADD:'
                thrAdd = thrAdd + threshadd + '\n'
                file.write(thrAdd)

                # Update config data
                vCnfg[0]['delayvalue'] = request.json['delayvalue']

                pDelayvalue = delayvalue # Copy previous value as a backup if configuring VOX controller failed
                delayvalue = vCnfg[0]['delayvalue']
                            
                # Create new text file for a new data
                dlyVal = 'DELAYVALUE:'
                dlyVal = dlyVal + delayvalue + '\n'
                file.write(dlyVal)

                # Copy the rest (no update) data....continues
                thrVal = 'THRESHOLDVALUE:'
                thrVal = thrVal + thresholdvalue + '\n'
                file.write(thrVal)

                voXmode = 'MODE:'
                voXmode = voXmode + voxMode + '\n'
                file.write(voXmode)

                # Close the file
                file.close()

                # Send command to VOX controller
                sendCmdType = 5
        # Update VOX config - VOX total threshold
        elif 'thresholdvalue' in request.json:
            tempThresVal = request.json['thresholdvalue']

            if tempThresVal != 'RETRIEVE':
                # Open VOX config file
                #file = open("/etc/conf.d/sipHFradio/voxHFradioCnfg.conf", "w")
                file = open("/etc/conf.d/sipradio/voxradioCnfg.conf", "w")

                # Copy the rest (no update) data
                dlyAinDiv = 'DELAYAINDIV:'
                dlyAinDiv = dlyAinDiv + delayaindiv + '\n'
                file.write(dlyAinDiv)

                dlyValAdd = 'DELAYVALADD:'
                dlyValAdd = dlyValAdd + delayvaladd + '\n'
                file.write(dlyValAdd)

                thrMultp = 'THRESHMULTP:'
                thrMultp = thrMultp + threshmultp + '\n'
                file.write(thrMultp)

                thrAdd = 'THRESHADD:'
                thrAdd = thrAdd + threshadd + '\n'
                file.write(thrAdd)

                dlyVal = 'DELAYVALUE:'
                dlyVal = dlyVal + delayvalue + '\n'
                file.write(dlyVal)

                # Update config data
                vCnfg[0]['thresholdvalue'] = request.json['thresholdvalue']

                pThresvalue = thresholdvalue # Copy previous value as a backup if configuring VOX controller failed
                thresholdvalue = vCnfg[0]['thresholdvalue']
                            
                # Create new text file for a new data
                thrVal = 'THRESHOLDVALUE:'
                thrVal = thrVal + thresholdvalue + '\n'
                file.write(thrVal)
                
                # Copy the rest (no update) data....continues
                voXmode = 'MODE:'
                voXmode = voXmode + voxMode + '\n'
                file.write(voXmode)

                # Close the file
                file.close()

                # Send command to VOX controller
                sendCmdType = 6
        # Update VOX config - VOX controller current mode
        elif 'mode' in request.json:
            tempMode = request.json['mode']

            if tempMode != 'RETRIEVE':
                # Open VOX config file
                #file = open("/etc/conf.d/sipHFradio/voxHFradioCnfg.conf", "w")
                file = open("/etc/conf.d/sipradio/voxradioCnfg.conf", "w")

                # Copy the rest (no update) data
                dlyAinDiv = 'DELAYAINDIV:'
                dlyAinDiv = dlyAinDiv + delayaindiv + '\n'
                file.write(dlyAinDiv)

                dlyValAdd = 'DELAYVALADD:'
                dlyValAdd = dlyValAdd + delayvaladd + '\n'
                file.write(dlyValAdd)

                thrMultp = 'THRESHMULTP:'
                thrMultp = thrMultp + threshmultp + '\n'
                file.write(thrMultp)

                thrAdd = 'THRESHADD:'
                thrAdd = thrAdd + threshadd + '\n'
                file.write(thrAdd)

                dlyVal = 'DELAYVALUE:'
                dlyVal = dlyVal + delayvalue + '\n'
                file.write(dlyVal)

                thrVal = 'THRESHOLDVALUE:'
                thrVal = thrVal + thresholdvalue + '\n'
                file.write(thrVal)

                # Update config data
                pVoxMode = voxMode # Copy previous value as a backup if configuring VOX controller failed
                voxMode = request.json['mode']
                if voxMode == '1':
                    vCnfg[0]['mode'] = 'Mode 1'
                else:
                    vCnfg[0]['mode'] = 'Mode 2'

                # Update RIC daemon status REST API data
                ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                ric[0]['voxmode'] = vCnfg[0]['mode']
        
                # Create new text file for a new data
                voXmode = 'MODE:'
                voXmode = voXmode + voxMode + '\n'
                file.write(voXmode)

                # Close the file
                file.close()

                # Send command to VOX controller
                sendCmdType = 7
    return jsonify({'voxconfig': vCnfg})

# Handle Cross-Origin (CORS) problem upon client request
@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')

    return response

# Get current setting for local SIP configuration
# Example command to send:
# http://192.168.101.1:5000/sipconfig
@app.route('/sipconfig', methods=['GET'])
def getSipConfigData():
    return jsonify({'sipConfig': sipConfigData}) 

# Update setting for local SIP configuration
# Example command to send:
# curl -i -H "Content-type: application/json" -X PUT -d "{\"sipusername\":\"1002\"}" http://192.168.101.1:5000/sipconfig/000
# 'RETRIEVE' value are only to retrieve current setting
@app.route('/sipconfig/<cnfgid>', methods=['PUT'])
def updateSipConfigData(cnfgid):
    global sipUserName
    global sipPswd
    global asteriskIP
    global pttSet
    global micSet
    global audioSet
    global audMultSet
    global pttToVal
    global pttMode
    global pttModeOper

    tempSipUName = ''
    tempSipPswd = ''
    tempAstIp = ''
    tempPttSet = ''
    tempMicSet = ''
    tempAudSet = ''
    tempAudMSet = ''
    tempPttTo = ''
    tempPttMod = ''
    
    cnfg = [ cnfgG for cnfgG in sipConfigData if (cnfgG['id'] == cnfgid) ]
    # Update SIP user name
    if 'sipusername' in request.json:
        tempSipUName = request.json['sipusername']
                    
        # It is to update SIP user name
        if tempSipUName != 'RETRIEVE':
            # Open SIP config file
            #file = open("/etc/conf.d/sipHFradio/sipHFradioCnfg.conf", "w")
            file = open("/etc/conf.d/sipradio/sipradioCnfg.conf", "w")

            # Update config data
            cnfg[0]['sipusername'] = request.json['sipusername']
            sipUserName = cnfg[0]['sipusername']
            
            # Create new text file for a new data
            sipuname = 'SIPUSERNAME:'
            sipuname = sipuname + sipUserName + '\n'
            file.write(sipuname)
                    
            # Copy the rest (no update) data
            sippswd = 'SIPPSWD:'
            sippswd = sippswd + sipPswd + '\n'
            file.write(sippswd)
            
            astip = 'ASTERISKIP:'
            astip = astip + asteriskIP + '\n'
            file.write(astip)

            pttset = 'PTTSET:'
            pttset = pttset + pttSet + '\n'
            file.write(pttset)

            micset = 'MICSET:'
            micset = micset + micSet + '\n'
            file.write(micset)

            audioset = 'AUDIOSET:'
            audioset = audioset + audioSet + '\n'
            file.write(audioset)

            audmultset = 'AUDMULTSET:'
            audmultset = audmultset + audMultSet + '\n'
            file.write(audmultset)
            
            ptttoval = 'PTTTO:'
            ptttoval = ptttoval + pttToVal + '\n'
            file.write(ptttoval)
            
            pttmode = 'PTTMODE:'
            pttmode = pttmode + pttMode + '\n'
            file.write(pttmode)

            # Close the file
            file.close()
    # Update SIP password
    elif 'sippassword' in request.json:
        tempSipPswd = request.json['sippassword']
        
        # It is to update SIP password
        if tempSipPswd != 'RETRIEVE': 
            # Open SIP config file
            #file = open("/etc/conf.d/sipHFradio/sipHFradioCnfg.conf", "w")
            file = open("/etc/conf.d/sipradio/sipradioCnfg.conf", "w")

            # Update config data
            cnfg[0]['sippassword'] = request.json['sippassword']
            sipPswd = cnfg[0]['sippassword']
            
            # Copy the rest (no update) data
            sipuname = 'SIPUSERNAME:'
            sipuname = sipuname + sipUserName + '\n'
            file.write(sipuname)

            # Create new text file for a new data
            sippswd = 'SIPPSWD:'
            sippswd = sippswd + sipPswd + '\n'
            file.write(sippswd)

            # Copy the rest (no update) data....continues
            astip = 'ASTERISKIP:'
            astip = astip + asteriskIP + '\n'
            file.write(astip)

            pttset = 'PTTSET:'
            pttset = pttset + pttSet + '\n'
            file.write(pttset)

            micset = 'MICSET:'
            micset = micset + micSet + '\n'
            file.write(micset)

            audioset = 'AUDIOSET:'
            audioset = audioset + audioSet + '\n'
            file.write(audioset)

            audmultset = 'AUDMULTSET:'
            audmultset = audmultset + audMultSet + '\n'
            file.write(audmultset)
            
            ptttoval = 'PTTTO:'
            ptttoval = ptttoval + pttToVal + '\n'
            file.write(ptttoval)
            
            pttmode = 'PTTMODE:'
            pttmode = pttmode + pttMode + '\n'
            file.write(pttmode)

            # Close the file
            file.close()
    # Update ASTERISK IP address
    elif 'asteriskip' in request.json:
        tempAstIp = request.json['asteriskip']
                    
        # It is to update SIP registrar IP address
        if tempAstIp != 'RETRIEVE':
            # Open SIP config file
            #file = open("/etc/conf.d/sipHFradio/sipHFradioCnfg.conf", "w")
            file = open("/etc/conf.d/sipradio/sipradioCnfg.conf", "w")

            # Update config data
            cnfg[0]['asteriskip'] = request.json['asteriskip']
            asteriskIP = cnfg[0]['asteriskip']
            
            # Copy the rest (no update) data
            sipuname = 'SIPUSERNAME:'
            sipuname = sipuname + sipUserName + '\n'
            file.write(sipuname)

            sippswd = 'SIPPSWD:'
            sippswd = sippswd + sipPswd + '\n'
            file.write(sippswd)

            # Create new text file for a new data
            astip = 'ASTERISKIP:'
            astip = astip + asteriskIP + '\n'
            file.write(astip)

            # Copy the rest (no update) data....continues
            pttset = 'PTTSET:'
            pttset = pttset + pttSet + '\n'
            file.write(pttset)

            micset = 'MICSET:'
            micset = micset + micSet + '\n'
            file.write(micset)

            audioset = 'AUDIOSET:'
            audioset = audioset + audioSet + '\n'
            file.write(audioset)

            audmultset = 'AUDMULTSET:'
            audmultset = audmultset + audMultSet + '\n'
            file.write(audmultset)
            
            ptttoval = 'PTTTO:'
            ptttoval = ptttoval + pttToVal + '\n'
            file.write(ptttoval)
            
            pttmode = 'PTTMODE:'
            pttmode = pttmode + pttMode + '\n'
            file.write(pttmode)

            # Close the file
            file.close()
    # Update PTT setting - enable of disable
    elif 'pttset' in request.json:
        tempPttSet = request.json['pttset']
                    
        # It is to update PTT functionality
        if tempPttSet != 'RETRIEVE':
            # Open SIP config file
            #file = open("/etc/conf.d/sipHFradio/sipHFradioCnfg.conf", "w")
            file = open("/etc/conf.d/sipradio/sipradioCnfg.conf", "w")

            # Update config data
            cnfg[0]['pttset'] = request.json['pttset']
            pttSet = cnfg[0]['pttset']
            
            # Copy the rest (no update) data
            sipuname = 'SIPUSERNAME:'
            sipuname = sipuname + sipUserName + '\n'
            file.write(sipuname)

            sippswd = 'SIPPSWD:'
            sippswd = sippswd + sipPswd + '\n'
            file.write(sippswd)

            astip = 'ASTERISKIP:'
            astip = astip + asteriskIP + '\n'
            file.write(astip)

            # Create new text file for a new data
            pttset = 'PTTSET:'
            pttset = pttset + pttSet + '\n'
            file.write(pttset)

            # Copy the rest (no update) data....continues
            micset = 'MICSET:'
            micset = micset + micSet + '\n'
            file.write(micset)

            audioset = 'AUDIOSET:'
            audioset = audioset + audioSet + '\n'
            file.write(audioset)

            audmultset = 'AUDMULTSET:'
            audmultset = audmultset + audMultSet + '\n'
            file.write(audmultset)
            
            ptttoval = 'PTTTO:'
            ptttoval = ptttoval + pttToVal + '\n'
            file.write(ptttoval)
            
            pttmode = 'PTTMODE:'
            pttmode = pttmode + pttMode + '\n'
            file.write(pttmode)

            # Close the file
            file.close()
    # Update MIC setting - enable of disable
    elif 'micset' in request.json:
        tempMicSet = request.json['micset']
                    
        # It is to update MIC functionality
        if tempMicSet != 'RETRIEVE':
            # Open SIP config file
            #file = open("/etc/conf.d/sipHFradio/sipHFradioCnfg.conf", "w")
            file = open("/etc/conf.d/sipradio/sipradioCnfg.conf", "w")

            # Update config data
            cnfg[0]['micset'] = request.json['micset']
            micSet = cnfg[0]['micset']
            
            # Copy the rest (no update) data
            sipuname = 'SIPUSERNAME:'
            sipuname = sipuname + sipUserName + '\n'
            file.write(sipuname)

            sippswd = 'SIPPSWD:'
            sippswd = sippswd + sipPswd + '\n'
            file.write(sippswd)

            astip = 'ASTERISKIP:'
            astip = astip + asteriskIP + '\n'
            file.write(astip)

            pttset = 'PTTSET:'
            pttset = pttset + pttSet + '\n'
            file.write(pttset)

            # Create new text file for a new data
            micset = 'MICSET:'
            micset = micset + micSet + '\n'
            file.write(micset)

            # Copy the rest (no update) data....continues
            audioset = 'AUDIOSET:'
            audioset = audioset + audioSet + '\n'
            file.write(audioset)

            audmultset = 'AUDMULTSET:'
            audmultset = audmultset + audMultSet + '\n'
            file.write(audmultset)
            
            ptttoval = 'PTTTO:'
            ptttoval = ptttoval + pttToVal + '\n'
            file.write(ptttoval)
            
            pttmode = 'PTTMODE:'
            pttmode = pttmode + pttMode + '\n'
            file.write(pttmode)

            # Close the file
            file.close()
    # Update AUDIO setting - enable of disable
    elif 'audioset' in request.json:
        tempAudSet = request.json['audioset']
                    
        # It is to update AUDIO functionality
        if tempAudSet != 'RETRIEVE':
            # Open SIP config file
            #file = open("/etc/conf.d/sipHFradio/sipHFradioCnfg.conf", "w")
            file = open("/etc/conf.d/sipradio/sipradioCnfg.conf", "w")

            # Update config data
            cnfg[0]['audioset'] = request.json['audioset']
            audioSet = cnfg[0]['audioset']
            
            # Copy the rest (no update) data
            sipuname = 'SIPUSERNAME:'
            sipuname = sipuname + sipUserName + '\n'
            file.write(sipuname)

            sippswd = 'SIPPSWD:'
            sippswd = sippswd + sipPswd + '\n'
            file.write(sippswd)

            astip = 'ASTERISKIP:'
            astip = astip + asteriskIP + '\n'
            file.write(astip)

            pttset = 'PTTSET:'
            pttset = pttset + pttSet + '\n'
            file.write(pttset)

            micset = 'MICSET:'
            micset = micset + micSet + '\n'
            file.write(micset)

            # Create new text file for a new data
            audioset = 'AUDIOSET:'
            audioset = audioset + audioSet + '\n'
            file.write(audioset)

            # Copy the rest (no update) data....continues
            audmultset = 'AUDMULTSET:'
            audmultset = audmultset + audMultSet + '\n'
            file.write(audmultset)
            
            ptttoval = 'PTTTO:'
            ptttoval = ptttoval + pttToVal + '\n'
            file.write(ptttoval)
            
            pttmode = 'PTTMODE:'
            pttmode = pttmode + pttMode + '\n'
            file.write(pttmode)

            # Close the file
            file.close()
    # Update AUDIO MULTICAST setting - enable of disable
    elif 'audmultset' in request.json:
        tempAudMSet = request.json['audmultset']
                    
        # It is to update AUDIO MULTICAST functionality
        if tempAudMSet != 'RETRIEVE':
            # Open SIP config file
            #file = open("/etc/conf.d/sipHFradio/sipHFradioCnfg.conf", "w")
            file = open("/etc/conf.d/sipradio/sipradioCnfg.conf", "w")

            # Update config data
            cnfg[0]['audmultset'] = request.json['audmultset']
            audMultSet = cnfg[0]['audmultset']
            
            # Copy the rest (no update) data
            sipuname = 'SIPUSERNAME:'
            sipuname = sipuname + sipUserName + '\n'
            file.write(sipuname)

            sippswd = 'SIPPSWD:'
            sippswd = sippswd + sipPswd + '\n'
            file.write(sippswd)

            astip = 'ASTERISKIP:'
            astip = astip + asteriskIP + '\n'
            file.write(astip)

            pttset = 'PTTSET:'
            pttset = pttset + pttSet + '\n'
            file.write(pttset)

            micset = 'MICSET:'
            micset = micset + micSet + '\n'
            file.write(micset)

            audioset = 'AUDIOSET:'
            audioset = audioset + audioSet + '\n'
            file.write(audioset)

            # Create new text file for a new data
            audmultset = 'AUDMULTSET:'
            audmultset = audmultset + audMultSet + '\n'
            file.write(audmultset)

            # Copy the rest (no update) data....continues
            ptttoval = 'PTTTO:'
            ptttoval = ptttoval + pttToVal + '\n'
            file.write(ptttoval)
            
            pttmode = 'PTTMODE:'
            pttmode = pttmode + pttMode + '\n'
            file.write(pttmode)

            # Close the file
            file.close()
    # Update PTT time out value
    elif 'pttto' in request.json:
        tempPttTo = request.json['pttto']
                    
        # It is to update PTT time out value
        if tempPttTo != 'RETRIEVE':
            # Open SIP config file
            #file = open("/etc/conf.d/sipHFradio/sipHFradioCnfg.conf", "w")
            file = open("/etc/conf.d/sipradio/sipradioCnfg.conf", "w")

            # Update config data
            cnfg[0]['pttto'] = request.json['pttto']
            pttToVal = cnfg[0]['pttto']
            
            # Copy the rest (no update) data
            sipuname = 'SIPUSERNAME:'
            sipuname = sipuname + sipUserName + '\n'
            file.write(sipuname)

            sippswd = 'SIPPSWD:'
            sippswd = sippswd + sipPswd + '\n'
            file.write(sippswd)

            astip = 'ASTERISKIP:'
            astip = astip + asteriskIP + '\n'
            file.write(astip)

            pttset = 'PTTSET:'
            pttset = pttset + pttSet + '\n'
            file.write(pttset)

            micset = 'MICSET:'
            micset = micset + micSet + '\n'
            file.write(micset)

            audioset = 'AUDIOSET:'
            audioset = audioset + audioSet + '\n'
            file.write(audioset)

            audmultset = 'AUDMULTSET:'
            audmultset = audmultset + audMultSet + '\n'
            file.write(audmultset)

            # Create new text file for a new data
            ptttoval = 'PTTTO:'
            ptttoval = ptttoval + pttToVal + '\n'
            file.write(ptttoval)

            # Copy the rest (no update) data....continues
            pttmode = 'PTTMODE:'
            pttmode = pttmode + pttMode + '\n'
            file.write(pttmode)

            # Close the file
            file.close()
    # Update PTT mode of operation
    elif 'pttmode' in request.json:
        tempPttMod = request.json['pttmode']
                    
        # It is to update PTT mode of operation
        if tempPttMod != 'RETRIEVE':
            # Open SIP config file
            #file = open("/etc/conf.d/sipHFradio/sipHFradioCnfg.conf", "w")
            file = open("/etc/conf.d/sipradio/sipradioCnfg.conf", "w")

            # Update config data
            cnfg[0]['pttmode'] = request.json['pttmode']
            pttMode = cnfg[0]['pttmode']
            
            # Copy the rest (no update) data
            sipuname = 'SIPUSERNAME:'
            sipuname = sipuname + sipUserName + '\n'
            file.write(sipuname)

            sippswd = 'SIPPSWD:'
            sippswd = sippswd + sipPswd + '\n'
            file.write(sippswd)

            astip = 'ASTERISKIP:'
            astip = astip + asteriskIP + '\n'
            file.write(astip)

            pttset = 'PTTSET:'
            pttset = pttset + pttSet + '\n'
            file.write(pttset)

            micset = 'MICSET:'
            micset = micset + micSet + '\n'
            file.write(micset)

            audioset = 'AUDIOSET:'
            audioset = audioset + audioSet + '\n'
            file.write(audioset)

            audmultset = 'AUDMULTSET:'
            audmultset = audmultset + audMultSet + '\n'
            file.write(audmultset)

            ptttoval = 'PTTTO:'
            ptttoval = ptttoval + pttToVal + '\n'
            file.write(ptttoval)

            pttModeOper = int(pttMode) # Update PTT mode to be use in PTT logic of operation
            
            # Create new text file for a new data
            pttmode = 'PTTMODE:'
            pttmode = pttmode + pttMode + '\n'
            file.write(pttmode)

            # Mode 1
            if pttModeOper == 1:
                # Initialize PTT mode relay OFF
                GPIO.output(12, GPIO.LOW)

                # Update RIC daemon status REST API data
                ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                ric[0]['pttmode'] = 'Mode 1'
            # Mode 2
            elif pttModeOper == 2:
                # Initialize PTT mode relay OFF
                GPIO.output(12, GPIO.LOW)
        
                # Update RIC daemon status REST API data
                ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                ric[0]['pttmode'] = 'Mode 2'
            # Mode 3
            elif pttModeOper == 3:
                # Initialize PTT mode relay OFF
                GPIO.output(12, GPIO.HIGH)
        
                # Update RIC daemon status REST API data
                ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                ric[0]['pttmode'] = 'Mode 3'
        
    return jsonify({'sipConfig': cnfg}) 

# Revert back VOX configuration data to previous value
def revertVOXdata (cmdType):
    global delayaindiv
    global pDelayaindiv
    global delayvaladd
    global pDelayvaladd
    global threshmultp
    global pThreshmultp
    global threshadd
    global pThreshadd
    global delayvalue
    global pDelayvalue
    global thresholdvalue
    global pThresvalue
    global voxMode
    global pVoxMode

    vCnfg = [ vCnfgG for vCnfgG in voxParamData if (vCnfgG['id'] == '000') ]

    # Restore VOX config - PTT delay analog input delay division factor
    if cmdType == 1:
        # Open VOX config file
        #file = open("/etc/conf.d/sipHFradio/voxHFradioCnfg.conf", "w")
        file = open("/etc/conf.d/sipradio/voxradioCnfg.conf", "w")

        # Restore config data
        vCnfg[0]['delayaindiv'] = pDelayaindiv
        delayaindiv = pDelayaindiv # Restore back current value
        
        # Restore new text file with a previous data
        dlyAinDiv = 'DELAYAINDIV:'
        dlyAinDiv = dlyAinDiv + pDelayaindiv + '\n'
        pDelayaindiv = ''
        file.write(dlyAinDiv)

        # Copy the rest (no restore) data
        dlyValAdd = 'DELAYVALADD:'
        dlyValAdd = dlyValAdd + delayvaladd + '\n'
        file.write(dlyValAdd)

        thrMultp = 'THRESHMULTP:'
        thrMultp = thrMultp + threshmultp + '\n'
        file.write(thrMultp)

        thrAdd = 'THRESHADD:'
        thrAdd = thrAdd + threshadd + '\n'
        file.write(thrAdd)

        dlyVal = 'DELAYVALUE:'
        dlyVal = dlyVal + delayvalue + '\n'
        file.write(dlyVal)

        thrVal = 'THRESHOLDVALUE:'
        thrVal = thrVal + thresholdvalue + '\n'
        file.write(thrVal)

        voXmode = 'MODE:'
        voXmode = voXmode + voxMode + '\n'
        file.write(voXmode)

        # Close the file
        file.close()
    # Restore VOX config - VOX PTT delay addition factor
    elif cmdType == 2:
        # Open VOX config file
        #file = open("/etc/conf.d/sipHFradio/voxHFradioCnfg.conf", "w")
        file = open("/etc/conf.d/sipradio/voxradioCnfg.conf", "w")

        # Copy the rest (no restore) data
        dlyAinDiv = 'DELAYAINDIV:'
        dlyAinDiv = dlyAinDiv + delayaindiv + '\n'
        file.write(dlyAinDiv)

        # Restore config data
        vCnfg[0]['delayvaladd'] = pDelayvaladd
        delayvaladd = pDelayvaladd # Restore back current value
        
        # Restore new text file with a previous data
        dlyValAdd = 'DELAYVALADD:'
        dlyValAdd = dlyValAdd + pDelayvaladd + '\n'
        pDelayvaladd = ''
        file.write(dlyValAdd)

        # Copy the rest (no restore) data
        thrMultp = 'THRESHMULTP:'
        thrMultp = thrMultp + threshmultp + '\n'
        file.write(thrMultp)

        thrAdd = 'THRESHADD:'
        thrAdd = thrAdd + threshadd + '\n'
        file.write(thrAdd)

        dlyVal = 'DELAYVALUE:'
        dlyVal = dlyVal + delayvalue + '\n'
        file.write(dlyVal)

        thrVal = 'THRESHOLDVALUE:'
        thrVal = thrVal + thresholdvalue + '\n'
        file.write(thrVal)

        voXmode = 'MODE:'
        voXmode = voXmode + voxMode + '\n'
        file.write(voXmode)

        # Close the file
        file.close()
    # Restore VOX config - VOX threshold analog input multiplication factor
    elif cmdType == 3:
        # Open VOX config file
        #file = open("/etc/conf.d/sipHFradio/voxHFradioCnfg.conf", "w")
        file = open("/etc/conf.d/sipradio/voxradioCnfg.conf", "w")

        # Copy the rest (no restore) data
        dlyAinDiv = 'DELAYAINDIV:'
        dlyAinDiv = dlyAinDiv + delayaindiv + '\n'
        file.write(dlyAinDiv)

        dlyValAdd = 'DELAYVALADD:'
        dlyValAdd = dlyValAdd + delayvaladd + '\n'
        file.write(dlyValAdd)

        # Restore config data
        vCnfg[0]['threshmultp'] = pThreshmultp
        threshmultp = pThreshmultp # Restore back current value
        
        # Restore new text file with a previous data
        thrMultp = 'THRESHMULTP:'
        thrMultp = thrMultp + pThreshmultp + '\n'
        pThreshmultp = ''
        file.write(thrMultp)

        # Copy the rest (no restore) data....continues
        thrAdd = 'THRESHADD:'
        thrAdd = thrAdd + threshadd + '\n'
        file.write(thrAdd)

        dlyVal = 'DELAYVALUE:'
        dlyVal = dlyVal + delayvalue + '\n'
        file.write(dlyVal)

        thrVal = 'THRESHOLDVALUE:'
        thrVal = thrVal + thresholdvalue + '\n'
        file.write(thrVal)

        voXmode = 'MODE:'
        voXmode = voXmode + voxMode + '\n'
        file.write(voXmode)

        # Close the file
        file.close()
    # Restore VOX config - VOX threshold analog input addition factor
    elif cmdType == 4:
        # Open VOX config file
        #file = open("/etc/conf.d/sipHFradio/voxHFradioCnfg.conf", "w")
        file = open("/etc/conf.d/sipradio/voxradioCnfg.conf", "w")

        # Copy the rest (no restore) data
        dlyAinDiv = 'DELAYAINDIV:'
        dlyAinDiv = dlyAinDiv + delayaindiv + '\n'
        file.write(dlyAinDiv)

        dlyValAdd = 'DELAYVALADD:'
        dlyValAdd = dlyValAdd + delayvaladd + '\n'
        file.write(dlyValAdd)

        thrMultp = 'THRESHMULTP:'
        thrMultp = thrMultp + threshmultp + '\n'
        file.write(thrMultp)

        # Restore config data
        vCnfg[0]['threshadd'] = pThreshadd
        threshadd = pThreshadd # Restore back current value
        
        # Restore new text file with a previous data
        thrAdd = 'THRESHADD:'
        thrAdd = thrAdd + pThreshadd + '\n'
        pThreshadd = ''
        file.write(thrAdd)

        # Copy the rest (no update) data....continues
        dlyVal = 'DELAYVALUE:'
        dlyVal = dlyVal + delayvalue + '\n'
        file.write(dlyVal)

        thrVal = 'THRESHOLDVALUE:'
        thrVal = thrVal + thresholdvalue + '\n'
        file.write(thrVal)

        voXmode = 'MODE:'
        voXmode = voXmode + voxMode + '\n'
        file.write(voXmode)

        # Close the file
        file.close()
    # Update VOX config - VOX total delay
    elif cmdType == 5:
        # Open VOX config file
        #file = open("/etc/conf.d/sipHFradio/voxHFradioCnfg.conf", "w")
        file = open("/etc/conf.d/sipradio/voxradioCnfg.conf", "w")

        # Copy the rest (no restore) data
        dlyAinDiv = 'DELAYAINDIV:'
        dlyAinDiv = dlyAinDiv + delayaindiv + '\n'
        file.write(dlyAinDiv)

        dlyValAdd = 'DELAYVALADD:'
        dlyValAdd = dlyValAdd + delayvaladd + '\n'
        file.write(dlyValAdd)

        thrMultp = 'THRESHMULTP:'
        thrMultp = thrMultp + threshmultp + '\n'
        file.write(thrMultp)

        thrAdd = 'THRESHADD:'
        thrAdd = thrAdd + threshadd + '\n'
        file.write(thrAdd)

        # Update config data
        vCnfg[0]['delayvalue'] = pDelayvalue
        delayvalue = pDelayvalue # Restore back current value
        
        # Restore new text file with a previous data
        dlyVal = 'DELAYVALUE:'
        dlyVal = dlyVal + pDelayvalue + '\n'
        file.write(dlyVal)

        # Copy the rest (no restore) data....continues
        thrVal = 'THRESHOLDVALUE:'
        thrVal = thrVal + thresholdvalue + '\n'
        file.write(thrVal)

        voXmode = 'MODE:'
        voXmode = voXmode + voxMode + '\n'
        file.write(voXmode)

        # Close the file
        file.close()
    # Restore VOX config - VOX total threshold
    elif cmdType == 6:
        # Open VOX config file
        #file = open("/etc/conf.d/sipHFradio/voxHFradioCnfg.conf", "w")
        file = open("/etc/conf.d/sipradio/voxradioCnfg.conf", "w")

        # Copy the rest (no restore) data
        dlyAinDiv = 'DELAYAINDIV:'
        dlyAinDiv = dlyAinDiv + delayaindiv + '\n'
        file.write(dlyAinDiv)

        dlyValAdd = 'DELAYVALADD:'
        dlyValAdd = dlyValAdd + delayvaladd + '\n'
        file.write(dlyValAdd)

        thrMultp = 'THRESHMULTP:'
        thrMultp = thrMultp + threshmultp + '\n'
        file.write(thrMultp)

        thrAdd = 'THRESHADD:'
        thrAdd = thrAdd + threshadd + '\n'
        file.write(thrAdd)

        dlyVal = 'DELAYVALUE:'
        dlyVal = dlyVal + delayvalue + '\n'
        file.write(dlyVal)

        # Restore config data
        vCnfg[0]['thresholdvalue'] = pThresvalue
        thresholdvalue = pThresvalue # Restore back current value

        # Restore new text file with a previous data
        thrVal = 'THRESHOLDVALUE:'
        thrVal = thrVal + pThresvalue + '\n'
        file.write(thrVal)
        
        # Copy the rest (no update) data....continues
        voXmode = 'MODE:'
        voXmode = voXmode + voxMode + '\n'
        file.write(voXmode)

        # Close the file
        file.close()
    # Restore VOX config - VOX controller current mode
    elif cmdType == 7:
        # Open VOX config file
        #file = open("/etc/conf.d/sipHFradio/voxHFradioCnfg.conf", "w")
        file = open("/etc/conf.d/sipradio/voxradioCnfg.conf", "w")

        # Copy the rest (no restore) data
        dlyAinDiv = 'DELAYAINDIV:'
        dlyAinDiv = dlyAinDiv + delayaindiv + '\n'
        file.write(dlyAinDiv)

        dlyValAdd = 'DELAYVALADD:'
        dlyValAdd = dlyValAdd + delayvaladd + '\n'
        file.write(dlyValAdd)

        thrMultp = 'THRESHMULTP:'
        thrMultp = thrMultp + threshmultp + '\n'
        file.write(thrMultp)

        thrAdd = 'THRESHADD:'
        thrAdd = thrAdd + threshadd + '\n'
        file.write(thrAdd)

        dlyVal = 'DELAYVALUE:'
        dlyVal = dlyVal + delayvalue + '\n'
        file.write(dlyVal)

        thrVal = 'THRESHOLDVALUE:'
        thrVal = thrVal + thresholdvalue + '\n'
        file.write(thrVal)

        # Restore config data
        voxMode = pVoxMode # Restore back current value
        if pVoxMode == '1':
            vCnfg[0]['mode'] = 'Mode 1'
        else:
            vCnfg[0]['mode'] = 'Mode 2'
            
        # Update RIC daemon status REST API data
        ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
        ric[0]['voxmode'] = vCnfg[0]['mode']
            
        # Create new text file for a new data
        voXmode = 'MODE:'
        voXmode = voXmode + pVoxMode + '\n'
        file.write(voXmode)

        # Close the file
        file.close()        
            
# Thread for serial communication with VOX controller
def serial_vox_comm (threadname, delay):
    global delayaindiv
    global delayvaladd
    global threshmultp
    global threshadd
    global delayvalue
    global thresholdvalue
    global voxMode
    global sendCmdType 
    global commBusy
    
    retryDatToSend = ''
    sendAtmptCnt = 0
    sendAliveCnt = 0
    txOneSec = 0
    cmdSent = False
    
    # Serial communication port for VOX controller configuration
    serPort = "/dev/serial0"    # VOX controller detected serial port
    serPortBRate = 9600         # Serial communication baudrate

    # Open serial communication port with VOX controller
    voxSerComm = serial.Serial(serPort, serPortBRate)
    voxSerComm.flushInput()

    # ACK command data from VOX controller
    ackCommand = '<06>\n'
    while True:
        time.sleep(delay)
        # 0.5s elapsed
        if (txOneSec == 0):
            txOneSec = 1
        # 1s elapsed
        else:
            # NOT received any ACK command from VOX controller, resend the command
            if cmdSent == True:
                try:
                    # Send command to VOX controller
                    voxSerComm.write(retryDatToSend.encode())
                    
                    logger.info("DEBUG_VOX: RETRY SEND CMD: %s" % (retryDatToSend))
                except:
                    sendAtmptCnt += 1 # Increment send command attempt counter
                    # Reach 5 attempt, no need to send the command, update VOX configuration data to previous value
                    # Reset necessary variable
                    if sendAtmptCnt == 5:
                        retryDatToSend = ''
                        sendAtmptCnt = 0
                        cmdSent = False

                        # Update VOX configuration data to previous value
                        revertVOXdata(sendCmdType)

                        sendCmdType = 0
                        commBusy = False
                        
                    logger.info("DEBUG_VOX: ERROR during sending command!")
            else: 
                sendAliveCnt += 1 # Increment counter before request current VOX controller status 
                # Every 1 minute send VOX controller status request command
                if sendAliveCnt == 60:
                    try:
                        command = '<03>'
                        # Send command to VOX controller
                        voxSerComm.write(command.encode())

                        logger.info("DEBUG_VOX: SEND ALIVE CMD: %s" % (command))
                    except:
                        sendAliveCnt = 0
                        logger.info("DEBUG_VOX: ERROR during sending ALIVE request!")
                    sendAliveCnt = 0
            txOneSec = 0
            
        # Check for data availability
        if voxSerComm.inWaiting() > 0:
            rxData = voxSerComm.readline()
            # Received ACK from VOX controller
            if rxData == ackCommand:
                if commBusy == True:
                    commBusy = False
                    cmdSent = False
                    sendCmdType = 0

                    # Print serial data receive from VOX controller
                    logger.info("DEBUG_VOX: RECEIVE ACK FOR CONFIG. CMD: %s" % (rxData))
                else:
                    # Update RIC daemon status REST API data
                    ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                    ric[0]['voxstatus'] = 'ALIVE'
        
                    sendAliveCnt = 0
                    # Print serial data receive from VOX controller
                    logger.info("DEBUG_VOX: RECEIVE ACK FOR ALIVE: %s" % (rxData))
                
        # Check for any command to send 
        else:
            if cmdSent == False:
                # PTT delay analog input delay division factor
                if sendCmdType == 1:
                    # Mode 1
                    if voxMode == '1':
                        # Check param length - Valid value length are 1 - Default value are 5
                        # Experimental configuration range - 1 to 5
                        lengthStr = len(delayaindiv)
                        # Valid length
                        if lengthStr == 1:
                            dataToSend = '0' + delayaindiv
                            try:
                                command = '<0101' + dataToSend + '>'
                                retryDatToSend = command
                                
                                # Send command to VOX controller
                                voxSerComm.write(command.encode())
                                commBusy = True
                                cmdSent = True

                                logger.info("DEBUG_VOX: SEND CMD: %s" % (command))
                            except:
                                commBusy = True
                                cmdSent = True
                                
                                logger.info("DEBUG_VOX: ERROR during sending command!")
                        # Invalid length, don't send the command
                        else:
                            sendCmdType = 0
                            logger.info("DEBUG_VOX: Invalid data length for Mode 1 and data type [01]!")
                    else:
                        # Update VOX configuration data to previous value
                        revertVOXdata(sendCmdType)
                        
                        sendCmdType = 0
                        logger.info("DEBUG_VOX: Setting parameter with a wrong MODE")
                # VOX PTT delay addition factors
                elif sendCmdType == 2:
                    # Mode 1
                    if voxMode == '1':
                        # Check param length - Valid value length are are 1 or 2 - Default value are 2
                        # Experimental configuration range - 2 to 99
                        lengthStr = len(delayvaladd)
                        if (lengthStr == 1):
                            dataToSend = '0' + delayvaladd
                        elif (lengthStr == 2):
                            dataToSend = delayvaladd
                        # Valid length are 1 or 2
                        if lengthStr == 1 or lengthStr == 2:
                            try:
                                command = '<0102' + dataToSend + '>'
                                retryDatToSend = command
                                
                                # Send command to VOX controller
                                voxSerComm.write(command.encode())
                                commBusy = True
                                cmdSent = True
                                                                
                                logger.info("DEBUG_VOX: SEND CMD: %s" % (command))
                            except:
                                commBusy = True
                                cmdSent = True
                                
                                logger.info("DEBUG_VOX: ERROR during sending command!")
                        # Invalid length
                        else:
                            sendCmdType = 0
                            logger.info("DEBUG_VOX: Invalid data length for Mode 1 and data type [02]!")
                    else:
                        # Update VOX configuration data to previous value
                        revertVOXdata(sendCmdType)
                        
                        sendCmdType = 0
                        logger.info("DEBUG_VOX: Setting parameter with a wrong MODE")            
                # VOX threshold analog input multiplication factor
                elif sendCmdType == 3:
                    # Mode 1
                    if voxMode == '1':
                        # Check param length - Valid value length are are 3 (floating point) - Default value are 0.8
                        # Experimental configuration range - ???
                        lengthStr = len(threshmultp)
                        if (lengthStr == 3):
                            dataToSend = threshmultp
                            try:
                                command = '<0103' + dataToSend + '>'
                                retryDatToSend = command
                                
                                # Send command to VOX controller
                                voxSerComm.write(command.encode())
                                commBusy = True
                                cmdSent = True

                                logger.info("DEBUG_VOX: SEND CMD: %s" % (command))
                            except:
                                commBusy = True
                                cmdSent = True
                                
                                logger.info("DEBUG_VOX: ERROR during sending command!")
                        # Invalid length
                        else:
                            sendCmdType = 0
                            logger.info("DEBUG_VOX: Invalid data length for Mode 1 and data type [03]!")
                    else:
                        # Update VOX configuration data to previous value
                        revertVOXdata(sendCmdType)
                        
                        sendCmdType = 0
                        logger.info("DEBUG_VOX: Setting parameter with a wrong MODE")
                # VOX threshold analog input addition factor
                elif sendCmdType == 4:
                    # Mode 1
                    if voxMode == '1':
                        # Check param length - Valid value length are 1 or 2 - Default value are 70
                        # Experimental configuration range - 1 to 99
                        lengthStr = len(threshadd)
                        if (lengthStr == 1):
                            dataToSend = '0' + threshadd
                        elif (lengthStr == 2):
                            dataToSend = threshadd
                        # Valid length are 1 or 2
                        if lengthStr == 1 or lengthStr == 2:
                            try:
                                command = '<0104' + dataToSend + '>'
                                retryDatToSend = command
                                
                                # Send command to VOX controller
                                voxSerComm.write(command.encode())
                                commBusy = True
                                cmdSent = True

                                logger.info("DEBUG_VOX: SEND CMD: %s" % (command))
                            except:
                                commBusy = True
                                cmdSent = True
                                
                                logger.info("DEBUG_VOX: ERROR during sending command!")
                        # Invalid length
                        else:
                            sendCmdType = 0
                            logger.info("DEBUG_VOX: Invalid data length for Mode 1 and data type [04]!")
                    else:
                        # Update VOX configuration data to previous value
                        revertVOXdata(sendCmdType)
                        
                        sendCmdType = 0
                        logger.info("DEBUG_VOX: Setting parameter with a wrong MODE")

                # VOX total delay
                elif sendCmdType == 5:
                    # Mode 2
                    if voxMode == '2':
                        # Check param length - Valid value length are 1, 2 or 3 - Default value are 95
                        # Experimental configuration range - 2 to 999
                        lengthStr = len(delayvalue)
                        if lengthStr == 1:
                            dataToSend = '00' + delayvalue
                        elif lengthStr == 2:
                            dataToSend = '0' + delayvalue
                        elif lengthStr == 3:
                            dataToSend = delayvalue
                        # Valid length are 1, 2 or 3
                        if lengthStr == 1 or lengthStr == 2 or lengthStr == 3:
                            try:
                                command = '<0201' + dataToSend + '>'
                                retryDatToSend = command
                                
                                # Send command to VOX controller
                                voxSerComm.write(command.encode())
                                commBusy = True
                                cmdSent = True

                                logger.info("DEBUG_VOX: SEND CMD: %s" % (command))
                            except:
                                commBusy = True
                                cmdSent = True
                                
                                logger.info("DEBUG_VOX: ERROR during sending command!")
                        # Invalid length
                        else:
                            sendCmdType = 0
                            logger.info("DEBUG_VOX: Invalid data length for Mode 2 and data type [01]!")    
                    else:
                        # Update VOX configuration data to previous value
                        revertVOXdata(sendCmdType)
                        
                        sendCmdType = 0
                        logger.info("DEBUG_VOX: Setting parameter with a wrong MODE")
                # VOX total threshold
                elif sendCmdType == 6:
                    # Mode 2
                    if voxMode == '2':
                        # Check param length - Valid value length are 1, 2 or 3 - Default value are 267
                        # Experimental configuration range - 70 to 999
                        lengthStr = len(thresholdvalue)
                        if lengthStr == 1:
                            dataToSend = '00' + thresholdvalue
                        elif lengthStr == 2:
                            dataToSend = '0' + thresholdvalue
                        elif lengthStr == 3:
                            dataToSend = thresholdvalue
                        # Valid length are 1, 2 or 3
                        if lengthStr == 1 or lengthStr == 2 or lengthStr == 3:
                            try:
                                command = '<0202' + dataToSend + '>'
                                retryDatToSend = command
                                
                                # Send command to VOX controller
                                voxSerComm.write(command.encode())
                                commBusy = True
                                cmdSent = True

                                logger.info("DEBUG_VOX: SEND CMD: %s" % (command))
                            except:
                                commBusy = True
                                cmdSent = True
                                
                                logger.info("DEBUG_VOX: ERROR during sending command!")
                        # Invalid length
                        else:
                            sendCmdType = 0
                            logger.info("DEBUG_VOX: Invalid data length for Mode 2 and data type [02]!")    
                    else:
                        # Update VOX configuration data to previous value
                        revertVOXdata(sendCmdType)
                        
                        sendCmdType = 0
                        logger.info("DEBUG_VOX: Setting parameter with a wrong MODE")
                # VOX controller current mode
                elif sendCmdType == 7:
                    # Check param length - Valid value length are 1 - Default value are 2
                    lengthStr = len(voxMode)
                    if lengthStr == 1:
                        modeToSend = '0' + voxMode
                        # Mode 1
                        if modeToSend == '01':
                            lengthStr = len(delayaindiv)
                            # Valid length
                            if lengthStr == 1:
                                datToSend = '0' + delayaindiv
                                try:
                                    command = '<' + modeToSend + '01' + datToSend + '>'
                                    retryDatToSend = command
                                    
                                    # Send command to VOX controller
                                    voxSerComm.write(command.encode())
                                    commBusy = True
                                    cmdSent = True

                                    logger.info("DEBUG_VOX: SEND CMD: %s" % (command))
                                except:
                                    commBusy = True
                                    cmdSent = True
                                
                                    logger.info("DEBUG_VOX: ERROR during sending command!")
                            else:
                                sendCmdType = 0
                                logger.info("DEBUG_VOX: Invalid data length for Mode 1 and data type [01]!")    
                        # Mode 2
                        elif modeToSend == '02':
                            # Check param length - Valid value length are 1, 2 or 3 - Default value are 95
                            # Experimental configuration range - 2 to 999
                            lengthStr = len(delayvalue)
                            if lengthStr == 1:
                                datToSend = '00' + delayvalue
                            elif lengthStr == 2:
                                datToSend = '0' + delayvalue
                            elif lengthStr == 3:
                                datToSend = delayvalue
                            # Valid length are 1, 2 or 3
                            if lengthStr == 1 or lengthStr == 2 or lengthStr == 3:
                                try:
                                    command = '<' + modeToSend + '01' + datToSend + '>'
                                    retryDatToSend = command
                                    
                                    # Send command to VOX controller
                                    voxSerComm.write(command.encode())
                                    commBusy = True
                                    cmdSent = True

                                    logger.info("DEBUG_VOX: SEND CMD: %s" % (command))
                                except:
                                    commBusy = True
                                    cmdSent = True
                                
                                    logger.info("DEBUG_VOX: ERROR during sending command!")
                            # Invalid length
                            else:
                                sendCmdType = 0
                                logger.info("DEBUG_VOX: Invalid data length for Mode 2 and data type [01]!")
                    # Invalid length
                    else:
                        sendCmdType = 0
                        logger.info("DEBUG_VOX: Invalid data length for VOX Mode!")
                                    
# Thread for RESTFul API web server
def restful_web_server (threadname):
    logger.info("DEBUG_REST_API: RestFul API web server STARTED")
    if __name__ == "__main__":
        # RUN RestFul API web server
        # Add a certificate to make sure REST web API can support HTTPS request
        # Generate first cert.pem (new certificate) and key.pem (new key) by initiate below command:
        # openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
        # Secure web server (HTTPS) - Default port 5000
        if macSecInSec == True:
            #app.run(host='0.0.0.0', ssl_context=('cert.pem', 'key.pem'))
            #app.run(host='0.0.0.0', ssl_context=('asterisk.pem', 'ca.key'))
            app.run(host='0.0.0.0', port=5000, ssl_context=('asterisk.pem', 'ca.key'))
        # Insecure web server (HTTP) - Default port 5000
        else:
            app.run(host='0.0.0.0')

# Thread for monitor daemon activities
def monitor_this_daemon(threadname, delay):
    global wdog
    global pttIsON
    global pttRx    
    global pttTOcnt
    global pttCnt
    global pttTimeOut
    global pttModeOper
    global dtmfRx
    global dtmfSmplCnt
    global ledBlnkCnt
    global ledEn
    global DTMFMETHOD
    global icomEnaDis
    global joinIcomCnt
    global strtJoinIcom
    global strtTmrJoin
    
    while True:
        time.sleep(delay)

        # ON ALIVE led
        if wdog == False:
            if ledEn == False:
                #GPIO.output(17, GPIO.HIGH)
                GPIO.output(6, GPIO.HIGH)
                ledEn = True
            wdog = True
        # OFF ALIVE led
        else:
            if ledEn == False:
                #GPIO.output(17, GPIO.LOW)
                GPIO.output(6, GPIO.LOW)

            pttTOcnt += 1    # Increment time out counter
            dtmfSmplCnt += 1 # Increment DTMF character '#' sampling counter
            wdog = False

        # PTT DTMF checking only valid in none intercom mode
        if icomEnaDis == False:
            # New DTMF method
            if DTMFMETHOD == True:
                # Every 2 seconds check DTMF character '#' for PTT signal
                if dtmfSmplCnt == 2:
                    # Previously received DTMF character '#' for PTT signal
                    # Start process a PTT operation
                    if dtmfRx == True:
                        # ON PTT
                        if pttRx == False:
                            logger.info("DEBUG_DTMF_PTT: Receive PTT signal, ON PTT")
                            
                            # Checking PTT mode of operation
                            # Mode 1
                            if pttModeOper == 1:
                                # Activate GPIO for PTT mode MANUAL
                                GPIO.output(12, GPIO.HIGH)
                                # Activate GPIO for PTT control
                                GPIO.output(4, GPIO.HIGH)
                            # Mode 3
                            elif pttModeOper == 3:
                                # Activate GPIO for PTT control
                                GPIO.output(4, GPIO.HIGH)
                            
                            dtmfRx = False
                            pttRx = True
                            pttTOcnt = 0

                            # Update RIC daemon status REST API data
                            ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                            ric[0]['pttstatus'] = 'ON'
                        # OFF PTT
                        elif pttRx == True:
                            logger.info("DEBUG_DTMF_PTT: Receive PTT signal, OFF PTT")
                            
                            # Checking PTT mode of operation
                            # Mode 1
                            if pttModeOper == 1:
                                # Deactivate GPIO for PTT control
                                GPIO.output(4, GPIO.LOW)
                                # Deactivate GPIO for PTT mode MANUAL
                                GPIO.output(12, GPIO.LOW)
                            # Mode 3
                            elif pttModeOper == 3:
                                # Deactivate GPIO for PTT control
                                GPIO.output(4, GPIO.LOW)
                            
                            dtmfRx = False
                            pttRx = False
                            pttTOcnt = 0

                            # Update RIC daemon status REST API data
                        ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                        ric[0]['pttstatus'] = 'OFF'
                    dtmfSmplCnt = 0

        # Intercom group delay reconnection by 10s
        else:
            # Start a delay before intercom reconnection process are initiated
            if strtTmrJoin == True:
                if joinIcomCnt < 20:
                    joinIcomCnt += 1

                # Initiate intercom reconnection process after 10s
                elif joinIcomCnt == 20:
                    strtJoinIcom = True

                    strtTmrJoin = False
                    joinIcomCnt = 0

                    logger.info("DEBUG_INTERCOM: Prepare to joining intercom group....")

        # Blink LED every half of PTT time out setting
        # Initialize LED blink counter
        if ledBlnkCnt == 0:
            ledBlnkCnt = pttTimeOut / 2
        # Check PTT time out counter against LED blink counter setting
        else:
            # Enable the LED Blink
            if pttTOcnt == ledBlnkCnt:
                ledEn = False
        
        # Create time out for PTT signal, if caller are NOT deactivate it
        # After 1 minute check PTT, if its still ON, then OFF it
        # if pttTOcnt == 60:
        if pttTOcnt == pttTimeOut:
            # ON LED again after PTT time out counter reaches the count setting
            GPIO.output(6, GPIO.LOW)
            # Enable back the LED blink
            ledEn = False
            
            # Check for PTT mode
            # Hybrid PTT mode:
            # Mode 1:
            # When there is no PTT signal, PTT are in VOX mode
            # When there is a PTT signal, PTT are in MANUAL mode

            # Mode 2:
            # Always in VOX PTT activation
            
            # Mode 3:
            # Always in MANUAL PTT activation

            # Intercom mode:
            # Always in intercom mode, and all functionalities related to RoIP
            # will be disable, the current setting status will remain as
            # previous except the intercom features will enable

            # PTT time out checking only valid in none intercom mode
            if icomEnaDis == False:
                # Manual PTT are available only in Mode 1 and 3
                if pttModeOper == 1 or pttModeOper == 3:
                    # Previously PTT is still ON after 10 seconds time out elapsed 
                    if pttRx == True or pttIsON == True:
                        # Previous PTT are using DTMF '#' - From IP phone
                        if pttRx == True:
                            logger.info("DEBUG_DTMF_PTT: Time OUT! PTT still ON, OFF PTT")

                            pttCnt = 0
                            pttRx = False
                        # Previous PTT are using SIP message - From Tactical SIP application
                        elif pttIsON == True:
                            logger.info("DEBUG_SIP_PTT: Time OUT! PTT still ON, OFF PTT")

                            pttIsON = False
                        # Mode 1
                        if pttModeOper == 1:
                            # Deactivate GPIO for PTT control
                            GPIO.output(4, GPIO.LOW)
                            # Deactivate GPIO for PTT mode MANUAL
                            GPIO.output(12, GPIO.LOW)
                        # Mode 3
                        elif pttModeOper == 3:
                            # Deactivate GPIO for PTT control
                            GPIO.output(4, GPIO.LOW)
                        # Update RIC daemon status REST API data
                        ric = [ ricC for ricC in daemonStat if (ricC['id'] == '000') ]
                        ric[0]['pttstatus'] = 'OFF'
                else:
                    logger.info("DEBUG_TOUT_PTT: PTT are in VOX mode (Mode 2)")    

            pttTOcnt = 0
            # Print time out counter
            logger.info("DEBUG_TOUT_PTT: SEC BEFORE T.O: %s, SET: %s" % (pttTOcnt, pttTimeOut))
        else:
            # Print time out counter
            logger.info("DEBUG_TOUT_PTT: SEC BEFORE T.O: %s, SET: %s" % (pttTOcnt, pttTimeOut))            
                
def main():
    #hfradio = HFRadioSIPclient(username='1002', password='1234', snd_capture='ALSA: audioinjector-octo-soundcard')
    #hfradio = HFRadioSIPclient(username='1002', password='1234', snd_capture='ALSA: default device')
    
    global sipUserName
    global sipPswd

    # Create thread for monitor a daemon activities
    try:
        thread.start_new_thread(monitor_this_daemon, ("[monitor_this_daemon]", 0.5 ))
    except:
        logger.info("Error: Unable to start [monitor_this_daemon] thread")

    # Create thread for RestFul API web server
    try:
        thread.start_new_thread(restful_web_server, ("[restful_web_server]", ))
    except:
        logger.info("Error: Unable to start [restful_web_server] thread")

    # Create thread for serial communication with VOX controller 
    try:
        thread.start_new_thread(serial_vox_comm, ("[serial_vox_comm]", 0.5 ))
    except:
        logger.info("Error: Unable to start [serial_vox_comm] thread")    
        
    #hfradio = HFRadioSIPclient(username=sipUserName, password=sipPswd, snd_capture='ALSA: USB PnP Sound Device')
    hfradio = radioSIPclient(username=sipUserName, password=sipPswd, snd_capture='audioinjector-pi-soundcard')
    hfradio.run()

    logger.info("THREAD:")
    
    sys.exit()
    
main()
