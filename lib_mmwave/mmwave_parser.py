# ----- Imports -------------------------------------------------------

# Standard Imports
import struct
import serial
import time
import numpy as np
import math
import datetime

# Local Imports
from .parseFrame import *
 
class cfgParser:
    def __init__(self):
        self.profile = {}
        self.chirpComnCfg = {}
        self.chirpTimingCfg = {}
        pass

    
    def parse_cfg(self, cfg_fname):
        '''
        1. Read the config file
        2. Generate a dictionary of cfg values (stored here)
        3. return the config
        '''
        with open(cfg_fname, 'r') as cfg_file:
            self.cfg = cfg_file.readlines()
        
        self.gen_cfg_dict()

        return self.cfg
    

    def gen_cfg_dict(self):
        counter = 0
        chirpCount = 0
        for line in self.cfg:
            args = line.split()
            if len(args) > 0:
                if args[0] == 'trackingCfg':
                    if len(args) < 5:
                        print ("Error: trackingCfg had fewer arguments than expected")
                        continue
                    self.profile['maxTracks'] = int(args[4])

                elif args[0] == 'profileCfg':
                    if len(args) < 12:
                        print ("Error: profileCfg had fewer arguments than expected")
                        continue
                    self.profile['startFreq'] = float(args[2])
                    self.profile['idle'] = float(args[3])
                    self.profile['adcStart'] = float(args[4])
                    self.profile['rampEnd'] = float(args[5])
                    self.profile['slope'] = float(args[8])
                    self.profile['samples'] = float(args[10])
                    self.profile['sampleRate'] = float(args[11])

                elif args[0] == 'frameCfg':
                    if len(args) < 4:
                        print ("Error: frameCfg had fewer arguments than expected")
                        continue
                    self.frame_time = float(args[5]) # this is in ms
                    self.profile['numLoops'] = float(args[3])
                    self.profile['numTx'] = float(args[2])+1

                elif args[0] == 'chirpCfg':
                    chirpCount += 1

                elif args[0] == 'chirpComnCfg':
                    if len(args) < 8:
                        print ("Error: chirpComnCfg had fewer arguments than expected")
                        continue
                    try:
                        self.chirpComnCfg['DigOutputSampRate'] = int(args[1])
                        self.chirpComnCfg['DigOutputBitsSel'] = int(args[2])
                        self.chirpComnCfg['DfeFirSel'] = int(args[3])
                        self.chirpComnCfg['NumOfAdcSamples'] = int(args[4])
                        self.chirpComnCfg['ChirpTxMimoPatSel'] = int(args[5])
                        self.chirpComnCfg['ChirpRampEndTime'] = 10 * float(args[6])
                        self.chirpComnCfg['ChirpRxHpfSel'] = int(args[7])
                    except Exception as e:
                        print (e)

                elif args[0] == 'chirpTimingCfg':
                    if len(args) < 6:
                        print ("Error: chirpTimingCfg had fewer arguments than expected")
                        continue
                    self.chirpTimingCfg['ChirpIdleTime'] = 10.0 * float(args[1])
                    self.chirpTimingCfg['ChirpAdcSkipSamples'] = int(args[2]) << 10
                    self.chirpTimingCfg['ChirpTxStartTime'] = 10.0 * float(args[3])
                    self.chirpTimingCfg['ChirpRfFreqSlope'] = float(args[4])
                    self.chirpTimingCfg['ChirpRfFreqStart'] = float(args[5])
                else:
                    # print(f"Ignoring {args[0]}")
                    pass


