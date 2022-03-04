import threading
import datetime, time
import socket
import csv
from logging import debug
from pycomm3 import LogixDriver
from pycomm3.cip.data_types import DINT, UINT
import json
import os
import keyboard

'''
This is the first testing thread for Grob using threading and an all-in-one Python program.

Progresses through the timing diagram based on tag values read off Grobs's PLC. Loads and Triggers Keyence.

*** Only reads 'CAM01' PLC tags and communicates with Keyence#1 (172.19.147.82)
'''

trigger_count = 0
slow_count = 0
longest_time = 0

current_stage_1 = 0
current_stage_2 = 0

sock_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect(('192.168.1.83', 8500)) # 'sock' is the connection variable used to communicate with the Keyence
sock_1.connect(('172.19.147.82', 8500)) # GROB address, Keyence head #1

sock_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect(('192.168.1.83', 8500)) # 'sock' is the connection variable used to communicate with the Keyence
sock_2.connect(('172.19.148.83', 8500)) # GROB address, Keyence head #2

lock = threading.Lock()

arrayOutTags = [
    'LOAD_PROGRAM',
    'START_PROGRAM',
    'END_PROGRAM',
    'ABORT_PROGRAM',
    'RESET',
    'PART_TYPE',
    'PART_PROGRAM',
    #'SCAN_NUMBER',
    'PUN{64}',
    'MODULE',
    #'PLANTCODE',
    'TIMESTAMP_MONTH',
    'TIMESTAMP_DAY',
    'TIMESTAMP_YEAR',
    'TIMESTAMP_HOUR',
    'TIMESTAMP_MINUTE',
    'TIMESTAMP_SECOND'
    ];

tagKeys = []
for tag in arrayOutTags:
    tagKeys.append(tag.split("{")[0]) # delete trailiing { if it exists

#order matters!
tagCmds = [
    'LOAD_PROGRAM',
    'START_PROGRAM',
    'END_PROGRAM',
    'ABORT_PROGRAM',
    'RESET'];

tagDateTime = [
    'TIMESTAMP_MONTH',
    'TIMESTAMP_DAY',
    'TIMESTAMP_YEAR',
    'TIMESTAMP_HOUR',
    'TIMESTAMP_MINUTE',
    'TIMESTAMP_SECOND'];

tagStringInt = [
    'PUN'];

tagInt = [
    'PART_TYPE',
    'PART_PROGRAM',
    'SCAN_NUMBER'
    ];

tagChar = [
    'MODULE',
    'PLANTCODE'
    ];

def read_plc_dict(plc, machine_num):
    #print("read_plc_dict, generating list of read tags")
    readList = []
    for tag in arrayOutTags :
        newTag = 'Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.O.' + tag;
        #print(newTag);
        readList.append(newTag)
        
    resultsList = plc.read(*readList) # tag, value, type, error
    readDict = {}

    #print("returned results")
    #print(resultsList)

    for tag in resultsList:
        key = tag.tag.split(".")[-1]
        #print(key)
        #print(tag)
        readDict[key] = tag

    #print(readDict)
    return readDict
#END read_plc_dict

