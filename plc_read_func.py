from platform import machine
from logging import debug
from pycomm3 import LogixDriver
from pycomm3.cip.data_types import DINT, UINT
import time

#example of just the function to read PLC tags and populate into a dict
## only calling booleans in 'arrayOutTags'

# global variable declarations, some are probably unnecessary(?)
'''
arrayOutTags = [
    'LOAD_PROGRAM',
    'START_PROGRAM',
    'END_PROGRAM',
    'ABORT_PROGRAM',
    'RESET'
    ];
'''
arrayOutTags = [
    'PUN{64}'
    ];

tagKeys = []
for tag in arrayOutTags:
    tagKeys.append(tag.split("{")[0]) # delete trailiing { if it exists

#single-shot read of all 'arrayOutTags' off PLC
def read_plc_dict(machine_num):
    with LogixDriver('120.123.230.39/0') as plc:
        '''
        #print("read_plc_dict, generating list of read tags")
        readList = []
        for tag in arrayOutTags :
            newTag = 'Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.O.' + tag
            #print(newTag)
            readList.append(newTag)
            
        resultsList = plc.read(*readList) # tag, value, type, error
        #print(resultsList)
        readDict = {}

        #print("returned results")
        #print(resultsList)

        for tag in resultsList:
            #print(tag)
            key = tag.tag.split(".")[-1]
            #print(key)
            #print(tag)
            readDict[key] = tag[1]

        #print(readDict)
        return readDict
        '''
        display_1 = plc.read('Program:CM080CA01.PorosityInspect.CAM0' + machine_num + '.O.PUN{64}')
        print(display_1[1])

#END read_plc_dict

print('PUN(1):')
read_plc_dict('1')
print()
print('PUN(2):')
read_plc_dict('2')
print()