from platform import machine
import threading
import datetime, time
import socket
import csv
from logging import debug
from pycomm3 import LogixDriver
from pycomm3.cip.data_types import DINT, UINT
import json
import os
from multiprocessing import Process
import keyboard
import glob

'''
Confirmed Elwema test. Automatically cycles based on PLC reads

Cleaned up code to make more readable
'''


### GLOBALS ########################################################
trigger_count = 0
slow_count = 0
longest_time = 0

current_stage_14 = 0
current_stage_15 = 0

#lock = threading.Lock()

# Testing
start_timer = datetime.datetime.now()
start_timer_END = datetime.datetime.now()

kill_threads = False # global boolean to stop both threads on error

endProgram_latch_14 = False
abort_latch_14 = False
reset_latch_14 = False

config_info = {}

# global variable declarations, some are probably unnecessary(?)
arrayOutTags = [
    'LoadProgram',
    'StartProgram',
    'EndProgram',
    'AbortProgram',
    'Reset',
    'PartType',
    'PartProgram',
    'ScanNumber',
    'PUN{64}',
    'GMPartNumber{8}',
    'Module',
    'PlantCode',
    'Month',
    'Day',
    'Year',
    'Hour',
    'Minute',
    'Second',
    'QualityCheckOP110',
    'QualityCheckOP120',
    'QualityCheckOP130',
    'QualityCheckOP140',
    'QualityCheckOP150',
    'QualityCheckOP310',
    'QualityCheckOP320',
    'QualityCheckOP330',
    'QualityCheckOP340',
    'QualityCheckOP360',
    'QualityCheckOP370',
    'QualityCheckOP380',
    'QualityCheckOP390',
    'QualityCheckScoutPartTracking',
    'Heartbeat'
    #'KeyenceFltCode',
    #'PhoenixFltCode'
    ];

tagKeys = []
for tag in arrayOutTags:
    tagKeys.append(tag.split("{")[0]) # delete trailiing { if it exists

tagCmds = [
    'LoadProgram',
    'EndProgram',
    'StartProgram',
    'AbortProgram',
    'Reset'];

tagDateTime = [
    'Month',
    'Day',
    'Year',
    'Hour',
    'Minute',
    'Second'];

tagStringInt = [
    'PUN',
    'GMPartNumber'];

tagInt = [
    'PartType',
    'PartProgram',
    'ScanNumber',
    #'KeyenceFltCode',
    #'PhoenixFltCode'
    ];

tagChar = [
    'Module',
    'PlantCode',
    'QualityCheckOP110',
    'QualityCheckOP120',
    'QualityCheckOP130',
    'QualityCheckOP140',
    'QualityCheckOP150',
    'QualityCheckOP310',
    'QualityCheckOP320',
    'QualityCheckOP330',
    'QualityCheckOP340',
    'QualityCheckOP360',
    'QualityCheckOP370',
    'QualityCheckOP380',
    'QualityCheckOP390',
    'QualityCheckScoutPartTracking'
        ];
# END GLOBALS ####################################################

#reads config file into dict
def read_config():

    #reading config.txt file
    with open('D:\\python_testing\\config\\config.txt') as config_file:
        config_data = config_file.read()
        #print(config_data)
        #print(config_data[0][0])
        config_vars = json.loads(config_data)
        #print(type(config_vars))

        return config_vars
#END

#single-shot read of all 'arrayOutTags' off PLC
def read_plc_dict(plc, machine_num):
    readList = []
    for tag in arrayOutTags :
        newTag = 'Program:HM1450_VS' + machine_num + '.VPC1.O.' + tag;
        readList.append(newTag)
        
    resultsList = plc.read(*readList) # splat-read: tag, value, type, error
    readDict = {}
    #print(resultsList)

    #generating list of tag names, ONLY end of the full tag name
    for tag in resultsList:
        key = tag.tag.split(".")[-1]
        readDict[key] = tag

    #print(readDict)
    return readDict
#END read_plc_dict