#Writing back to PLC to mirror data on LOAD
#TODO: Modify to use running values instead of relying on reads from an OPC server
def write_plc(plc, machine_num, results):
    #logging how long the 'read' takes
    start_time = datetime.datetime.now()

    plc.write(('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.PART_TYPE', results['PART_TYPE'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.PART_PROGRAM', results['PART_PROGRAM'][1]),
    #('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.SCAN_NUMBER', results['SCAN_NUMBER'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.PUN{64}', results['PUN'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.MODULE', results['MODULE'][1]),
    #('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.PLANTCODE', results['PLANTCODE'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_MONTH', results['TIMESTAMP_MONTH'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_DAY', results['TIMESTAMP_DAY'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_YEAR', results['TIMESTAMP_YEAR'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_HOUR', results['TIMESTAMP_HOUR'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_MINUTE', results['TIMESTAMP_MINUTE'][1]),
    ('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_SECOND', results['TIMESTAMP_SECOND'][1])
    )

    end_time = datetime.datetime.now()
    time_diff = (end_time - start_time)
    execution_time = time_diff.total_seconds() * 1000
    print('\'plc.write()\' took %d ms to run' % (execution_time))
    #print("Finished writing PLC...")
    pass
#END write_plc

# Flushes PLC data mirroring tags (to 0)
def write_plc_flush(plc, machine_num):

    plc_writer_PUN = [72, 101, 108, 108, 111, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35, 35]

    plc.write(
    ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.PART_TYPE', 0),
    ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.PART_PROGRAM', 0),
    #('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.SCAN_NUMBER', 0),
    ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.PUN{64}', plc_writer_PUN),
    ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.MODULE', 0),
    #('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.PLANTCODE', 0),
    ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_MONTH', 0),
    ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_DAY', 0),
    ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_YEAR', 0),
    ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_HOUR', 0),
    ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_MINUTE', 0),
    ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.TIMESTAMP_SECOND', 0)
    )
# end write_plc_flush

# Triggering Keyence with socket only being connected/closed ONCE (program startup and shutdown)
def TriggerKeyence(sock, machine_num, item):

    global trigger_count
    global slow_count
    global longest_time
    global start_timer_END

    #verify Keyence(Trg1READY) is high before we send a 'T1' trigger
    with lock:
        message = 'MR,%Trg1READY\r\n' #initial read of '%BUSY' to ensure scan is actually taking place (%BUSY == 1)
        sock.sendall(message.encode())
        data = sock.recv(32)
        print(f'({machine_num}) %Trg1READY = {data}')

    # looping until '%BUSY' == 0
    while(data != b'MR,+0000000001.000000\r'):
        print(f'Keyence(Trg1READY) was not high, \'T1\' not sent!')
        # utilizing 'with' to use thread lock
        #message = 'T1\r\n'
        message = 'MR,%Trg1READY\r\n'
        with lock:
            sock.sendall(message.encode())
            data = sock.recv(32)
        print(f'({machine_num}) TriggerKeyence: received "%s"' % data)
        #print('Scanning...')
        time.sleep(.2) # artificial 1ms pause between Keyence reads

    message = item
    trigger_start_time = datetime.datetime.now() # marking when 'T1' is sent
    with lock:
        sock.sendall(message.encode())
        data = sock.recv(32)
        print(f'({machine_num}) received "%s"\n' % data)
        #start_timer_END = datetime.datetime.now() # END test timer
    #time_diff = (start_timer_END - start_timer)
    #execution_time = time_diff.total_seconds() * 1000
    #print(f'PLC(Start) read to Keyence(T1) read in : {execution_time} ms')

    #am I using these right?(!)
    with lock:
        message = 'MR,%Trg1READY\r\n' #initial read of '%BUSY' to ensure scan is actually taking place (%BUSY == 1)
        sock.sendall(message.encode())
        data = sock.recv(32)
        print(f'%Trg1READY = {data}')
    
    '''
    if(execution_time > longest_time):
        longest_time = execution_time
    '''
    # looping until '%BUSY' == 0
    while(data != b'MR,+0000000000.000000\r'):
    #while(data != b'T1\r'):
        # utilizing 'with' to use thread lock
        #message = 'T1\r\n'
        message = 'MR,%Trg1READY\r\n'
        with lock:
            sock.sendall(message.encode())
            data = sock.recv(32)
        print(f'({machine_num})TriggerKeyence: received "%s"' % data)
        #print('Scanning...')
        time.sleep(.2) # artificial 1ms pause between Keyence reads
    #print('Keyence %Trg1READY verified!')
    trigger_end_time = datetime.datetime.now() # marking when '%BUSY' is read off Keyence
    time_diff = (trigger_end_time - trigger_start_time)
    execution_time = time_diff.total_seconds() * 1000
    print(f'\n({machine_num}) \'T1\' sent to \'%Trg1READY\' verified in {execution_time} ms\n')
#END 'TriggerKeyence'

#sends specific Keyence Program (branch) info to pre-load/prepare Keyence for Trigger(T1)
def LoadKeyence(sock, item):
    print('LOADING KEYENCE')
    message = item # setting 'TE,0' first
    with lock:
        sock.sendall(message.encode()) # sending TE,0
        print(f'\n\'{item}\' Sent!')
        data = sock.recv(32)
        print('received "%s"' % data)

# sends 'TE,0' then 'TE,1' to the Keyence, RESETting to original state (READY for new 'T1')
def ExtKeyence(sock, item, item_RESET):
    message = item # setting 'TE,0' first
    with lock:
        sock.sendall(message.encode()) # sending TE,0
        print('\n\'TE,0\' Sent!')

        message = item_RESET # setting 'TE,1' to RESET
        sock.sendall(message.encode()) # sending, TE,1
        print('\'TE,1\' Sent!')

        #data = sock.recv(32)
        #print('received "%s"' % data)
# END 'ExtKeyence'

### THE PASTE

# reading PLC(END_SCAN) until it goes high to interrupt current Keyence scan
def monitor_END_SCAN(plc, machine_num, sock):
    print(f'({machine_num}) Listening for PLC(END_SCAN) high\n')
    current = plc.read('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.O.END_SCAN')

    while(current[1] != True):
        current = plc.read('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.O.END_SCAN')
        time.sleep(.005)
    print(f'({machine_num}) PLC(END_SCAN) went high!\n')

    ExtKeyence(sock) #function to interrupt Keyence
    pass
#END monitor_END_SCAN

# function to monitor the Keyence tag 'KeyenceNotRunning', when True (+00001.00000) we know Keyence has completed result processing and FTP file write
def monitor_KeyenceNotRunning(sock, machine_num):
    #print(f'({machine_num}) Keyence Processing...')
    #msg = 'MR,#KeyenceNotRunning\r\n'
    msg = 'MR,#KeyenceNotRunning\r\n'
    sock.sendall(msg.encode())
    data = sock.recv(32)
    while(data != b'MR,+0000000001.000000\r'):
        sock.sendall(msg.encode())
        data = sock.recv(32)
        time.sleep(.001)
    #print(f'({machine_num}) Keyence Processing Complete!\n')
    pass
#END monitor_KeyenceNotRunning

# primary function, to be used by 14/15 threads
def cycle(machine_num, sock, current_stage):
    global start_timer #testing
    is_paused = False

    print(f'({machine_num}) Connecting to PLC\n')
    with LogixDriver('120.57.42.114') as plc:
        while(True):
            check_pause() # user pause if 'p' is pressed

            #print(f'({machine_num}) Reading PLC\n')
            results_dict = read_plc_dict(plc, machine_num) #initial PLC tag read for 'robot 14' values
            #print(results_dict['LOAD_PROGRAM'][1]) #how to print the value of one specific tag

            # PLC read and check to RESET system off PLC(RESET) tag
            RESET_check = plc.read('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.O.RESET')
            if (RESET_check[1] == True):
                print(f'({machine_num}) RESET Detected! Setting back to Stage 0...')
                current_stage = 0
                print(f'({machine_num}) Flushing PLC(Result) tag data...\n')
                write_plc_flush(plc,machine_num)

                plc.write('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.O.RESET', False)

            #STAGE0 CHECK HERE
            if(current_stage == 0):
                print(f'({machine_num}) Setting Boolean Flags to Stage 0\n')
                plc.write(
                    ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.BUSY', False),
                    ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.DONE', False),
                    ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.PASS', False),
                    ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.FAIL', False)
                )
                #print(f'({machine_num}) Flushing PLC(Result) tag data...\n')
                #write_plc_flush(plc,machine_num) # defaults all .I Phoenix tags at start of cycle
                plc.write('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.READY', True)
                
                print(f'({machine_num}) Stage 0 : Listening for PLC(LOAD_PROGRAM) = 1\n')
                #reading PLC until LOAD_PROGRAM goes high
                while(results_dict['LOAD_PROGRAM'][1] != True):
                    check_pause() # user pause if 'p' is pressed
                    results_dict = read_plc_dict(plc, machine_num) # continuous PLC read
                    #print(csv_results)
                    time.sleep(.005) # 5ms pause between reads

                #print('PLC(LOAD_PROGRAM) went high!\n')
                # Once PLC(LOAD_PROGRAM) goes high, mirror data and set Phoenix(READY) high, signifies end of "loading" process
                plc.write('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.READY', False)
                print(f'({machine_num}) Dropping Phoenix(READY) low.\n')

                ''' PART_PROGRAM mapping
                # 1A (?), is this a string?!
                (R2)1=Ring Seal Surface Section 1, 
                (R2)1A=Ring Seal Surface Section 2, 
                (R2)1A=Ring Seal Surface Section 3,
                (R2)2=Case Mounting Face Section 1, 
                (R2)3=Case Mounting Face Section 2, 
                (R2)4=Case Mounting Face Section 3,
                (R3)1=Case Rear Extension 1 Sealing Face Section 1,  
                (R3)2=Case Rear Extension 1 Sealing Face Section 2,
                (R3)3=Case Rear Extension OD Pilot Section 1,  
                (R3)4=Case Rear Extension OD Pilot Section 2,
                (R3)5=H114,  
                (R3)6=Shift Cable Holes,  
                (R3)7=Oil Cooler Ports,  
                (R3)8=H308,  
                (R3)9=H403,  
                (R3)10= H406
                '''

                keyence_string = '' #building out external Keyence string for scan file naming
                if(machine_num == '1'):
                    if(results_dict['PART_PROGRAM'][1] == 1):
                        keyence_string = 'Ring_Seal_Surface_Section_1'
                    elif(results_dict['PART_PROGRAM'][1] == 2):
                        keyence_string = 'Ring_Seal_Surface_Section_2'
                    elif(results_dict['PART_PROGRAM'][1] == 3):
                        keyence_string = 'Ring_Seal_Surface_Section_3'
                    elif(results_dict['PART_PROGRAM'][1] == 4):
                        keyence_string = 'Case_Mounting_Face_Section_1'
                    elif(results_dict['PART_PROGRAM'][1] == 5):
                        keyence_string = 'Case_Mounting_Face_Section_2'
                    elif(results_dict['PART_PROGRAM'][1] == 6):
                        keyence_string = 'Case_Mounting_Face_Section_3'
                    elif(results_dict['PART_PROGRAM'][1] == 12):
                        keyence_string = 'FrontFace-45T3'
                elif(machine_num == '2'):
                    if(results_dict['PART_PROGRAM'][1] == 1):
                        keyence_string = 'Case_Rear_Extension_1_Sealing_Face_Section_1'
                    elif(results_dict['PART_PROGRAM'][1] == 2):
                        keyence_string = 'Case_Rear_Extension_1_Sealing_Face_Section_2'
                    elif(results_dict['PART_PROGRAM'][1] == 3):
                        keyence_string = 'Case_Rear_Extension_OD_Pilot_Section_1'
                    elif(results_dict['PART_PROGRAM'][1] == 4):
                        keyence_string = 'Case_Rear_Extension_OD_Pilot_Section_2'
                    elif(results_dict['PART_PROGRAM'][1] == 5):
                        keyence_string = 'H114'
                    elif(results_dict['PART_PROGRAM'][1] == 6):
                        keyence_string = 'Shift_Cable_Holes'
                    elif(results_dict['PART_PROGRAM'][1] == 7):
                        keyence_string = 'Oil_Cooler_Ports'
                    elif(results_dict['PART_PROGRAM'][1] == 8):
                        keyence_string = 'H308'
                    elif(results_dict['PART_PROGRAM'][1] == 9):
                        keyence_string = 'H403'
                    elif(results_dict['PART_PROGRAM'][1] == 10):
                        keyence_string = 'H406'

                #load_to_trigger_start = datetime.datetime.now()
                #TODO Send branch data to load Keyence for scan
                print(f'Loading: {keyence_string}')
                LoadKeyence(sock,'MW,#PhoenixControlFaceBranch,' + str(results_dict['PART_PROGRAM'][1]) + '\r\n') #Keyence loading message, uses PART_PROGRAM from PLC to load specific branch
                LoadKeyence(sock,'STW,0,"' + keyence_string + '\r\n') # PASSing external string to Keyence for file naming (?)
                print(f'({machine_num}) Keyence Loaded!\n')

                #TODO Actually Mirror Data (write back to PLC)
                #print('!Mirroring Data!\n')
                write_plc(plc,machine_num,results_dict) #writing back mirrored values to PLC to confirm LOAD has been processed / sent to Keyence
                #timer_mirrored_to_START_PROGRAM = datetime.datetime.now()
                #LOAD_PROGRAM_to_Mirrored_diff = (timer_mirrored_to_START_PROGRAM - load_to_trigger_start)
                #execution_time = LOAD_PROGRAM_to_Mirrored_diff.total_seconds() * 1000
                #print(f'({machine_num}) LOAD_PROGRAM(high) read until Mirror Complete in {execution_time} ms')

                #csv_results['DATA'] = csv_results_plc['DATA']
                #time.sleep(1) # FINAL SLEEP REMOVAL #artificial pause to see step happening in testing
                print(f'({machine_num}) Data Mirrored, Setting \'READY\' high\n')
                plc.write('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.READY', True)
                #time.sleep(3) # FINAL SLEEP REMOVAL
                current_stage += 1 #incrementing out of STAGE0
                print(f'({machine_num}) Stage 1!\nListening for PLC(START_PROGRAM) = 1\n')
            #END STAGE0
            #START STAGE1 : START/END Program
            elif(current_stage == 1):
                #print('Stage 1!\nListening for PLC(START_PROGRAM) = 1')
                #time.sleep(.01) # FINAL SLEEP REMOVAL #10ms artificial delay for testing

                '''
                start_check = plc.read('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.O.START_PROGRAM')
                while(start_check[1] == False):
                    start_check = plc.read('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.O.START_PROGRAM')
                    time.sleep(.005)
                '''

                #if(start_check[1] == True):
                if(results_dict['START_PROGRAM'][1] == True):
                    plc.write('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.READY', False)
                    print(f'({machine_num}) PLC(START_PROGRAM) went high! Time to trigger Keyence...\n')

                    start_timer_Trigger_to_BUSY = datetime.datetime.now()
                    plc.write('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.BUSY', True) #BUSY BEFORE KEYENCE TRIGGER TEST ***
                    end_timer_BUSYWrite = datetime.datetime.now()
                    time_diff_BUSYWrite = (end_timer_BUSYWrite - start_timer_Trigger_to_BUSY)
                    execution_time = time_diff_BUSYWrite.total_seconds() * 1000
                    print(f'({machine_num}) Writing \'BUSY\' to PLC took: {execution_time} ms')
                    # ARTIFICIAL PAUSE TESTING, DIFFERENT ROBOT / FACE DIFFERENT TIME.SLEEP
                    #if(machine_num == '14'):
                        #print(f'(14) .5 SECOND ARTIFICIAL DELAY')
                        #time.sleep(.5)
                    
                    #Actual Keyence Trigger (T1) here***
                    TriggerKeyence(sock, machine_num, 'T1\r\n')
                    start_timer_T1_to_END_PROGRAM = datetime.datetime.now()
                    #print('WAITING 2 SECONDS (TEST)')
                    #time.sleep(2) #testing pause***
                    
                    #plc.write('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.BUSY', True) # BUSY goes HIGH while Keyence is scanning
                    #end_timer_Trigger_to_BUSY = datetime.datetime.now()
                    diff_timer_Trigger_to_BUSY = (start_timer_T1_to_END_PROGRAM - start_timer_Trigger_to_BUSY)
                    execution_time = diff_timer_Trigger_to_BUSY.total_seconds() * 1000
                    print(f'({machine_num}) PLC(BUSY) high to TriggerKeyence in: {execution_time} ms')

                    monitor_END_SCAN(plc, machine_num, sock) # ends Keyence with END_SCAN
                    end_timer_T1_to_END_SCAN = datetime.datetime.now()
                    diff_timer_T1_to_END_SCAN = (end_timer_T1_to_END_SCAN - start_timer_T1_to_END_PROGRAM)
                    execution_time = diff_timer_T1_to_END_SCAN.total_seconds() * 1000
                    print(f'({machine_num}) TriggerKeyence to PLC(END_SCAN) high in: {execution_time} ms')

                    monitor_KeyenceNotRunning(sock, machine_num) # verify Keyence has processed results and written out FTP files

                    #BUSY HIGH TEST*
                    print(f'({machine_num}) Scan ended! PHOENIX(BUSY) is low\n')
                    plc.write('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.BUSY', False)
                    

                    #TODO PASS/FAIL RESULTS
                    keyenceResults_to_PLC(sock, plc, machine_num)
                    #plc.write('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.PASS', True)
                    #plc.write('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.DONE', True)
                    #print(f'({machine_num}) PASS/FAIL/DONE data written out\n')
                    #print('PHOENIX(PASS) and PHOENIX(DONE) = 1\n')

                    # Setting Chinmay's Keyence tag high
                    keyence_msg = 'MW,#PhoenixControlContinue,1\r\n'
                    sock.sendall(keyence_msg.encode())
                    print(f'({machine_num}) Sent \'#PhoenixControlContinue,1\' to Keyence!')
                    data = sock.recv(32) #obligatory Keyence read to keep buffer clear

                    print(f'({machine_num})Stage 1 Complete!\n')
                    current_stage += 1
                    #time.sleep(1) # FINAL SLEEP REMOVAL
                
            #Final Stage, RESET to Stage 0 once PLC(END_PROGRAM) and PHOENIX(DONE) have been set low
            elif(current_stage == 2):
                DONE_check = plc.read('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.DONE')
                #print(f'({machine_num}) Stage 2 : Listening to PLC(END_PROGRAM) low to RESET back to Stage 0\n')
                if(results_dict['END_PROGRAM'][1] == True):
                    end_timer_T1_to_END_PROGRAM = datetime.datetime.now()
                    diff_timer_T1_to_END_PROGRAM = (end_timer_T1_to_END_PROGRAM - start_timer_T1_to_END_PROGRAM)
                    execution_time = diff_timer_T1_to_END_PROGRAM.total_seconds() * 1000
                    #print(f'({machine_num}) TriggerKeyence to PLC(END_PROGRAM) high in: {execution_time} ms')

                    print(f'({machine_num}) PLC(END_PROGRAM) is high. Dropping PHOENIX(DONE) low\n')
                    plc.write(
                        ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.BUSY', False),
                        ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.PASS', False),
                        ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.FAIL', False)
                    )
                    plc.write('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.DONE', False)

                    print(f'({machine_num}) Flushing PLC(Result) tag data...\n')
                    write_plc_flush(plc,machine_num) # defaults all .I Phoenix tags at start of cycle

                    print(f'({machine_num}) Artificial Pause (1 seconds)...Then READY high')
                    time.sleep(1)
                    
                    check_pause() # checking if user wants to pause

                if(results_dict['END_PROGRAM'][1] == False and DONE_check[1] == False):
                    print(f'({machine_num}) PLC(END_PROGRAM) is low. RESETting PHOENIX to Stage 0\n')
                    
                    plc.write('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.READY', True)
                    current_stage = 0 # cycle complete, RESET to stage 0
                
                #time.sleep(1) # FINAL SLEEP REMOVAL
            time.sleep(.005) #artificial loop timer
        pass

# function to check if user is holding down 'p' to pause the cycle, then resumes on next 'p'
def check_pause():
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
            print('Pausing!')
            time.sleep(5) #stops accidental toggle
            while(running == True):
                print('Paused...')
                if keyboard.is_pressed('p'):
                    running = False
                    print('Unpause!')
                    time.sleep(5) #stops accidental toggle
                time.sleep(1)
#END check_pause

def heartbeat(machine_num):
    with LogixDriver('120.57.42.114') as plc:
        print(f'({machine_num}) Heartbeat thread connected to PLC. Writing \'HEARTBEAT\' high every 1 second')
        while(True):
            plc.write('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.HEARTBEAT', True)
            #print(f'({machine_num}) Heartbeat written HIGH')
            time.sleep(1)
#END heartbeat

# read defect information from the Keyence, then PASSes that as well as PASS,FAIL,DONE to PLC
def keyenceResults_to_PLC(sock, plc, machine_num):
    #TODO read results from Keyence then PASS to proper tags on PLC
    result_messages = ['MR,#ReportDefectCount\r\n', 'MR,#ReportLargestDefectSize\r\n', 'MR,#ReportLargestDefectZoneNumber\r\n', 'MR,#ReportPASS\r\n', 'MR,#ReportFAIL\r\n']
    results = []

    # sending result messages to Keyence, then cleaning results to 'human-readable' list
    for msg in result_messages:
        sock.sendall(msg.encode())
        data = sock.recv(32)
        keyence_value_raw = str(data).split('.')
        keyence_value_raw = keyence_value_raw[0].split('+')
        keyence_value = int(keyence_value_raw[1])
        results.append(keyence_value)

    # writing normalized Keyence results to proper PLC tags
    plc.write(
        ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.Defect_Number', results[0]),
        ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.Defect_Size', results[1]),
        ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.DefectZone', results[2]),
        ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.PASS', results[3]),
        ('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.FAIL', results[4]),
    )
    print(f'({machine_num}) PASS = {results[3]} ; FAIL = {results[4]}')
    plc.write('Program:CM080CA0.PorosityInspect.CAM0' + machine_num + '.I.DONE', True)
    print(f'({machine_num}) Keyence Results written to PLC!')

#END keyenceResults_to_PLC



### AFTER 'THE PASTE'

#START main()
def main():
    global current_stage_14 #keeps track of which stage program is currently in from the timing process
    global current_stage_15

    #declaring threads, does not run
    #t1 = threading.Thread(target=TriggerKeyence, args=[sock, 'T1\r\n']) #thread1, PASSing in socket connection and 'T1' keyence command
    #t2 = threading.Thread(target=ExtKeyence, args=[sock, 'TE,0\r\n', 'TE,1\r\n']) #thread2, uses 'TE,0' and 'TE,1' to cancel while scanning and RESET to original state

    # original threading tests
    
    t1 = threading.Thread(target=cycle, args=['1', sock_1, current_stage_14])
    t2 = threading.Thread(target=cycle, args=['2', sock_2, current_stage_15])

    t1_heartbeat = threading.Thread(target=heartbeat, args=['1'])
    t2_heartbeat = threading.Thread(target=heartbeat, args=['2'])

    print("Starting Threads (14 & 15)...")
    t1.start()
    t2.start()
    #t1.join()
    #t2.join() # making sure threads complete before moving forward

    print("Starting Heartbeat Threads (14 & 15)")
    t1_heartbeat.start()
    t2_heartbeat.start()
    

    '''
    p1 = Process(target=cycle, args=('14', sock_14, current_stage_14))
    p1.start()
    p2 = Process(target=cycle, args=('15', sock_15, current_stage_15))
    p2.start()
    p1.join()
    p2.join()
    '''

    #print('This code is beyond the threads!')

#END 'main'

#implicit 'main()' declaration
if __name__ == '__main__':
    main()