from platform import machine
from logging import debug
from pycomm3 import LogixDriver
from pycomm3.cip.data_types import DINT, UINT
import time

#example of just the function to read PLC tags and populate into a dict
## only calling booleans in 'arrayOutTags'

# global variable declarations, some are probably unnecessary(?)
arrayOutTags = [
    'LoadProgram',
    'StartProgram',
    'EndProgram',
    'AbortProgram',
    'Reset',
    #'PartType',
    #'PartProgram',
    #'ScanNumber',
    #'PUN{64}',
    #'GMPartNumber{8}',
    #'Module',
    #'PlantCode',
    #'Month',
    #'Day',
    #'Year',
    #'Hour',
    #'Minute',
    #'Second',
    #'QualityCheckOP110',
    #'QualityCheckOP120',
    #'QualityCheckOP130',
    #'QualityCheckOP140',
    #'QualityCheckOP150',
    #'QualityCheckOP310',
    #'QualityCheckOP320',
    #'QualityCheckOP330',
    #'QualityCheckOP340',
    #'QualityCheckOP360',
    #'QualityCheckOP370',
    #'QualityCheckOP380',
    #'QualityCheckOP390',
    #'QualityCheckScoutPartTracking',
    #'Heartbeat'
    #'KeyenceFltCode',
    #'PhoenixFltCode'
    ];

tagKeys = []
for tag in arrayOutTags:
    tagKeys.append(tag.split("{")[0]) # delete trailing { if it exists

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


#single-shot read of all 'arrayOutTags' off PLC
def read_plc_dict(machine_num, plc):
    #with LogixDriver('120.57.42.114') as plc:
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
        readDict[key] = tag[1]

    #print(readDict)
    return readDict
#END read_plc_dict

results_dict = {}
changed_flag = False

with LogixDriver('120.57.42.114') as plc:
    while True:
        results_dict = read_plc_dict('14', plc)
        #print(results_dict)
        
        if((results_dict['LoadProgram'] == True) and (changed_flag == False)):
            print('(14) LoadProgram went HIGH!')
            changed_flag = True
        if((results_dict['LoadProgram'] == False) and (changed_flag == True)):
            print('(14) LoadProgram went LOW!')
            changed_flag = False
        

print(results_dict)

