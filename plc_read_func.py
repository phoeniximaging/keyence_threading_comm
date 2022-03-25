from platform import machine
from logging import debug
from pycomm3 import LogixDriver
from pycomm3.cip.data_types import DINT, UINT
import time

#example of just the function to read PLC tags and populate into a dict
## only calling booleans in 'arrayOutTags'

# global variable declarations, some are probably unnecessary(?)
arrayOutTags = [
    'LOAD_PROGRAM',
    'START_PROGRAM',
    'END_PROGRAM',
    'ABORT_PROGRAM',
    'RESET'
    ];

tagKeys = []
for tag in arrayOutTags:
    tagKeys.append(tag.split("{")[0]) # delete trailiing { if it exists

#single-shot read of all 'arrayOutTags' off PLC
def read_plc_dict(machine_num):
    with LogixDriver('120.123.230.39/0') as plc:
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
            readDict[key] = tag[1]

        #print(readDict)
        return readDict
#END read_plc_dict

results_dict = {}
results_dict = read_plc_dict('1')

print(results_dict)