#Writing back to PLC to mirror data on LOAD
def write_plc(plc, machine_num, results):

    #logging how long the 'read' takes
    #start_time = datetime.datetime.now()

    #one-shot PLC write (to mirror data back)
    plc.write(('Program:HM1450_VS' + machine_num + '.VPC1.I.PartType', results['PartType'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PartProgram', results['PartProgram'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.ScanNumber', results['ScanNumber'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PUN{64}', results['PUN'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.GMPartNumber{8}', results['GMPartNumber'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Module', results['Module'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PlantCode', results['PlantCode'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Month', results['Month'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Day', results['Day'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Year', results['Year'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Hour', results['Hour'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Minute', results['Minute'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Second', results['Second'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP110', results['QualityCheckOP110'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP120', results['QualityCheckOP120'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP130', results['QualityCheckOP130'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP140', results['QualityCheckOP140'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP150', results['QualityCheckOP150'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP310', results['QualityCheckOP310'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP320', results['QualityCheckOP320'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP330', results['QualityCheckOP330'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP340', results['QualityCheckOP340'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP360', results['QualityCheckOP360'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP370', results['QualityCheckOP370'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP380', results['QualityCheckOP380'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP390', results['QualityCheckOP390'][1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckScoutPartTracking', results['QualityCheckScoutPartTracking'][1])
    )

    #end_time = datetime.datetime.now()
    #time_diff = (end_time - start_time)
    #execution_time = time_diff.total_seconds() * 1000
    #print('\'plc.write()\' took %d ms to run\n' % (execution_time))
    #print("Finished writing PLC...")
#END write_plc

# Flushes PLC data mirroring tags (to 0)
def write_plc_flush(plc, machine_num):

    #generic fillers for PUN and GMPartNumber (special cases) since they are arrays instead of single values
    plc_writer_PUN = [72, 101, 108, 108, 111, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35]
    plc_writer_GMPartNumber = [35, 35, 35, 35, 35, 35, 35, 35]

    #clearing our PLC tags so they will NOT match .O equivalents
    plc.write(('Program:HM1450_VS' + machine_num + '.VPC1.I.PartType', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PartProgram', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.ScanNumber', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PUN{64}', plc_writer_PUN),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.GMPartNumber{8}', plc_writer_GMPartNumber),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Module', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PlantCode', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Month', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Day', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Year', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Hour', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Minute', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Second', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP110', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP120', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP130', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP140', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP150', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP310', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP320', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP330', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP340', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP360', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP370', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP380', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP390', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckScoutPartTracking', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Defect_Number', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Defect_Size', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.DefectZone', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Pass', 0),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Fail', 0)
    )
# end write_plc_flush


### Data-Type Functions
#used to verify values when writing back to PLC, 
def protected_ord(value):
    if len(value) > 1:
        print("WRONG Below: ")
        print(value)
        print()
        value = value[0]
    #print(f'Returning: {value}')
    return ord(value)
#END protected_ord

#function to translate PLC int-arrays into ASCII str for OPC
def intArray_to_str(intArray):
    strReturn = ""
    #print(intArray)

    #reads each 'int' from array then appends to 'str' array in char form (per element)
    for i in range(len(intArray)):
        strReturn += chr(intArray[i])

    #print(strReturn)
    return strReturn
#END intArray_to_str

#function to translate PLC int-arrays into ASCII str-arrays for OPC, deprecated with OPC removal
def intArray_to_strArray(intArray):
    #declaring an array of 'str' to hold return value
    strArray = []
    #print(intArray)

    #reads each 'int' from array then appends to 'str' array in char form (per element)
    for i in range(len(intArray)):
        strArray.append(chr(intArray[i]))

    #print(strArray)
    return strArray
#END intArray_to_strArray

# Triggering Keyence (to start a scan)
def TriggerKeyence(sock, machine_num, item):

    global trigger_count
    global slow_count
    global longest_time
    global start_timer_END

    message = 'MR,%Busy\r\n' #initial read of '%Busy' to ensure scan is actually taking place (%Busy == 1)
    sock.sendall(message.encode())
    data = sock.recv(32)
    #print(f'({machine_num}) %Busy = {data}')

    first_busy_pull_start = datetime.datetime.now()
    # looping until '%Busy' == 0
    while(data != b'MR,+0000000000.000000\r'):
        #print(f'Keyence(Busy) was not high, \'T1\' not sent!')
        # utilizing 'with' to use thread lock
        #message = 'T1\r\n'
        message = 'MR,%Busy\r\n'
        #message = 'MR,%Cam1Ready\r\n'
        #with lock:
        sock.sendall(message.encode())
        data = sock.recv(32)
        print(f'({machine_num}) (Pre-Trigger) TriggerKeyence: received "%s"' % data)
        #print('Scanning...')
        time.sleep(.2) # artificial 1ms pause between Keyence reads
    first_busy_pull_stop = datetime.datetime.now()
    time_diff = (first_busy_pull_stop - first_busy_pull_start)
    execution_time = time_diff.total_seconds() * 1000
    if(int(execution_time) > 100):
        print(f'\n({machine_num}) TriggerKeyence (First Busy Pull) SLOW (over 100ms)! Took {execution_time} ms!!!\n')

    message = item # 'T1' in this case
    trigger_start_time = datetime.datetime.now() # marking when 'T1' is sent
    #with lock:
    sock.sendall(message.encode()) #*** sending 'T1', actual trigger command ***
    data = sock.recv(32)
    #print(f'({machine_num}) received "%s"\n' % data)
    #start_timer_END = datetime.datetime.now() # END test timer
    #time_diff = (start_timer_END - start_timer)
    #execution_time = time_diff.total_seconds() * 1000
    #print(f'PLC(Start) read to Keyence(T1) read in : {execution_time} ms')
    trigger_t1Only_end = datetime.datetime.now()
    time_diff = (trigger_t1Only_end - trigger_start_time)
    execution_time = time_diff.total_seconds() * 1000
    if(int(execution_time) > 50):
        print(f'({machine_num}) TriggerKeyence (Sending T1) SLOW (over 50ms)! Took {execution_time} ms!!!\n')
    
    message = 'MR,%Busy\r\n' #initial read of '%Busy' to ensure scan is actually taking place (%Busy == 1)
    sock.sendall(message.encode())
    data = sock.recv(32)
    #print(f'%Busy = {data}')
    
    final_busy_pull_start = datetime.datetime.now()
    # looping until '%Busy' == 0
    while(data != b'MR,+0000000001.000000\r'):
    #while(data != b'T1\r'):
        #message = 'T1\r\n'
        message = 'MR,%Busy\r\n'
        sock.sendall(message.encode())
        data = sock.recv(32)
        print(f'({machine_num}) (Post-Trigger) TriggerKeyence: received "%s"' % data)
        time.sleep(.2) # artificial 1ms pause between Keyence reads
    #print('Keyence %Busy verified!')
    trigger_end_time = datetime.datetime.now() # marking when '%Busy' is read off Keyence
    time_diff = (trigger_end_time - final_busy_pull_start)
    execution_time = time_diff.total_seconds() * 1000
    if(int(execution_time) > 100):
        print(f'({machine_num}) TriggerKeyence (Final Busy Pull) SLOW (over 100ms)! Took {execution_time} ms!!!\n')

    #time_diff = (trigger_end_time - trigger_start_time)
    #execution_time = time_diff.total_seconds() * 1000
    #print(f'\n({machine_num}) \'T1\' sent to \'%Busy\' verified in {execution_time} ms\n')
    
#END 'TriggerKeyence'

#sends specific Keyence Program (branch) info to pre-load/prepare Keyence for Trigger(T1), also loads naming variables for result files
def LoadKeyence(sock, item):
    #print('LOADING KEYENCE\n')
    message = item # keyence message
    sock.sendall(message.encode()) # sending branch info
    #print(f'\n\'{item}\' Sent!\n')
    data = sock.recv(32)
    #print('received "%s"\n' % data)

# sends 'TE,0' then 'TE,1' to the Keyence, resetting to original state (ready for new 'T1')
#interrupts active scans on 'EndScan' from PLC
def ExtKeyence(sock):
    #print('ExtKeyence!')
    message = 'TE,0\r\n' # setting 'TE,0' first
    sock.sendall(message.encode()) # sending TE,0
    data = sock.recv(32)
    #print('\n\'TE,0\' Sent!\n')

    message = 'TE,1\r\n' # setting 'TE,1' to reset
    sock.sendall(message.encode()) # sending, TE,1
    #print('\'TE,1\' Sent!\n')
    data = sock.recv(32)
    #print('received "%s"' % data)

    message = 'MR,%Busy\r\n' #read of '%Busy' to ensure scan has ended (should be 0)
    sock.sendall(message.encode())
    data = sock.recv(32)
    #print(f'%Busy = {data}')

    # looping until '%Busy' == 0
    while(data != b'MR,+0000000000.000000\r'):
        message = 'MR,%Busy\r\n'
        sock.sendall(message.encode())
        data = sock.recv(32)
        print(f'ExtKeyence: received "%s"' % data)
        #print('Scanning...')
        time.sleep(.2) # artificial 1ms pause between Keyence reads
# END 'ExtKeyence'

# reading PLC(EndScan) until it goes high to interrupt current Keyence scan
def monitor_endScan(plc, machine_num, sock):
    global kill_threads
    #print(f'({machine_num}) Listening for PLC(END_SCAN) high\n')

    #PLC read
    current = plc.read(
        ('Program:HM1450_VS' + machine_num + '.VPC1.O.EndScan'),
        ('Program:HM1450_VS' + machine_num + '.VPC1.O.Reset')
    )

    #listening for 'EndScan' OR 'Reset' to go high
    while((current[0][1] == False) and (current[1][1] == False)):
        if kill_threads == True:
            break
        #continuing tag check(s)
        current = plc.read(('Program:HM1450_VS' + machine_num + '.VPC1.O.EndScan'),
            ('Program:HM1450_VS' + machine_num + '.VPC1.O.Reset')
        )
        time.sleep(.005)

    #print(f'({machine_num}) PLC(END_SCAN) went high!\n')
    #ExtKeyence(sock) #function to interrupt Keyence
#END monitor_endScan

# function to monitor the Keyence tag 'KeyenceNotRunning', when True (+00001.00000) we know Keyence has completed result processing and FTP file write
def monitor_KeyenceNotRunning(sock, machine_num):
    #print(f'({machine_num}) Keyence Processing...')
    #msg = 'MR,#KeyenceNotRunning\r\n'
    msg = 'MR,#KeyenceNotRunning\r\n'
    sock.sendall(msg.encode())
    data = sock.recv(32)

    #until #KeyenceNotRunning from Keyence goes high, continuously check its value
    while(data != b'MR,+0000000001.000000\r'):
        sock.sendall(msg.encode())
        data = sock.recv(32)
        time.sleep(.005)
    #print(f'({machine_num}) Keyence Processing Complete!\n')
#END monitor_KeyenceNotRunning

# read defect information from the Keyence, then passes that as well as pass,fail,done to PLC, returns a list of result data for .txt file creation
def keyenceResults_to_PLC(sock, plc, machine_num):
    #read results from Keyence then pass to proper tags on PLC
    result_messages = ['MR,#ReportDefectCount\r\n', 'MR,#ReportLargestDefectSize\r\n', 'MR,#ReportLargestDefectZoneNumber\r\n', 'MR,#ReportPass\r\n', 'MR,#ReportFail\r\n']
    results = []

    # sending result messages to Keyence, then cleaning results to 'human-readable' list
    for msg in result_messages:
        sock.sendall(msg.encode())
        data = sock.recv(32)
        keyence_value_raw = str(data).split('.')
        keyence_value_raw = keyence_value_raw[0].split('+')
        keyence_value = int(keyence_value_raw[1])
        results.append(keyence_value)

    print(f'({machine_num}) Defect_Number: {results[0]}')
    print(f'({machine_num}) Defect_Size: {results[1]}')
    print(f'({machine_num}) Defect_Zone: {results[2]}')
    print(f'({machine_num}) Pass: {results[3]}')
    print(f'({machine_num}) Fail: {results[4]}')

    # writing normalized Keyence results to proper PLC tags
    plc.write(
        ('Program:HM1450_VS' + machine_num + '.VPC1.I.DefectNumber', results[0]),
        ('Program:HM1450_VS' + machine_num + '.VPC1.I.DefectSize', results[1]),
        ('Program:HM1450_VS' + machine_num + '.VPC1.I.DefectZone', results[2]),
        ('Program:HM1450_VS' + machine_num + '.VPC1.I.Pass', results[3]),
        ('Program:HM1450_VS' + machine_num + '.VPC1.I.Fail', results[4])
    )
    #print(f'({machine_num}) Pass = {results[3]} ; Fail = {results[4]}')
    plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Done', True)
    #print(f'({machine_num}) Keyence Results written to PLC!')
    return results #return results to use in result files

#END keyenceResults_to_PLC

# primary function, to be used by 14/15 threads
def cycle(machine_num, current_stage):
    #globals, not all used
    global start_timer #testing
    is_paused = False
    global kill_threads
    global endProgram_latch_14
    global abort_latch_14
    global reset_latch_14
    global config_info
    #print(config_info)

    part_result = '' # string for .csv logging
    scan_duration = 0 # keeping track of scan time in MS

    #print(f'({machine_num}) Connecting to PLC\n')
    #with LogixDriver('120.57.42.114') as plc:
    with LogixDriver(config_info['plc_ip']) as plc:
        print(f'({machine_num}) Connected to PLC')
        try:
            # Keyence socket connections
            if(machine_num == '14'):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((config_info['keyence_1'], 8500))
            elif(machine_num == '15'):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((config_info['keyence_2'], 8500))

            # clearing potential fault info when resetting
            plc.write(
                ('Program:HM1450_VS' + machine_num + '.VPC1.I.Faulted', False),
                ('Program:HM1450_VS' + machine_num + '.VPC1.I.PhoenixFltCode', 0),
                ('Program:HM1450_VS' + machine_num + '.VPC1.I.KeyenceFltCode', 0)
            )

            while(True):
                if(kill_threads):
                    print(f'({machine_num}) kill_threads detected! Restarting threads...')
                    break
                #check_pause(machine_num) # user pause if 'p' is pressed

                #print(f'({machine_num}) Reading PLC\n')
                results_dict = read_plc_dict(plc, machine_num) #initial PLC tag read for 'robot 14' values
                #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Heartbeat', True)
                #print(results_dict['LoadProgram'][1]) #how to print the value of one specific tag

                # PLC read and check to reset system off PLC(Reset) tag
                reset_check = plc.read('Program:HM1450_VS' + machine_num + '.VPC1.O.Reset')
                if (reset_check[1] == True):
                    #print(f'({machine_num}) (Pre-Load) Reset Detected! Setting back to Stage 0...')
                    current_stage = 0
                    #print(f'({machine_num}) Flushing PLC(Result) tag data...\n')
                    write_plc_flush(plc,machine_num)
                    plc.write(
                        ('Program:HM1450_VS' + machine_num + '.VPC1.O.Reset', False),
                        ('Program:HM1450_VS' + machine_num + '.VPC1.I.Faulted', False),
                        ('Program:HM1450_VS' + machine_num + '.VPC1.I.PhoenixFltCode', 0),
                        ('Program:HM1450_VS' + machine_num + '.VPC1.I.KeyenceFltCode', 0)
                    )

                #checking rising/falling edge logic of .O booleans
                #if((machine_num == '14') and results_dict['LoadProgram'][1] == False):
                    #print('(14) LOAD went LOW!')
                #if((machine_num == '14') and results_dict['StartProgram'][1] == True):
                    #print('(14) StartProgram went HIGH!')
                if((machine_num == '14') and results_dict['EndProgram'][1] == True and endProgram_latch_14 == False):
                    #print('(14) EndProgram went HIGH!')
                    endProgram_latch_14 = True
                elif((machine_num == '14') and results_dict['EndProgram'][1] == False and endProgram_latch_14 == True):
                    #print('(14) EndProgram went LOW!')
                    endProgram_latch_14 = False
                if((machine_num == '14') and results_dict['AbortProgram'][1] == True and abort_latch_14 == False):
                    print('(14) AbortProgram went HIGH!')
                    abort_latch_14 = True
                elif((machine_num == '14') and results_dict['AbortProgram'][1] == False and abort_latch_14 == True):
                    print('(14) AbortProgram went LOW!')
                    abort_latch_14 = False
                if((machine_num == '14') and results_dict['Reset'][1] == True and reset_latch_14 == False):
                    print('(14) Reset went HIGH!')
                    reset_latch_14 = True
                elif((machine_num == '14') and results_dict['Reset'][1] == False and reset_latch_14 == True):
                    print('(14) Reset went LOW!')
                    reset_latch_14 = False

                #STAGE0 CHECK HERE
                if(current_stage == 0):
                    #print(f'({machine_num}) Setting Boolean Flags to Stage 0\n')
                    plc.write(
                        ('Program:HM1450_VS' + machine_num + '.VPC1.I.Busy', False),
                        ('Program:HM1450_VS' + machine_num + '.VPC1.I.Done', False),
                        ('Program:HM1450_VS' + machine_num + '.VPC1.I.Pass', False),
                        ('Program:HM1450_VS' + machine_num + '.VPC1.I.Fail', False)
                    )
                    #print(f'({machine_num}) Flushing PLC(Result) tag data...\n')
                    #write_plc_flush(plc,machine_num) # defaults all .I Phoenix tags at start of cycle
                    plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Ready', True)
                    
                    #print(f'({machine_num}) Stage 0 : Listening for PLC(LOAD_PROGRAM) = 1\n')
                    #reading PLC until LOAD_PROGRAM goes high
                    while(results_dict['LoadProgram'][1] != True):
                        if kill_threads == True:
                            break
                        #check_pause(machine_num) # user pause if 'p' is pressed
                        results_dict = read_plc_dict(plc, machine_num) # continuous PLC read

                        if (results_dict['Reset'][1] == True):
                            #print(f'({machine_num}) (LoadProgram Check) Reset Detected! Setting back to Stage 0...')
                            current_stage = 0
                            #print(f'({machine_num}) Flushing PLC(Result) tag data...\n')
                            write_plc_flush(plc,machine_num)
                            plc.write(
                                ('Program:HM1450_VS' + machine_num + '.VPC1.O.Reset', False),
                                ('Program:HM1450_VS' + machine_num + '.VPC1.I.Faulted', False),
                                ('Program:HM1450_VS' + machine_num + '.VPC1.I.PhoenixFltCode', 0),
                                ('Program:HM1450_VS' + machine_num + '.VPC1.I.KeyenceFltCode', 0)
                            )
                        #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Heartbeat', True)
                        #print(csv_results)
                        time.sleep(.005) # 5ms pause between reads

                    #print('PLC(LOAD_PROGRAM) went high!\n')
                    # Once PLC(LOAD_PROGRAM) goes high, mirror data and set Phoenix(READY) high, signifies end of "loading" process
                    plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Ready', False)
                    #print(f'({machine_num}) Dropping Phoenix(READY) low.\n')

                    ''' 
                    *Part Program Table (14):*
                    1= Cover Face Exhaust Side(625T)
                    2= Cover Face Intake Side(625T)
                    3= Intake Face(625T)
                    4= Front Face(625T)
                    5= Cover Face Exhaust Side(675T)
                    6= Cover Face Intake Side(675T)
                    7= Intake Face(675T)
                    8= Front Face(675T)
                    9= Cover Face Exhaust Side(45T3)
                    10= Cover Face Intake Side(45T3)
                    11= Intake Side(45T3)
                    12= Front Side(45T3) 
                    '''

                    keyence_string = '' #building out external Keyence string for scan file naming
                    
                    if(machine_num == '14'):
                        if(results_dict['PartProgram'][1] == 1):
                            #keyence_string = 'CoverFace-1_625T'
                            keyence_string = config_info['machine_1_1'] #machine num_face num
                        elif(results_dict['PartProgram'][1] == 2):
                            #keyence_string = 'CoverFace-2_625T'
                            keyence_string = config_info['machine_1_2']
                        elif(results_dict['PartProgram'][1] == 3):
                            #keyence_string = 'IntakeFace_625T'
                            keyence_string = config_info['machine_1_3']
                        elif(results_dict['PartProgram'][1] == 4):
                            #keyence_string = 'FrontFace_625T'
                            keyence_string = config_info['machine_1_4']
                        elif(results_dict['PartProgram'][1] == 5):
                            #keyence_string = 'CoverFace-1_675T'
                            keyence_string = config_info['machine_1_5']
                        elif(results_dict['PartProgram'][1] == 6):
                            #keyence_string = 'CoverFace-2_675T'
                            keyence_string = config_info['machine_1_6']
                        elif(results_dict['PartProgram'][1] == 7):
                            #keyence_string = 'IntakeFace_675T'
                            keyence_string = config_info['machine_1_7']
                        elif(results_dict['PartProgram'][1] == 8):
                            #keyence_string = 'FrontFace_675T'
                            keyence_string = config_info['machine_1_8']
                        elif(results_dict['PartProgram'][1] == 9):
                            #keyence_string = 'CoverFace-1_45T3'
                            keyence_string = config_info['machine_1_9']
                        elif(results_dict['PartProgram'][1] == 10):
                            #keyence_string = 'CoverFace-2_45T3'
                            keyence_string = config_info['machine_1_10']
                        elif(results_dict['PartProgram'][1] == 11):
                            #keyence_string = 'IntakeFace_45T3'
                            keyence_string = config_info['machine_1_11']
                        elif(results_dict['PartProgram'][1] == 12):
                            #keyence_string = 'FrontFace_45T3'
                            keyence_string = config_info['machine_1_12']
                    elif(machine_num == '15'):
                        if(results_dict['PartProgram'][1] == 1):
                            #keyence_string = 'DeckFace-1_625T'
                            keyence_string = config_info['machine_2_1']
                        elif(results_dict['PartProgram'][1] == 2):
                            #keyence_string = 'DeckFace-2_625T'
                            keyence_string = config_info['machine_2_2']
                        elif(results_dict['PartProgram'][1] == 3):
                            #keyence_string = 'ExhaustFace_625T'
                            keyence_string = config_info['machine_2_3']
                        elif(results_dict['PartProgram'][1] == 4):
                            #keyence_string = 'RearFace_625T'
                            keyence_string = config_info['machine_2_4']
                        elif(results_dict['PartProgram'][1] == 5):
                            #keyence_string = 'DeckFace-1_675T'
                            keyence_string = config_info['machine_2_5']
                        elif(results_dict['PartProgram'][1] == 6):
                            #keyence_string = 'DeckFace-2_675T'
                            keyence_string = config_info['machine_2_6']
                        elif(results_dict['PartProgram'][1] == 7):
                            #keyence_string = 'ExhaustFace_675T'
                            keyence_string = config_info['machine_2_7']
                        elif(results_dict['PartProgram'][1] == 8):
                            #keyence_string = 'RearFace_675T'
                            keyence_string = config_info['machine_2_8']
                        elif(results_dict['PartProgram'][1] == 9):
                            #keyence_string = 'DeckFace-1_45T3'
                            keyence_string = config_info['machine_2_9']
                        elif(results_dict['PartProgram'][1] == 10):
                            #keyence_string = 'DeckFace-2_45T3'
                            keyence_string = config_info['machine_2_10']
                        elif(results_dict['PartProgram'][1] == 11):
                            #keyence_string = 'ExhaustFace_45T3'
                            keyence_string = config_info['machine_2_11']
                        elif(results_dict['PartProgram'][1] == 12):
                            #keyence_string = 'RearFace_45T3'
                            keyence_string = config_info['machine_2_12']

                    pun_str = intArray_to_str(results_dict['PUN'][1])

                    datetime_info_len_check = [str(results_dict['Month'][1]), str(results_dict['Day'][1]), str(results_dict['Hour'][1]), str(results_dict['Minute'][1]), str(results_dict['Second'][1])]

                    #confirming all date/time fields are 2 digits (except year)
                    for x in range(0,len(datetime_info_len_check)):
                        if(len(datetime_info_len_check[x]) < 2):
                            datetime_info_len_check[x] = '0' + datetime_info_len_check[x]

                    keyence_string = str(pun_str[10:22]) + '_' + str(results_dict['Year'][1]) + '-' + datetime_info_len_check[0] + '-' + datetime_info_len_check[1] + '-' + datetime_info_len_check[2] + '-' + datetime_info_len_check[3] + '-' + datetime_info_len_check[4] + '_' + keyence_string
                    print(f'({machine_num}) LOADING : {keyence_string}')

                    #load_to_trigger_start = datetime.datetime.now()
                    #TODO Send branch data to load Keyence for scan
                    #print(f'Loading: {keyence_string}')
                    LoadKeyence(sock,'MW,#PhoenixControlFaceBranch,' + str(results_dict['PartProgram'][1]) + '\r\n') #Keyence loading message, uses PartProgram from PLC to load specific branch
                    LoadKeyence(sock,'STW,0,"' + keyence_string + '\r\n') # passing external string to Keyence for file naming (?)
                    LoadKeyence(sock,'OW,42,"' + keyence_string + '-Result\r\n') # .csv file naming loads
                    LoadKeyence(sock,'OW,43,"' + keyence_string + '-10Lar\r\n')
                    LoadKeyence(sock,'OW,44,"' + keyence_string + '-10Loc\r\n')
                    #print(f'({machine_num}) Keyence Loaded!\n')

                    #TODO Actually Mirror Data (write back to PLC)
                    #print('!Mirroring Data!\n')
                    write_plc(plc,machine_num,results_dict) #writing back mirrored values to PLC to confirm LOAD has been processed / sent to Keyence

                    #print(f'({machine_num}) Data Mirrored, Setting \'READY\' high\n')
                    plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Ready', True)
                    #time.sleep(3) # FINAL SLEEP REMOVAL
                    current_stage += 1 #incrementing out of STAGE0
                    #print(f'({machine_num}) Stage 1!\nListening for PLC(START_PROGRAM) = 1\n')
                #END STAGE0
                #START STAGE1 : START/END Program
                elif(current_stage == 1):
                    #print('Stage 1!\nListening for PLC(START_PROGRAM) = 1')

                    #if(start_check[1] == True):
                    if(results_dict['StartProgram'][1] == True):
                        #time.sleep(5)
                        #print(f'({machine_num}) StartProgram went high, artificial 5 second pause')

                        start_timer_Trigger_to_Busy = datetime.datetime.now()
                        #Actual Keyence Trigger (T1) here***
                        TriggerKeyence(sock, machine_num, 'T1\r\n')
                        #print(f'({machine_num}) **************Keyence Triggered!*****************\n')
                        start_timer_T1_to_EndProgram = datetime.datetime.now()
                        time_diff = (start_timer_T1_to_EndProgram - start_timer_Trigger_to_Busy)
                        execution_time = time_diff.total_seconds() * 1000
                        if(execution_time > 3000):
                            print(f'({machine_num}) TriggerKeyence timeout fault (longer than 3 seconds)! PhoenixFltCode : 2')
                            plc.write(
                                ('Program:HM1450_VS' + machine_num + '.VPC1.I.PhoenixFltCode', 2),
                                ('Program:HM1450_VS' + machine_num + '.VPC1.I.Faulted', True)
                            )

                        plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Ready', False)
                        #print(f'({machine_num}) PLC(START_PROGRAM) went high! Time to trigger Keyence...\n')

                        start_timer_BusyWrite = datetime.datetime.now()
                        plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Busy', True) #BUSY BEFORE KEYENCE TRIGGER TEST ***
                        end_timer_BusyWrite = datetime.datetime.now()
                        time_diff_BusyWrite = (end_timer_BusyWrite - start_timer_BusyWrite)
                        execution_time = time_diff_BusyWrite.total_seconds() * 1000
                        #print(f'({machine_num}) Writing \'Busy\' to PLC took: {execution_time} ms')
                        
                        #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Busy', True) # Busy goes HIGH while Keyence is scanning
                        #end_timer_Trigger_to_Busy = datetime.datetime.now()
                        diff_timer_Trigger_to_Busy = (end_timer_BusyWrite - start_timer_Trigger_to_Busy)
                        execution_time = diff_timer_Trigger_to_Busy.total_seconds() * 1000
                        #print(f'({machine_num}) TriggerKeyence to PLC(Busy) high in: {execution_time} ms')

                        monitor_endScan(plc, machine_num, sock) # ends Keyence with EndScan
                        end_timer_T1_to_EndScan = datetime.datetime.now()
                        diff_timer_T1_to_EndScan = (end_timer_T1_to_EndScan - start_timer_T1_to_EndProgram)
                        execution_time = diff_timer_T1_to_EndScan.total_seconds() * 1000
                        scan_duration = execution_time #for logging in .csv
                        #print(f'({machine_num}) TriggerKeyence to PLC(EndScan) high in: {execution_time} ms') # log these in .csv? include PUN and Face if applicable

                        #BUSY HIGH TEST*
                        #print(f'({machine_num}) Scan ended! PHOENIX(BUSY) is low\n')
                        plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Busy', False)

                        ExtKeyence(sock) #function to interrupt Keyence

                        keyence_result_check_start = datetime.datetime.now()
                        monitor_KeyenceNotRunning(sock, machine_num) # verify Keyence has processed results and written out FTP files
                        keyence_result_check_end = datetime.datetime.now()
                        time_diff = (keyence_result_check_end - keyence_result_check_start)
                        execution_time = time_diff.total_seconds() * 1000
                        #print(f'({machine_num}) KeyenceNotRunning verified in : {execution_time} ms')
                        if(execution_time > 3000):
                            print(f'({machine_num}) KeyenceNotRunning timeout (took longer than 3 seconds)! PhoenixFltCode : 3')
                            plc.write(
                                ('Program:HM1450_VS' + machine_num + '.VPC1.I.PhoenixFltCode', 3),
                                ('Program:HM1450_VS' + machine_num + '.VPC1.I.Faulted', True)
                            )

                        #abort test, if image was clipped
                        #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Aborted', True)
                        #print(f'({machine_num}) PLC(Aborted) high artificially, waiting .5 sec')
                        #time.sleep(.5)

                        #TODO PASS/FAIL RESULTS
                        keyence_results = []
                        keyence_results = keyenceResults_to_PLC(sock, plc, machine_num)

                        create_csv(machine_num, results_dict, keyence_results, keyence_string, scan_duration) # results to .csv, PER SCAN

                        #check if we're ready to write out a parts results, PER PART
                        part_result = write_part_results(machine_num, part_result, results_dict, keyence_results, pun_str) #appends to result string, writes out file and clears string if on final scan of part
                        if(machine_num == '14'):
                            path = 'E:\\FTP\\' + config_info['keyence_1'] + '\\xg\\'
                        elif(machine_num == '15'):
                            path = 'E:\\FTP\\' + config_info['keyence_2'] + '\\xg\\'
                        
                        #file_cleanup(path)#14 days result/image cleanup

                        # Setting Chinmay's Keyence tag high
                        keyence_msg = 'MW,#PhoenixControlContinue,1\r\n'
                        sock.sendall(keyence_msg.encode())
                        #print(f'({machine_num}) Sent \'#PhoenixControlContinue,1\' to Keyence!')
                        data = sock.recv(32) #obligatory Keyence read to keep buffer clear

                        #print(f'({machine_num})Stage 1 Complete!\n')
                        current_stage += 1
                        #time.sleep(1) # FINAL SLEEP REMOVAL
                    
                #Final Stage, reset to Stage 0 once PLC(END_PROGRAM) and PHOENIX(DONE) have been set low
                elif(current_stage == 2):
                    done_check = plc.read('Program:HM1450_VS' + machine_num + '.VPC1.I.Done')
                    #print(f'({machine_num}) Stage 2 : Listening to PLC(END_PROGRAM) low to reset back to Stage 0\n')
                    if(results_dict['EndProgram'][1] == True):
                        end_timer_T1_to_EndProgram = datetime.datetime.now()
                        diff_timer_T1_to_EndProgram = (end_timer_T1_to_EndProgram - start_timer_T1_to_EndProgram)
                        execution_time = diff_timer_T1_to_EndProgram.total_seconds() * 1000
                        #print(f'({machine_num}) TriggerKeyence to PLC(EndProgram) high in: {execution_time} ms')

                        #print(f'({machine_num}) PLC(END_PROGRAM) is high. Dropping PHOENIX(DONE) low\n')
                        plc.write(
                            ('Program:HM1450_VS' + machine_num + '.VPC1.I.Busy', False),
                            ('Program:HM1450_VS' + machine_num + '.VPC1.I.Pass', False),
                            ('Program:HM1450_VS' + machine_num + '.VPC1.I.Fail', False),
                            ('Program:HM1450_VS' + machine_num + '.VPC1.I.Aborted', False)
                        )
                        plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Done', False)

                        #print(f'({machine_num}) Flushing PLC(Result) tag data...\n')
                        write_plc_flush(plc,machine_num) # defaults all .I Phoenix tags at start of cycle
                        
                        #check_pause(machine_num) # checking if user wants to pause

                    if(results_dict['EndProgram'][1] == False and done_check[1] == False):
                        #print(f'({machine_num}) PLC(END_PROGRAM) is low. Resetting PHOENIX to Stage 0\n')
                        
                        plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Ready', True)
                        current_stage = 0 # cycle complete, reset to stage 0
                        #print(f'({machine_num}) 1 sec artificial pause then reset to Stage 0')
                        #time.sleep(1)
                    
                if(kill_threads == True):
                    print(f'({machine_num}) Cycle : kill_threads high, restarting all threads')
                    break # Kill thread if global is set True for any reason
                time.sleep(.005) #artificial loop timer
        #if something goes wrong while 'cycle' is looping
        except Exception as e:
            if(str(e) == '[WinError 10054] An existing connection was forcibly closed by the remote host'):
                print(f'({machine_num}) Keyence Connection Error, sending PhoenixFltCode : 1')
                plc.write(
                    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PhoenixFltCode', 1),
                    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Faulted', True)
                )
            if(str(e) == 'failed to receive reply'):
                print(f'({machine_num}) Keyence Connection Error, sending PhoenixFltCode : 4')
                plc.write(
                    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PhoenixFltCode', 4),
                    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Faulted', True)
                )
            print(f'({machine_num}) Exception! {e}')
            kill_threads = True # global to stop/restart all threads
        

# function to check if user is holding down 'p' to pause the cycle, then resumes on next 'p'
def check_pause(machine_num):
    running = True
    display = True
    block = False

    #print('Checking for \'p\' to pause...')

    while (running == True):
        if keyboard.is_pressed('p'):
            if block == False:
                display = not display
                block = True
        else:
            block = False
            running = False
        if display:
            #print('No Pause')
            #time.sleep(1)
            pass
        else:
            print(f'({machine_num}) Pausing!')
            time.sleep(10) #stops accidental toggle
            while(running == True):
                print('Paused...')
                if keyboard.is_pressed('p'):
                    running = False
                    print(f'({machine_num}) Unpause!')
                    time.sleep(5) #stops accidental toggle
                time.sleep(1)
#END check_pause

#sets PLC(Heartbeat) high every second to verify we're still running and communicating
def heartbeat(machine_num):
    global config_info
    with LogixDriver(config_info['plc_ip']) as plc:
        print(f'({machine_num}) Heartbeat thread connected to PLC. Writing \'Heartbeat\' high every 1 second\n')
        while(True):
            plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Heartbeat', True)
            #print(f'({machine_num}) Heartbeat written HIGH')
            time.sleep(1)
            if(kill_threads == True):
                print(f'({machine_num}) Heartbeat : kill_threads high, restarting all threads')
                break # Kill thread if global is set True for any reason
#END heartbeat

# George's request for a .csv file per inspection
def create_csv(machine_num, results, keyence_results, face_name, duration):
    global config_info
    #E:\FTP\172.19.146.81\xg\result
    file_name = '' #empty string for .csv file name
    if(machine_num == '14'):
        #file_name = 'E:\\FTP\\172.19.145.80\\xg\\result'
        file_name = 'E:\\FTP\\' + config_info['keyence_1'] +'\\xg\\result'
    elif(machine_num == '15'):
        #file_name = 'E:\\FTP\\172.19.146.81\\xg\\result'
        file_name = 'E:\\FTP\\' + config_info['keyence_2'] +'\\xg\\result'
    file_name = file_name + '\\' + face_name + '.txt'
    with open(file_name, 'w', newline='') as f:
        f.write('PART_TYPE_2, ' + str(results['PartType'][1]) + '\n')
        f.write('PART_PROGRAM_2, ' + str(results['PartProgram'][1]) + '\n')
        f.write('SCAN_NUMBER_2, ' + str(results['ScanNumber'][1]) + '\n')
        f.write('PUN_2, ' + intArray_to_str(results['PUN'][1]) + '\n')
        f.write('GM_PART_NUMBER_2, ' + intArray_to_str(results['GMPartNumber'][1]) + '\n')
        f.write('MODULE_2, ' + str(results['Module'][1]) + '\n')
        f.write('PLANTCODE_2, ' + str(results['PlantCode'][1]) + '\n')
        f.write('MONTH_2, ' + str(results['Month'][1]) + '\n')
        f.write('DAY_2, ' + str(results['Day'][1]) + '\n')
        f.write('YEAR_2, ' + str(results['Year'][1]) + '\n')
        f.write('HOUR_2, ' + str(results['Hour'][1]) + '\n')
        f.write('MINUTE_2, ' + str(results['Minute'][1]) + '\n')
        f.write('SECOND_2, ' + str(results['Second'][1]) + '\n')
        f.write('OP 110 CNC_2, ' + str(results['QualityCheckOP110'][1]) + '\n')
        f.write('OP 120 CNC_2, ' + str(results['QualityCheckOP120'][1]) + '\n')
        f.write('OP 130 CNC_2, ' + str(results['QualityCheckOP130'][1]) + '\n')
        f.write('OP 140 CNC_2, ' + str(results['QualityCheckOP140'][1]) + '\n')
        f.write('OP 150 CNC_2, ' + str(results['QualityCheckOP150'][1]) + '\n')
        f.write('OP_310_DECK_MILL_CNC_2, ' + str(results['QualityCheckOP310'][1]) + '\n')
        f.write('OP 320 CNC_2, ' + str(results['QualityCheckOP320'][1]) + '\n')
        f.write('OP 330 CNC_2, ' + str(results['QualityCheckOP330'][1]) + '\n')
        f.write('OP 340 CNC_2, ' + str(results['QualityCheckOP340'][1]) + '\n')
        f.write('OP 360 CNC_2, ' + str(results['QualityCheckOP360'][1]) + '\n')
        f.write('OP 370 CNC_2, ' + str(results['QualityCheckOP370'][1]) + '\n')
        f.write('OP 380 CNC_2, ' + str(results['QualityCheckOP380'][1]) + '\n')
        f.write('OP 390 CNC_2, ' + str(results['QualityCheckOP390'][1]) + '\n')
        f.write('Scout_part_tracking_2, ' + str(results['QualityCheckScoutPartTracking'][1]) + '\n')
        f.write('Defect_Number_2, ' + str(keyence_results[0]) + '\n')
        f.write('Defect_Size_2, ' + str(keyence_results[1]) + '\n')
        f.write('Defect_Zone_2, ' + str(keyence_results[2]) + '\n')
        f.write('PASS_2, ' + str(keyence_results[3]) + '\n')
        f.write('FAIL_2, ' + str(keyence_results[4]) + '\n')
        f.write('DURATION_2, ' + str(duration) + '\n')

    pass
#END create_csv

# Gerry's request to log all results per part in one continuous file
def write_part_results(machine_num, part_result, results_dict, keyence_results, pun_str):
    global config_info
    #print(f'({machine_num}) part_result : {part_result}\n')
    #print(f'({machine_num}) keyence_results : {keyence_results}\n')
    pun_str = pun_str.strip() # remove spaces
    pun_str = pun_str.rstrip('\\x00') # remove nulls

    t = datetime.datetime.now()
    s = t.strftime('%Y-%m-%d %H:%M:%S.%f') # stripping off decimal (ms)
    dt_string = t.strftime("%Y-%m-%d") #datetime stamped file naming, year#-month#-day#

    if(machine_num == '14'):
        # designating end of part by part #, to write out actual line in .csv
        if((results_dict['PartProgram'][1] == 3) or (results_dict['PartProgram'][1] == 7) or (results_dict['PartProgram'][1] == 11)):
            part_result = part_result + str(keyence_results[3]) # final append to string before writing out to .txt file
            file_name = '' #empty string for .txt file name
            file_name = 'E:\\part_results_consolidated\\' + dt_string + '-machine_14.txt'
            with open(file_name, 'a+', newline='') as f:
                #t = datetime.datetime.now()
                #s = t.strftime('%Y-%m-%d %H:%M:%S.%f') # stripping off decimal (ms)
                f.write(s[:-4] + ', ')
                f.write(pun_str + ', ')
                f.write(part_result + '\n\n')
                print(f'({machine_num}) (WROTE) part_result : {part_result}')
                part_result = ''
                return part_result # clearing then returning pass result for next part
        else:
            part_result = part_result + str(keyence_results[3]) + ', ' # appending pass/fail data to part_result string if we're not @ end of the part
            return part_result
    elif(machine_num == '15'):
        if((results_dict['PartProgram'][1] % 4) == 0):
            part_result = part_result + str(keyence_results[3]) # final append to string before writing out to .txt file
            file_name = '' #empty string for .txt file name
            file_name = 'E:\\part_results_consolidated\\' + dt_string + '-machine_15.txt'
            with open(file_name, 'a+', newline='') as f:
                #t = datetime.datetime.now()
                #s = t.strftime('%Y-%m-%d %H:%M:%S.%f') # stripping off decimal (ms)
                f.write(s[:-4] + ', ')
                f.write(pun_str + ', ')
                f.write(part_result + '\n\n')
                part_result = ''
                return part_result # clearing then returning pass result for next part
        else:
            part_result = part_result + str(keyence_results[3]) + ', ' # appending pass/fail data to part_result string if we're not @ end of the part
            return part_result

    #file_cleanup('E:\\part_results_consolidated\\') #deleting old records if older than 14 days

    '''
    #checking if previous files are >2weeks old, delete if so
    path = 'E:\\part_results_consolidated\\' #folder path
    today = datetime.datetime.today()
    os.chdir(path) #'cd' command to set path

    for root,directories,files in os.walk(path,topdown=False):
        for name in files:
            #last modified time
            mod_t = os.stat(os.path.join(root, name))[8]
            filetime = datetime.datetime.fromtimestamp(t) - today
            #checking if old (greater than two weeks, 14 days)
            if filetime.days <= -14:
                print(os.path.join(root,name), filetime.days)
                os.remove(os.path.join(root,name))#actual file removal
    '''
#END write_part_results

#deletes anything older than 14 days at the argument path (and below)
def file_cleanup(path1, path2, path3):
    while(True):
        global config_info
        global kill_threads
        #break if other threads are having issues
        if(kill_threads):
            break
        #path = 'E:\\part_results_consolidated\\' #folder path
        today = datetime.datetime.today()
        os.chdir(path1) #'cd' command to set path
        age_check = int(config_info['file_age_check'])

        for root,directories,files in os.walk(path1,topdown=False):
            for name in files:
                #last modified time
                mod_t = os.stat(os.path.join(root, name))[8]
                filetime = datetime.datetime.fromtimestamp(mod_t) - today
                #checking if old (greater than two weeks, 14 days)
                #if filetime.days <= -14:
                if filetime.days <= -age_check:
                    print(os.path.join(root,name), filetime.days)
                    os.remove(os.path.join(root,name))#actual file removal
        #end keyence_1 folder cleanup
        today = datetime.datetime.today()
        os.chdir(path2) #'cd' command to set path

        for root,directories,files in os.walk(path2,topdown=False):
            for name in files:
                #last modified time
                mod_t = os.stat(os.path.join(root, name))[8]
                filetime = datetime.datetime.fromtimestamp(mod_t) - today
                #checking if old (greater than two weeks, 14 days)
                #if filetime.days <= -14:
                if filetime.days <= -age_check:
                    print(os.path.join(root,name), filetime.days)
                    os.remove(os.path.join(root,name))#actual file removal
        #end keyence_2 folder cleanup
        today = datetime.datetime.today()
        os.chdir(path3) #'cd' command to set path

        for root,directories,files in os.walk(path3,topdown=False):
            for name in files:
                #last modified time
                mod_t = os.stat(os.path.join(root, name))[8]
                filetime = datetime.datetime.fromtimestamp(mod_t) - today
                #checking if old (greater than two weeks, 14 days)
                #if filetime.days <= -14:
                if filetime.days <= -age_check:
                    print(os.path.join(root,name), filetime.days)
                    os.remove(os.path.join(root,name))#actual file removal
        #end parts_consolidated folder cleanup
        time.sleep(86400) #sleep for 1 day, or until thread is restarted
#END file_cleanup

#START main()
def main():
    global current_stage_14 #keeps track of which stage program is currently in from the timing process
    global current_stage_15
    global kill_threads # signal to end threads if an exception is thrown
    global config_info

    #config_info = {}
    config_info = read_config()
    print(config_info)

    #declaring threads, does not run
    #t1 = threading.Thread(target=TriggerKeyence, args=[sock, 'T1\r\n']) #thread1, passing in socket connection and 'T1' keyence command
    #t2 = threading.Thread(target=ExtKeyence, args=[sock, 'TE,0\r\n', 'TE,1\r\n']) #thread2, uses 'TE,0' and 'TE,1' to cancel while scanning and reset to original state

    # original threading tests
    
    t1 = threading.Thread(target=cycle, args=['14', current_stage_14])
    t2 = threading.Thread(target=cycle, args=['15', current_stage_15])

    t1_heartbeat = threading.Thread(target=heartbeat, args=['14'])
    t2_heartbeat = threading.Thread(target=heartbeat, args=['15'])

    #file cleanup thread, paths hard-coded right now, could probably be redone as a list
    t_file_cleanup = threading.Thread(target=file_cleanup, args=['E:\\FTP\\' + config_info['keyence_1'] + '\\xg\\', 'E:\\FTP\\' + config_info['keyence_2'] + '\\xg\\', 'E:\\part_results_consolidated\\'])

    kill_threads = False
    print("Starting Threads (14 & 15)...")
    t1.start()
    t2.start()
    #t1.join()
    #t2.join() # making sure threads complete before moving forward

    print("Starting Heartbeat Threads (14 & 15)")
    t1_heartbeat.start()
    t2_heartbeat.start()

    print("File Cleanup...")
    t_file_cleanup.start()

    #joining threads so they're not spammed, keeps them all sync'd up (max of 1 active at any time)
    t1.join()
    t2.join()
    t1_heartbeat.join()
    t2_heartbeat.join()
    t_file_cleanup.join()
    
    #print('This code is beyond the threads!')

#END 'main'

#implicit 'main()' declaration
if __name__ == '__main__':
    while(True):
        main()