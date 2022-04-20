import threading
import datetime, time
import socket
import csv
from logging import debug
from pycomm3 import LogixDriver
from pycomm3.cip.data_types import DINT, UINT
import json
import os

'''
This is the first testing thread for Elwema using threading and an all-in-one Python program.

Progresses through the timing diagram based on tag values read off Elwema's PLC. Loads and Triggers Keyence.
'''


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
    #'KeyenceFltCode',
    #'PhoenixFltCode'
    ];

tagKeys = []
for tag in arrayOutTags:
    tagKeys.append(tag.split("{")[0]) # delete trailiing { if it exists

#order matters!
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

trigger_count = 0
slow_count = 0
longest_time = 0

current_stage = 0

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect(('192.168.1.83', 8500)) # 'sock' is the connection variable used to communicate with the Keyence
sock.connect(('172.19.145.80', 8500))

lock = threading.Lock()

#single-shot read of all 'arrayOutTags' off PLC
def read_plc_dict(plc, machine_num):
    #print("read_plc_dict, generating list of read tags")
    readList = []
    for tag in arrayOutTags :
        newTag = 'Program:HM1450_VS' + machine_num + '.VPC1.O.' + tag;
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

    end_time = datetime.datetime.now()
    time_diff = (end_time - start_time)
    execution_time = time_diff.total_seconds() * 1000
    print('\'plc.write()\' took %d ms to run' % (execution_time))
    #print("Finished writing PLC...")
    pass
#END write_plc

#used to verify values when writing back to PLC
def protected_ord(value):
    if len(value) > 1:
        print("WRONG Below: ")
        print(value)
        value = value[0]
    #print("Returning:")
    #print(value)
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

#function to translate PLC int-arrays into ASCII str-arrays for OPC
def intArray_to_strArray(intArray):
    #declaring an array of 'str' to hold return value
    strArray = []
    #print(intArray)

    #print()

    #reads each 'int' from array then appends to 'str' array in char form (per element)
    for i in range(len(intArray)):
        strArray.append(chr(intArray[i]))

    #print(strArray)
    return strArray
#END intArray_to_strArray

#function to translate str-arrays into PLC int-arrays
def strArray_to_intArray(strArray):
    #declaring an array of 'int' to hold return value
    intArray = []
    strArray_list = list(strArray)
    #print(strArray_list)
    #print(list(strArray))

    #reads each char from str array then appends to 'intArray' in int form (per element)
    for i in range(len(strArray_list)):
        
        intArray.append(ord(strArray_list[i]))

    return intArray
#END strArray_to_intArray

# Triggering Keyence with socket only being connected/closed ONCE (program startup and shutdown)
def TriggerKeyence(sock, item):

    global trigger_count
    global slow_count
    global longest_time

    message = item
    trigger_start_time = datetime.datetime.now() # marking when 'T1' is sent
    with lock:
        sock.sendall(message.encode())
        data = sock.recv(32)
        print('received "%s"' % data)

    #am I using these right?(!)
    with lock:
        message = 'MR,%Busy\r\n' #initial read of '%Busy' to ensure scan is actually taking place (%Busy == 1)
        sock.sendall(message.encode())
        data = sock.recv(32)
        #print(data)
    trigger_end_time = datetime.datetime.now() # marking when '%Busy' is read off Keyence
    time_diff = (trigger_end_time - trigger_start_time)
    execution_time = time_diff.total_seconds() * 1000
    print(f'\n\'T1\' sent to \'%Busy\' read in: {execution_time} ms')
    if(execution_time > longest_time):
        longest_time = execution_time

    # looping until '%Busy' == 0
    while(data != b'MR,+0000000000.000000\r'):
        # utilizing 'with' to use thread lock
        message = 'MR,%Busy\r\n'
        with lock:
            sock.sendall(message.encode())
            data = sock.recv(32)
        print('TriggerKeyence: received "%s"' % data)
        #print('Scanning...')
        time.sleep(.5)
#END 'TriggerKeyence'