#Initialize this Class to create a UART Parser. Initialization takes one argument:
# 1: String Lab_Type - These can be:
#   a. 3D People Tracking
#   b. SDK Out of Box Demo
#   c. Long Range People Detection
#   d. Indoor False Detection Mitigation
#   e. (Legacy): Overhead People Counting
#   f. (Legacy) 2D People Counting
# Default is (f). Once initialize, call connectComPorts(self, cliComPort, DataComPort) to connect to device com ports.
# Then call readAndParseUart() to read one frame of data from the device. The gui this is packaged with calls this every frame period.
# readAndParseUart() will return all radar detection and tracking information.
class uartParser():
    def __init__(self,type='SDK Out of Box Demo'):
        # Set this option to 1 to save UART output from the radar device
        self.saveBinary = 0
        self.replay = 0
        self.binData = bytearray(0)
        self.uartCounter = 0
        self.framesPerFile = 100
        self.first_file = True
        self.filepath = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")
            
        if (type == DEMO_NAME_OOB):
            self.parserType = "DoubleCOMPort"
        elif (type == DEMO_NAME_LRPD):
            self.parserType = "DoubleCOMPort"
        elif (type == DEMO_NAME_3DPC):
            self.parserType = "DoubleCOMPort"
        elif (type == DEMO_NAME_SOD):
            self.parserType = "DoubleCOMPort"
        elif (type == DEMO_NAME_VITALS):
            self.parserType = "DoubleCOMPort"
        elif (type == DEMO_NAME_MT):
            self.parserType = "DoubleCOMPort"
        elif (type == DEMO_NAME_GESTURE):
            self.parserType = "DoubleCOMPort"
        elif (type == DEMO_NAME_x432_OOB):
            self.parserType = "SingleCOMPort"
        elif (type == DEMO_NAME_x432_GESTURE):
            self.parserType = "SingleCOMPort"
        # TODO Implement these
        elif (type == "Replay"):
            self.replay = 1
        else: 
            print ("ERROR, unsupported demo type selected!")
        
        # Data storage
        self.now_time = datetime.datetime.now().strftime('%Y%m%d-%H%M')
    

    def WriteFile(self, data, dir_capture="data"):
        filepath=os.path.join(dir_capture, self.now_time + '.bin')
        objStruct = '6144B'
        objSize = struct.calcsize(objStruct)
        binfile = open(filepath, 'ab+') #open binary file for append
        binfile.write(bytes(data))
        binfile.close()

    def setSaveBinary(self, saveBinary):
        self.saveBinary = saveBinary
        print(self.saveBinary)

    # This function is always called - first read the UART, then call a function to parse the specific demo output
    # This will return 1 frame of data. This must be called for each frame of data that is expected. It will return a dict containing all output info
    # Point Cloud and Target structure are liable to change based on the lab. Output is always cartesian.
    # DoubleCOMPort means this function refers to the xWRx843 family of devices.
    def readAndParseUartDoubleCOMPort(self):
        frameData = self.readUartDoubleCOMPort()
        if(self.saveBinary == 1):
            self.saveBinaryData(frameData)
        outputDict = parseStandardFrame(frameData)
        return outputDict

    def readUartDoubleCOMPort(self):
        self.fail = 0
        if (self.replay):
            return self.replayHist()
    
        # Find magic word, and therefore the start of the frame
        index = 0
        magicByte = self.dataCom.read(1)
        frameData = bytearray(b'')
        while (1):
            # If the device doesnt transmit any data, the COMPort read function will eventually timeout
            # Which means magicByte will hold no data, and the call to magicByte[0] will produce an error
            # This check ensures we can give a meaningful error
            if (len(magicByte) < 1):
                error_msg = """ERROR: No data detected on COM Port, read timed out.
                \tBe sure that the device is in the proper mode, and that the cfg you are sending is valid.
                \tTry resting the device with the NRST button.
                \tSee https://dev.ti.com/tirex/explore/content/radar_toolbox_1_20_00_11/docs/hardware_guides/evm_setup_operational_modes.html#isk-style-standalone-mode for help")
                """
                magicByte = self.dataCom.read(1)
                raise BrokenPipeError(error_msg)
                
            # Found matching byte
            elif (magicByte[0] == UART_MAGIC_WORD[index]):
                index += 1
                frameData.append(magicByte[0])
                if (index == 8): # Found the full magic word
                    break
                magicByte = self.dataCom.read(1)
                
            else:
                # When you fail, you need to compare your byte against that byte (ie the 4th) AS WELL AS compare it to the first byte of sequence
                # Therefore, we should only read a new byte if we are sure the current byte does not match the 1st byte of the magic word sequence
                if (index == 0): 
                    magicByte = self.dataCom.read(1)
                index = 0 # Reset index
                frameData = bytearray(b'') # Reset current frame data
        
        # Read in version from the header
        versionBytes = self.dataCom.read(4)
        
        frameData += bytearray(versionBytes)

        # Read in length from header
        lengthBytes = self.dataCom.read(4)
        frameData += bytearray(lengthBytes)
        frameLength = int.from_bytes(lengthBytes, byteorder='little')
        
        # Subtract bytes that have already been read, IE magic word, version, and length
        # This ensures that we only read the part of the frame in that we are lacking
        frameLength -= 16 

        # Read in rest of the frame
        frameData += bytearray(self.dataCom.read(frameLength))

        return frameData

    def saveBinaryData(self, frameData):
        # If save binary is enabled
        self.binData += frameData
        # Save data every framesPerFile frames
        self.uartCounter += 1
        if (self.uartCounter % self.framesPerFile == 0):
            # First file requires the path to be set up
            if(self.first_file is True): 
                if(os.path.exists('binData/') == False):
                    # Note that this will create the folder in the caller's path, not necessarily in the Industrial Viz Folder                        
                    os.mkdir('binData/')
                os.mkdir('binData/'+self.filepath)
                self.first_file = False
            toSave = bytes(self.binData)
            fileName = 'binData/' + self.filepath + '/pHistBytes_' + str(math.floor(self.uartCounter/self.framesPerFile)) + '.bin'
            bfile = open(fileName, 'wb')
            bfile.write(toSave)
            bfile.close()
            # Reset binData and missed frames
            self.binData = []
    
    @staticmethod
    def save_one_frame(frame, filename):
        bfile = open(filename, 'wb')
        bfile.write(bytes(frame))
        bfile.close()

    # This function is identical to the readAndParseUartDoubleCOMPort function, but it's modified to work for SingleCOMPort devices in the xWRLx432 family
    def readAndParseUartSingleCOMPort(self):
        # Reopen CLI port
        if(self.cliCom.isOpen() == False):
            print("Reopening Port")
            self.cliCom.open()

        self.fail = 0
        if (self.replay):
            return self.replayHist()
    
        # Find magic word, and therefore the start of the frame
        index = 0
        magicByte = self.cliCom.read(1)
        frameData = bytearray(b'')
        while (1):
            # If the device doesnt transmit any data, the COMPort read function will eventually timeout
            # Which means magicByte will hold no data, and the call to magicByte[0] will produce an error
            # This check ensures we can give a meaningful error
            if (len(magicByte) < 1):
                print ("ERROR: No data detected on COM Port, read timed out")
                print("\tBe sure that the device is in the proper mode, and that the cfg you are sending is valid")
                magicByte = self.cliCom.read(1)

            # Found matching byte
            elif (magicByte[0] == UART_MAGIC_WORD[index]):
                index += 1
                frameData.append(magicByte[0])
                if (index == 8): # Found the full magic word
                    break
                magicByte = self.cliCom.read(1)
                
            else:
                # When you fail, you need to compare your byte against that byte (ie the 4th) AS WELL AS compare it to the first byte of sequence
                # Therefore, we should only read a new byte if we are sure the current byte does not match the 1st byte of the magic word sequence
                if (index == 0):
                    magicByte = self.cliCom.read(1)
                index = 0 # Reset index
                frameData = bytearray(b'') # Reset current frame data
        
        # Read in version from the header
        versionBytes = self.cliCom.read(4)
        
        frameData += bytearray(versionBytes)

        # Read in length from header
        lengthBytes = self.cliCom.read(4)
        frameData += bytearray(lengthBytes)
        frameLength = int.from_bytes(lengthBytes, byteorder='little')
        
        # Subtract bytes that have already been read, IE magic word, version, and length
        # This ensures that we only read the part of the frame in that we are lacking
        frameLength -= 16 

        # Read in rest of the frame
        frameData += bytearray(self.cliCom.read(frameLength))

        # If save binary is enabled
        if(self.saveBinary == 1):
            self.binData += frameData
            # Save data every framesPerFile frames
            self.uartCounter += 1
            if (self.uartCounter % self.framesPerFile == 0):
                # First file requires the path to be set up
                if(self.first_file is True): 
                    if(os.path.exists('binData/') == False):
                        # Note that this will create the folder in the caller's path, not necessarily in the Industrial Viz Folder                        
                        os.mkdir('binData/')
                    os.mkdir('binData/'+self.filepath)
                    self.first_file = False
                toSave = bytes(self.binData)
                fileName = 'binData/'+self.filepath+'/pHistBytes_'+str(math.floor(self.uartCounter/self.framesPerFile))+'.bin'
                bfile = open(fileName, 'wb')
                bfile.write(toSave)
                bfile.close()
                # Reset binData and missed frames
                self.binData = []
 
        # frameData now contains an entire frame, send it to parser
        if (self.parserType == "SingleCOMPort"):
            outputDict = parseStandardFrame(frameData)
        else:
            print ('FAILURE: Bad parserType')
        
        return outputDict


    # Find various utility functions here for connecting to COM Ports, send data, etc...
    # Connect to com ports
    # Call this function to connect to the comport. This takes arguments self (intrinsic), cliCom, and dataCom. No return, but sets internal variables in the parser object.
    def connectComPorts(self, cliCom, dataCom):
        self.cliCom = serial.Serial(cliCom, 115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0.6)
        self.dataCom = serial.Serial(dataCom, 921600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=0.6)
        self.dataCom.reset_output_buffer()
        print('Connected')
    
    def disconnectComPorts(self):
        self.cliCom.close()
        self.dataCom.close()
    
    # Separate connectComPort (not PortS) for IWRL6432 because it only uses one port
    def connectComPort(self, cliCom, cliBaud=115200):
        # Longer timeout time for IWRL6432 to support applications with low power / low update rate
        self.cliCom = serial.Serial(cliCom, cliBaud, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=4)
        self.cliCom.reset_output_buffer()
        print('Connected (one port)')

    #send cfg over uart
    def sendCfg(self, cfg):
        # Ensure each line ends in \n for proper parsing
        for i, line in enumerate(cfg):
            # Remove empty lines from cfg
            if(line == '\n'):
                cfg.remove(line)
            # add a newline to the end of every line (protects against last line not having a newline at the end of it)
            elif(line[-1] != '\n'):
                cfg[i] = cfg[i] + '\n'

        for line in cfg:
            time.sleep(.03) # Line delay

            if(self.cliCom.baudrate == 1250000):
                for char in [*line]:
                    time.sleep(.001) # Character delay. Required for demos which are 1250000 baud by default else characters are skipped
                    self.cliCom.write(char.encode())
            else:
                self.cliCom.write(line.encode())
                
            ack = self.cliCom.readline()
            # print(ack)
            ack = self.cliCom.readline()
            # print(ack)
            splitLine = line.split()
            if(splitLine[0] == "baudRate"): # The baudrate CLI line changes the CLI baud rate on the next cfg line to enable greater data streaming off the IWRL device.
                try:
                    self.cliCom.baudrate = int(splitLine[1])
                except:
                    print("Error - Invalid baud rate")
                    sys.exit(1)
        # Give a short amount of time for the buffer to clear
        time.sleep(0.03)
        self.cliCom.reset_input_buffer()
        # NOTE - Do NOT close the CLI port because 6432 will use it after configuration


    #send single command to device over UART Com.
    def sendLine(self, line):
        self.cliCom.write(line.encode())
        ack = self.cliCom.readline()
        print(ack)
        ack = self.cliCom.readline()
        print(ack)

    # def replayHist(self):
    #     if (self.replayData):
    #         #print('reading data')
    #         #print('fail: ',self.fail)
    #         #print(len(self.replayData))
    #         #print(self.replayData[0:8])
    #         self.replayData = self.Capon3DHeader(self.replayData)
    #         #print('fail: ',self.fail)
    #         return self.pcBufPing, self.targetBufPing, self.indexes, self.numDetectedObj, self.numDetectedTarget, self.frameNum, self.fail, self.classifierOutput
    #         #frameData = self.replayData[0]
    #         #self.replayData = self.replayData[1:]
    #         #return frameData['PointCloud'], frameData['Targets'], frameData['Indexes'], frameData['Number Points'], frameData['NumberTracks'],frameData['frame'],0, frameData['ClassifierOutput'], frameData['Uniqueness']
    #     else:
    #         filename = 'overheadDebug/binData/pHistBytes_'+str(self.saveNum)+'.bin'
    #         #filename = 'Replay1Person10mShort/pHistRT'+str(self.saveNum)+'.pkl'
    #         self.saveNum+=1
    #         try:
    #             dfile = open(filename, 'rb', 0)
    #         except:
    #             print('cant open ', filename)
    #             return -1
    #         self.replayData = bytes(list(dfile.read()))
    #         if (self.replayData):
    #             print('entering replay')
    #             return self.replayHist()
    #         else:
    #             return -1
        
def getBit(byte, bitNum):
    mask = 1 << bitNum
    if (byte&mask):
        return 1
    else:
        return 0