#sends specific Keyence Program (branch) info to pre-load/prepare Keyence for Trigger(T1)
def LoadKeyence(sock, item):
    print('LOADING KEYENCE')
    message = item # keyence message
    with lock:
        sock.sendall(message.encode()) # sending branch info
        print(f'\n\'{item}\' Sent!')
        data = sock.recv(32)
        print('received "%s"' % data)

# sends 'TE,0' then 'TE,1' to the Keyence, resetting to original state (ready for new 'T1')
def ExtKeyence(sock, item, item_reset):
    message = item # setting 'TE,0' first
    with lock:
        sock.sendall(message.encode()) # sending TE,0
        print('\n\'TE,0\' Sent!')

        message = item_reset # setting 'TE,1' to reset
        sock.sendall(message.encode()) # sending, TE,1
        print('\'TE,1\' Sent!')

        #data = sock.recv(32)
        #print('received "%s"' % data)
# END 'ExtKeyence'

#START main()
def main():
    global current_stage #keeps track of which stage program is currently in from the timing process

    print("Connecting to PLC")
    with LogixDriver('120.57.42.114') as plc:
        while(True):
            flipper = 0
            while(True):
                if(flipper == 0):
                    plc.write('Program:HM1450_VS15.VPC1.I.DefectNumber', 1)
                    plc.write('Program:HM1450_VS15.VPC1.I.DefectSize', 0)
                    #print('Busy written FALSE, pausing 5 seconds')
                    print('Write (1)')
                    flipper = 1
                    time.sleep(5)
                else:
                    plc.write('Program:HM1450_VS15.VPC1.I.DefectNumber', 0)
                    plc.write('Program:HM1450_VS15.VPC1.I.DefectSize', 1)
                    #print('Busy written FALSE, pausing 5 seconds')
                    print('Write (1)')
                    flipper = 0
                    time.sleep(5)

            #reading in .csv plc emulator for initial values
            #split into two .csv files, representing each direction of traffic between PLC and Phoenix
            #csv_results = csv_read('o') #holds PHOENIX tags / data
            #csv_results_plc = csv_read('i') #holds PLC (Grob) tags / data
            csv_results = {}

            start_time = datetime.datetime.now()
            results_14_dict = read_plc_dict(plc, '14') #initial PLC tag read for 'robot 14' values
            end_time = datetime.datetime.now()
            time_diff = (end_time - start_time)
            execution_time = time_diff.total_seconds() * 1000
            print('\'read_plc_dict()\' took %d ms to run' % (execution_time))

            write_plc(plc,'14',results_14_dict)

            time.sleep(1000)

            #STAGE0 CHECK HERE
            if(current_stage == 0):
                print('Setting Boolean Flags to Stage 0')
                plc.write(
                ('Program:HM1450_VS14.VPC1.I.Ready', True),
                ('Program:HM1450_VS14.VPC1.I.Busy', False),
                ('Program:HM1450_VS14.VPC1.I.Done', False),
                ('Program:HM1450_VS14.VPC1.I.Pass', False),
                ('Program:HM1450_VS14.VPC1.I.Fail', False)
                )
                while(result_ready[1] != True):
                    print(result_ready)
                    plc.write('Program:HM1450_VS14.VPC1.I.Ready', True)
                    plc.write('Program:HM1450_VS15.VPC1.I.Ready', True)
                    print('Wrote Phoenix(READY) high!')
                    result_ready = plc.read('Program:HM1450_VS14.VPC1.I.Ready')
                    print(result_ready)
                    time.sleep(3)
                print('Stage 0 : Listening for PLC(LOAD_PROGRAM) = 1')
                #reading PLC until LOAD_PROGRAM goes high
                while(results_14_dict['LoadProgram'][1] != True):
                    results_14_dict = read_plc_dict(plc, '14') # continuous PLC read
                    #print(csv_results)
                    time.sleep(1)

                print('PLC(LOAD_PROGRAM) went high!')
                # Once PLC(LOAD_PROGRAM) goes high, mirror data and set Phoenix(READY) high, signifies end of "loading" process
                plc.write('Program:HM1450_VS14.VPC1.I.Ready', False)
                print('Dropping Phoenix(READY) low.')

                ''' 
                *Part Program Table:*
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
                #TODO Send branch data to load Keyence for scan
                LoadKeyence(sock,'MW,#PhoenixControlFaceBranch,' + str(results_14_dict['PartProgram'][1]) + '\r\n') #Keyence loading message, uses PartProgram from PLC to load specific branch
                print('Keyence Loaded!')

                #TODO Actually Mirror Data (write back to PLC)
                print('!Mirroring Data!')
                write_plc(plc,'14',results_14_dict) #writing back mirrored values to PLC to confirm LOAD has been processed / sent to Keyence
                #csv_results['DATA'] = csv_results_plc['DATA']
                time.sleep(1) #artificial pause to see step happening in testing
                print('Data Mirrored, Setting \'READY\' high')
                plc.write('Program:HM1450_VS14.VPC1.I.Ready', True)
                time.sleep(3)
                current_stage += 1 #incrementing out of STAGE0
            #END STAGE0
            #START STAGE1 : START/END Program
            elif(current_stage == 1):
                print('Stage 1!\nListening for PLC(START_PROGRAM) = 1')
                time.sleep(.01) #10ms artificial delay for testing
                if(results_14_dict['StartProgram'][1] == True):
                    print('PLC(START_PROGRAM) went high! Time to trigger Keyence...')
                    plc.write('Program:HM1450_VS14.VPC1.I.Busy', True) #Busy goes HIGH while Keyence is scanning

                    #Actual Keyence Trigger (T1) here***
                    TriggerKeyence(sock, 'T1\r\n')

                    print('Pretend scan ended! PHOENIX(BUSY) is low')
                    plc.write('Program:HM1450_VS14.VPC1.I.Busy', False)

                    #TODO PASS/FAIL RESULTS
                    print('PASS/FAIL/DONE data written out')
                    plc.write(
                        ('Program:HM1450_VS14.VPC1.I.Pass', True),
                        ('Program:HM1450_VS14.VPC1.I.Done', True)
                    )
                    print('PHOENIX(PASS) and PHOENIX(DONE) = 1')
                    print('Stage 1 Complete!')
                    current_stage += 1
                    time.sleep(1)
                
            #Final Stage, reset to Stage 0 once PLC(END_PROGRAM) and PHOENIX(DONE) have been set low
            elif(current_stage == 2):
                done_check = plc.read('Program:HM1450_VS14.VPC1.I.Done')
                print('Stage 2 : Listening to PLC(END_PROGRAM) low to reset back to Stage 0')
                if(results_14_dict['EndProgram'][1] == True):
                    print('PLC(END_PROGRAM) is high. Dropping PHOENIX(DONE) low')
                    plc.write('Program:HM1450_VS14.VPC1.I.Done', False)
                    
                if(results_14_dict['EndProgram'][1] == False and done_check[1] == False):
                    print('PLC(END_PROGRAM) is low. Resetting PHOENIX to Stage 0')
                    current_stage = 0 # cycle complete, reset to stage 0
                
                time.sleep(1)


    #BEGIN THREADING TRIGGER KEYENCE
    #declaring threads, does not run
    t1 = threading.Thread(target=TriggerKeyence, args=[sock, 'T1\r\n']) #thread1, passing in socket connection and 'T1' keyence command
    t2 = threading.Thread(target=ExtKeyence, args=[sock, 'TE,0\r\n', 'TE,1\r\n']) #thread2, uses 'TE,0' and 'TE,1' to cancel while scanning and reset to original state

    #starting threads
    t1.start()
    #t1.join() #'join' locks until the thread has processed (?)

    #waits 10 seconds while 'T1' starts / is scanning
    for x in range (10):
        print(x)
        time.sleep(1)

    # starts second thread to send 'TE,0' and 'TE,1' to Keyence, cancelling the current scan in progress and resetting Keyence to a state that will accept a new 'T1'
    t2.start()
    t2.join() #! will this keep thread ordered between calls to main()?

    print(f'\n*Longest Time*: {longest_time}\n')
    #print('End main()')
#END 'main'

#implicit 'main()' declaration
if __name__ == '__main__':
    for x in range(1000):
        print(f'Main Loop {x}')
        main()
        #time.sleep(3) # time between cycles to eyeball if multiple scans are actually taking place