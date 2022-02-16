from logging import debug
from pycomm3 import LogixDriver

import asyncio
import time
import datetime
#from asyncua import Client, Node, ua
import json
import os
import sys

from random import randrange

from pycomm3.cip.data_types import DINT, UINT
import socket

#global vars
retries = 0
debug_msgs = False
exception_count = 0

ready14_OLD = False
ready15_OLD = False


arrayOutTags = [
    'LOAD_PROGRAM',
    'START_PROGRAM',
    'END_PROGRAM',
    'ABORT_PROGRAM',
    'RESET',
    'PART_TYPE',
    'PART_PROGRAM',
    'PUN{64}',
    'MODULE',
    'PLANTCODE',
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
    'PART_PROGRAM'
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



def read_plc(plc, machine_num):
    results = plc.read('Program:HM1450_VS' + machine_num + '.VPC1.O.LoadProgram',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.StartProgram',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.EndProgram',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.AbortProgram',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.Reset',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.PartType',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.PartProgram',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.ScanNumber',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.PUN{64}',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.GMPartNumber{8}',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.Module',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.PlantCode',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.Month',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.Day',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.Year',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.Hour',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.Minute',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.Second',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.QualityCheckOP110',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.QualityCheckOP120',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.QualityCheckOP130',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.QualityCheckOP140',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.QualityCheckOP150',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.QualityCheckOP310',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.QualityCheckOP320',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.QualityCheckOP330',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.QualityCheckOP340',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.QualityCheckOP360',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.QualityCheckOP370',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.QualityCheckOP380',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.QualityCheckOP390',
        'Program:HM1450_VS' + machine_num + '.VPC1.O.QualityCheckScoutPartTracking'
    )

    return results
#end 'read_plc'


#singleton to connect to OPC server and assign variables
#filles dictionary 'opc_variables' with ALL our relevant OPC tags
def connect_opc(client):
    #url = opc_server_ip

    #client = Client(url=url)
    #with Client(url=url) as client:

    uri = 'http://phoeniximaging.com'
    idx = client.get_namespace_index(uri)

    opc_variables = {
    ###############
    # '.VPC1.O' OPC tags
    ###############
    'LoadProgram_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.LoadProgram"]),
    'LoadProgram_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.LoadProgram"]),
    
    'StartProgram_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.StartProgram"]),
    'StartProgram_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.StartProgram"]),

    'EndProgram_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.EndProgram"]),
    'EndProgram_15o' :client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.EndProgram"]),
    
    'AbortProgram_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.AbortProgram"]),
    'AbortProgram_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.AbortProgram"]),

    'Reset_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.Reset"]),
    'Reset_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.Reset"]),
    
    #DINT are read literally from PLC
    
    'PartType_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.PartType"]),
    'PartType_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.PartType"]),

    'PartProgram_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.PartProgram"]),
    'PartProgram_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.PartProgram"]),

    'ScanNumber_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.ScanNumber"]),
    'ScanNumber_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.ScanNumber"]),

    'PUN_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.PUN"]),
    'PUN_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.PUN"]),

    'GMPartNumber_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.GMPartNumber"]),
    'GMPartNumber_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.GMPartNumber"]),

    'Module_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.Module"]),
    'Module_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.Module"]),

    #requires 'chr' casting to go from PLC(int) to 'human-readable'
    'PlantCode_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.PlantCode"]),
    'PlantCode_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.PlantCode"]),
    
    'Month_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.Month"]),
    'Month_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.Month"]),

    'Day_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.Day"]),
    'Day_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.Day"]),

    'Year_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.Year"]),
    'Year_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.Year"]),

    'Hour_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.Hour"]),
    'Hour_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.Hour"]),

    'Minute_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.Minute"]),
    'Minute_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.Minute"]),

    'Second_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.Second"]),
    'Second_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.Second"]),

    'QualityCheckOP110_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.QualityCheckOP110"]),
    'QualityCheckOP110_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.QualityCheckOP110"]),

    'QualityCheckOP120_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.QualityCheckOP120"]),
    'QualityCheckOP120_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.QualityCheckOP120"]),

    'QualityCheckOP130_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.QualityCheckOP130"]),
    'QualityCheckOP130_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.QualityCheckOP130"]),

    'QualityCheckOP140_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.QualityCheckOP140"]),
    'QualityCheckOP140_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.QualityCheckOP140"]),

    'QualityCheckOP150_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.QualityCheckOP150"]),
    'QualityCheckOP150_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.QualityCheckOP150"]),

    'QualityCheckOP310_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.QualityCheckOP310"]),
    'QualityCheckOP310_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.QualityCheckOP310"]),

    'QualityCheckOP320_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.QualityCheckOP320"]),
    'QualityCheckOP320_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.QualityCheckOP320"]),

    'QualityCheckOP330_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.QualityCheckOP330"]),
    'QualityCheckOP330_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.QualityCheckOP330"]),

    'QualityCheckOP340_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.QualityCheckOP340"]),
    'QualityCheckOP340_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.QualityCheckOP340"]),

    'QualityCheckOP360_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.QualityCheckOP360"]),
    'QualityCheckOP360_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.QualityCheckOP360"]),

    'QualityCheckOP370_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.QualityCheckOP370"]),
    'QualityCheckOP370_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.QualityCheckOP370"]),

    'QualityCheckOP380_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.QualityCheckOP380"]),
    'QualityCheckOP380_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.QualityCheckOP380"]),

    'QualityCheckOP390_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.QualityCheckOP390"]),
    'QualityCheckOP390_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.QualityCheckOP390"]),

    'QualityCheckScoutPartTracking_14o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.O.QualityCheckScoutPartTracking"]),
    'QualityCheckScoutPartTracking_15o' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.O.QualityCheckScoutPartTracking"]),

    ######################
    # End of '.VPC1.O' OPC tags
    ######################

    ######################
    # Start '.VPC1.I' OPC tags
    ######################

    #print("I.Read: " + str(plc.read('Program:HM1450_VS' + machine_num + '.VPC1.I.Ready'))) #outputs for testing
    'Ready_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.Ready"]),
    'Ready_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.Ready"]),
    'Busy_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.Busy"]),
    'Busy_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.Busy"]),
    'Done_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.Done"]),
    'Done_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.Done"]),
    'Pass_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.Pass"]),
    'Pass_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.Pass"]),
    'Fail_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.Fail"]),
    'Fail_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.Fail"]),
    'Faulted_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.Faulted"]),
    'Faulted_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.Faulted"]),

    'PartType_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.PartType"]),
    'PartType_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.PartType"]),

    'PartProgram_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.PartProgram"]),
    'PartProgram_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.PartProgram"]),
    'ScanNumber_14i'  : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.ScanNumber"]),
    'ScanNumber_15i'  : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.ScanNumber"]),

    'KeyenceFault_14i'  : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.KeyenceFault"]),
    'KeyenceFault_15i'  : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.KeyenceFault"]),

    'PhoenixFault_14i'  : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.PhoenixFault"]),
    'PhoenixFault_15i'  : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.PhoenixFault"]),

    'PUN_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.PUN"]),
    'PUN_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.PUN"]),

    'GMPartNumber_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.GMPartNumber"]),
    'GMPartNumber_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.GMPartNumber"]),

    'Module_14i'   : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.Module"]),
    'Module_15i'   : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.Module"]),
    'PlantCode_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.PlantCode"]),
    'PlantCode_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.PlantCode"]),
    
    'Month_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.Month"]),
    'Month_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.Month"]),
    'Day_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.Day"]),
    'Day_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.Day"]),
    'Year_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.Year"]),
    'Year_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.Year"]),
    'Hour_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.Hour"]),
    'Hour_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.Hour"]),
    'Minute_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.Minute"]),
    'Minute_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.Minute"]),
    'Second_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.Second"]),
    'Second_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.Second"]),
    'QualityCheckOP110_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.QualityCheckOP110"]),
    'QualityCheckOP110_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.QualityCheckOP110"]),
    'QualityCheckOP120_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.QualityCheckOP120"]),
    'QualityCheckOP120_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.QualityCheckOP120"]),
    'QualityCheckOP130_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.QualityCheckOP130"]),
    'QualityCheckOP130_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.QualityCheckOP130"]),
    'QualityCheckOP140_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.QualityCheckOP140"]),
    'QualityCheckOP140_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.QualityCheckOP140"]),
    'QualityCheckOP150_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.QualityCheckOP150"]),
    'QualityCheckOP150_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.QualityCheckOP150"]),
    'QualityCheckOP310_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.QualityCheckOP310"]),
    'QualityCheckOP310_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.QualityCheckOP310"]),
    'QualityCheckOP320_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.QualityCheckOP320"]),
    'QualityCheckOP320_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.QualityCheckOP320"]),
    'QualityCheckOP330_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.QualityCheckOP330"]),
    'QualityCheckOP330_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.QualityCheckOP330"]),
    'QualityCheckOP340_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.QualityCheckOP340"]),
    'QualityCheckOP340_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.QualityCheckOP340"]),
    'QualityCheckOP360_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.QualityCheckOP360"]),
    'QualityCheckOP360_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.QualityCheckOP360"]),
    'QualityCheckOP370_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.QualityCheckOP370"]),
    'QualityCheckOP370_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.QualityCheckOP370"]),
    'QualityCheckOP380_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.QualityCheckOP380"]),
    'QualityCheckOP380_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.QualityCheckOP380"]),
    'QualityCheckOP390_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.QualityCheckOP390"]),
    'QualityCheckOP390_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.QualityCheckOP390"]),
    'QualityCheckScoutPartTracking_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.QualityCheckScoutPartTracking"]),
    'QualityCheckScoutPartTracking_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.QualityCheckScoutPartTracking"]),
    'DefectNumber_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.DefectNumber"]),
    'DefectNumber_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.DefectNumber"]),
    'DefectSize_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.DefectSize"]),
    'DefectSize_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.DefectSize"]),
    'DefectZone_14i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS14", f"{idx}:VPC1.I.DefectZone"]),
    'DefectZone_15i' : client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS15", f"{idx}:VPC1.I.DefectZone"])

    }

    #######################
    # End of '.VPC1.I' OPC tags
    #######################

    #returning dictionary of all 14/15 .I/.O
    return opc_variables
#end 'connect_opc'


#writing '.VPC1.I' vars from OPC to PLC
#If I could optimize this: I'd create a set of 2/3 dictionaries to map OPC/PLC and vice-versa
def write_plc(plc, client, machine_num, opc_variables):
    #url = opc_server_ip

    #print("Writing \'.VPC1.I\' variable values from OPC to PLC")

    #PLC connection / variable
    #with LogixDriver(plc_ip) as plc:
    #OPC connection / variable
    #print("Connected to PLC...")
    #with Client(url=url) as client:
    uri = 'http://phoeniximaging.com'
    idx = client.get_namespace_index(uri)

    
    #START HERE W/ NEW DICT
    #print("I.Read: " + str(plc.read('Program:HM1450_VS' + machine_num + '.VPC1.I.Ready'))) #outputs for testing
    #plc_Ready    = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.I.Ready"])

    #print(plc_Ready.get_value())

    #async uses 'read_value', sync uses 'get_value'
    #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Ready', plc_Ready.read_value())
    #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Ready', opc_variables['Ready_' + machine_num + 'i'].get_value())

    #print("I.Read: " + str(plc.read('Program:HM1450_VS' + machine_num + '.VPC1.I.Ready')))
    #plc_Busy    = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.I.Busy"])
    #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Busy', opc_variables['Busy_' + machine_num + 'i'].get_value())

    #plc_Done    = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.I.Done"])
    #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Done', opc_variables['Done_' + machine_num + 'i'].get_value())

    #plc_Pass    = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.I.Pass"])
    #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Pass', opc_variables['Pass_' + machine_num + 'i'].get_value())

    #plc_Fail    = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.I.Fail"])
    #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Fail', opc_variables['Fail_' + machine_num + 'i'].get_value())

    #plc_Faulted    = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.I.Faulted"])
    #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.Faulted', opc_variables['Faulted_' + machine_num + 'i'].get_value())

    
    
    # DINT read/write literally between PLC/OPC
    #plc_PartType    = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.I.PartType"])
    #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.PartType', opc_variables['PartType_' + machine_num + 'i'].get_value())

    #print(ord(await plc_PartType.get_value()))
    #plc_PartProgram = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.I.PartProgram"])
    #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.PartProgram', opc_variables['PartProgram_' + machine_num + 'i'].get_value())

    #plc_ScanNumber  = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.I.ScanNumber"])
    #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.ScanNumber', opc_variables['ScanNumber_' + machine_num + 'i'].get_value())

    

    #'PUN' and 'GMPartNumber' require additional translation from ASCII-to-INT to write back to PLC in int[] form
    #plc_PUN         = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.I.PUN"])
    #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.PUN', await plc_PUN.read_value())
    #print("plc_PUN: ")
    #print(await plc_PUN.read_value())
    #print()

    #the 'PUN' tags requires string-to-int64[] conversion to write to the PLC
    #plc_PUN_int = []
    plc_PUN_int = opc_variables['PUN_' + machine_num + 'i'].get_value()
    #print(plc_PUN_int)
    #converts a string into an array of ASCII int64 values
    plc_PUN_int = strArray_to_intArray(plc_PUN_int)
    #print(plc_PUN_int)
    #appending NULL values to fill out plc_PUN_int array[64]
    for i in range(len(plc_PUN_int), 64):
            #None = NULL in Python
            #plc_PUN_int.append(None)
            plc_PUN_int.append(0) #? Maybe won't write because 'None' is a different type than 'int'
            #plc_PUN_int[i] = None

    #print()
    #writing the int64[] to the PLC
    #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.PUN{64}', plc_PUN_int)

    
    #print()
    #Example of how to use conversion function w/ an OPC-read value
    #print(await intArray_to_strArray(int(await plc_PUN.read_value())))

    #requires 'I.GMPartNumber' to be set with 8-characters, part of the dotnet-opc-client's 'copy'
    #plc_GMPartNumber= client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.I.GMPartNumber"])
    #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.GMPartNumber', await plc_GMPartNumber.read_value())
    plc_GMPartNumber_int = opc_variables['GMPartNumber_' + machine_num + 'i'].get_value()
    #print(plc_GMPartNumber_int)
    plc_GMPartNumber_int = strArray_to_intArray(plc_GMPartNumber_int)
    #print(plc_GMPartNumber_int)
    #print()
    #plc.write('Program:HM1450_VS' + machine_num + '.VPC1.I.GMPartNumber{8}', plc_GMPartNumber_int)

    #the mightiest of PLC '.write' commands

    #GET_VALUES TESTING HERE
    '''
    (opc_variables['Ready_' + machine_num + 'i'],
    opc_variables['Busy_' + machine_num + 'i'],
    opc_variables['Done_' + machine_num + 'i'],
    opc_variables['Pass_' + machine_num + 'i'],
    opc_variables['Fail_' + machine_num + 'i'],
    opc_variables['Faulted_' + machine_num + 'i'],
    opc_variables['PartType_' + machine_num + 'i'],
    opc_variables['PartProgram_' + machine_num + 'i'],
    opc_variables['ScanNumber_' + machine_num + 'i'],
    plc_PUN_int,
    plc_GMPartNumber_int,
    protected_ord(opc_variables['Module_' + machine_num + 'i']),
    protected_ord(str(opc_variables['PlantCode_' + machine_num + 'i'])),
    int(opc_variables['Month_' + machine_num + 'i']),
    int(opc_variables['Day_' + machine_num + 'i']),
    int(opc_variables['Year_' + machine_num + 'i']),
    int(opc_variables['Hour_' + machine_num + 'i']),
    int(opc_variables['Minute_' + machine_num + 'i']),
    int(opc_variables['Second_' + machine_num + 'i']),
    protected_ord(opc_variables['QualityCheckOP110_' + machine_num + 'i']),
    protected_ord(opc_variables['QualityCheckOP120_' + machine_num + 'i']),
    protected_ord(opc_variables['QualityCheckOP130_' + machine_num + 'i']),
    protected_ord(opc_variables['QualityCheckOP140_' + machine_num + 'i']),
    protected_ord(opc_variables['QualityCheckOP150_' + machine_num + 'i']),
    protected_ord(opc_variables['QualityCheckOP310_' + machine_num + 'i']),
    protected_ord(opc_variables['QualityCheckOP320_' + machine_num + 'i']),
    protected_ord(opc_variables['QualityCheckOP330_' + machine_num + 'i']),
    protected_ord(opc_variables['QualityCheckOP340_' + machine_num + 'i']),
    protected_ord(opc_variables['QualityCheckOP360_' + machine_num + 'i']),
    protected_ord(opc_variables['QualityCheckOP370_' + machine_num + 'i']),
    protected_ord(opc_variables['QualityCheckOP380_' + machine_num + 'i']),
    protected_ord(opc_variables['QualityCheckOP390_' + machine_num + 'i']),
    protected_ord(opc_variables['QualityCheckScoutPartTracking_' + machine_num + 'i']),
    int(opc_variables['DefectNumber_' + machine_num + 'i']),
    int(opc_variables['DefectSize_' + machine_num + 'i']),
    int(opc_variables['DefectZone_' + machine_num + 'i']),
    int(opc_variables['PhoenixFault_' + machine_num + 'i']),
    int(opc_variables['KeyenceFault_' + machine_num + 'i'])
    )
    '''
    
    #logging how long the 'read' takes
    start_time = datetime.datetime.now()

    opc_snapshot = client.get_values((opc_variables['Ready_' + machine_num + 'i'], 
    opc_variables['Busy_' + machine_num + 'i'],
    opc_variables['Done_' + machine_num + 'i'],
    opc_variables['Pass_' + machine_num + 'i'],
    opc_variables['Fail_' + machine_num + 'i'],
    opc_variables['Faulted_' + machine_num + 'i'],
    opc_variables['PartType_' + machine_num + 'i'],
    opc_variables['PartProgram_' + machine_num + 'i'],
    opc_variables['ScanNumber_' + machine_num + 'i'],
    opc_variables['PUN_' + machine_num + 'i'],
    opc_variables['GMPartNumber_' + machine_num + 'i'],
    opc_variables['Module_' + machine_num + 'i'],
    opc_variables['PlantCode_' + machine_num + 'i'],
    opc_variables['Month_' + machine_num + 'i'],
    opc_variables['Day_' + machine_num + 'i'],
    opc_variables['Year_' + machine_num + 'i'],
    opc_variables['Hour_' + machine_num + 'i'],
    opc_variables['Minute_' + machine_num + 'i'],
    opc_variables['Second_' + machine_num + 'i'],
    opc_variables['QualityCheckOP110_' + machine_num + 'i'],
    opc_variables['QualityCheckOP120_' + machine_num + 'i'],
    opc_variables['QualityCheckOP130_' + machine_num + 'i'],
    opc_variables['QualityCheckOP140_' + machine_num + 'i'],
    opc_variables['QualityCheckOP150_' + machine_num + 'i'],
    opc_variables['QualityCheckOP310_' + machine_num + 'i'],
    opc_variables['QualityCheckOP320_' + machine_num + 'i'],
    opc_variables['QualityCheckOP330_' + machine_num + 'i'],
    opc_variables['QualityCheckOP340_' + machine_num + 'i'],
    opc_variables['QualityCheckOP360_' + machine_num + 'i'],
    opc_variables['QualityCheckOP370_' + machine_num + 'i'],
    opc_variables['QualityCheckOP380_' + machine_num + 'i'],
    opc_variables['QualityCheckOP390_' + machine_num + 'i'],
    opc_variables['QualityCheckScoutPartTracking_' + machine_num + 'i'],
    opc_variables['DefectNumber_' + machine_num + 'i'],
    opc_variables['DefectSize_' + machine_num + 'i'],
    opc_variables['DefectZone_' + machine_num + 'i'],
    opc_variables['PhoenixFault_' + machine_num + 'i'],
    opc_variables['KeyenceFault_' + machine_num + 'i'])
    )

    end_time = datetime.datetime.now()
    time_diff = (end_time - start_time)
    execution_time = time_diff.total_seconds() * 1000
    print('\'client.get_values()\' took %d ms to run' % (execution_time))

    plc_PUN_int = opc_snapshot[9]
    #print(plc_PUN_int)
    #converts a string into an array of ASCII int64 values
    plc_PUN_int = strArray_to_intArray(plc_PUN_int)
    #print(plc_PUN_int)
    #appending NULL values to fill out plc_PUN_int array[64]
    for i in range(len(plc_PUN_int), 64):
            #None = NULL in Python
            #plc_PUN_int.append(None)
            plc_PUN_int.append(0) #? Maybe won't write because 'None' is a different type than 'int'
            #plc_PUN_int[i] = None

    plc_GMPartNumber_int = opc_snapshot[10]
    #print(plc_GMPartNumber_int)
    plc_GMPartNumber_int = strArray_to_intArray(plc_GMPartNumber_int)

    #print(opc_snapshot)
    #time.sleep(5)
    

    #logging how long the 'read' takes
    start_time = datetime.datetime.now()

    plc.write(('Program:HM1450_VS' + machine_num + '.VPC1.I.Ready', opc_snapshot[0]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Busy', opc_snapshot[1]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Done', opc_snapshot[2]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Pass', opc_snapshot[3]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Fail', opc_snapshot[4]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Faulted', opc_snapshot[5]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PartType', opc_snapshot[6]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PartProgram', opc_snapshot[7]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.ScanNumber', opc_snapshot[8]),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PUN{64}', plc_PUN_int),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.GMPartNumber{8}', plc_GMPartNumber_int),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Module', protected_ord(opc_snapshot[11])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PlantCode', protected_ord(str(opc_snapshot[12]))),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Month', int(opc_snapshot[13])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Day', int(opc_snapshot[14])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Year', int(opc_snapshot[15])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Hour', int(opc_snapshot[16])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Minute', int(opc_snapshot[17])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.Second', int(opc_snapshot[18])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP110', protected_ord(opc_snapshot[19])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP120', protected_ord(opc_snapshot[20])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP130', protected_ord(opc_snapshot[21])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP140', protected_ord(opc_snapshot[22])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP150', protected_ord(opc_snapshot[23])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP310', protected_ord(opc_snapshot[24])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP320', protected_ord(opc_snapshot[25])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP330', protected_ord(opc_snapshot[26])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP340', protected_ord(opc_snapshot[27])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP360', protected_ord(opc_snapshot[28])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP370', protected_ord(opc_snapshot[29])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP380', protected_ord(opc_snapshot[30])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckOP390', protected_ord(opc_snapshot[31])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.QualityCheckScoutPartTracking', protected_ord(opc_snapshot[32])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.DefectNumber', int(opc_snapshot[33])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.DefectSize', int(opc_snapshot[34])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.DefectZone', int(opc_snapshot[35])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.PhoenixFltCode', int(opc_snapshot[36])),
    ('Program:HM1450_VS' + machine_num + '.VPC1.I.KeyenceFltCode', int(opc_snapshot[37]))
    )

    end_time = datetime.datetime.now()
    time_diff = (end_time - start_time)
    execution_time = time_diff.total_seconds() * 1000
    print('\'plc.write()\' took %d ms to run' % (execution_time))

    #print("Finished writing PLC...")
    #client.close_session

    pass

def plc_write_shim(plc, client, machine_num, opc_variables):
    write_plc(plc, client, machine_num, opc_variables)

def protected_ord(value):
    if len(value) > 1:
        print("WRONG Below: ")
        print(value)
        value = value[0]
    #print("Returning:")
    #print(value)
    return ord(value)

'''
def opc_write_value(client, idx, machine_num, key, value, datatype):
    opc_from_plc = client.nodes.root.get_child(["0:Objects", 
        f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O." + key])
    opc_from_plc.set_value(value, datatype)
'''

#function to bulk write PLC values to OPC serve
#necessary?
#def opc_write_values(client, machine_num, key, value, datatype, opc_variables, opc_translated_values):
def opc_write_values(client, machine_num, opc_variables, opc_translated_values):

    uri = 'http://phoeniximaging.com'
    idx = client.get_namespace_index(uri)

    #print(opc_translated_values['PartType'])
    #print(type(opc_translated_values['PartType'][1]))
    #time.sleep(1)

    #elif isinstance(val, ua.Variant):
    #ua.Variant(val, varianttype)t

    #THIS WORKS as a value inside the BULK writes if data-type needs to be specified
    #PartType_variant = ua.Variant(opc_translated_values['PartType'][1], ua.VariantType.UInt32)

    client.set_values([opc_variables['PartType_' + machine_num + 'o'],
        opc_variables['PartProgram_' + machine_num + 'o'],
        opc_variables['ScanNumber_' + machine_num + 'o'],
        opc_variables['PUN_' + machine_num + 'o'],
        opc_variables['GMPartNumber_' + machine_num + 'o'],
        opc_variables['Module_' + machine_num + 'o'],
        opc_variables['PlantCode_' + machine_num + 'o'],
        opc_variables['Month_' + machine_num + 'o'],
        opc_variables['Day_' + machine_num + 'o'],
        opc_variables['Year_' + machine_num + 'o'],
        opc_variables['Hour_' + machine_num + 'o'],
        opc_variables['Minute_' + machine_num + 'o'],
        opc_variables['Second_' + machine_num + 'o'],
        opc_variables['QualityCheckOP110_' + machine_num + 'o'], 
        opc_variables['QualityCheckOP120_' + machine_num + 'o'],
        opc_variables['QualityCheckOP130_' + machine_num + 'o'],
        opc_variables['QualityCheckOP140_' + machine_num + 'o'],
        opc_variables['QualityCheckOP150_' + machine_num + 'o'],
        opc_variables['QualityCheckOP310_' + machine_num + 'o'],
        opc_variables['QualityCheckOP320_' + machine_num + 'o'],
        opc_variables['QualityCheckOP330_' + machine_num + 'o'],
        opc_variables['QualityCheckOP340_' + machine_num + 'o'],
        opc_variables['QualityCheckOP360_' + machine_num + 'o'],
        opc_variables['QualityCheckOP370_' + machine_num + 'o'],
        opc_variables['QualityCheckOP380_' + machine_num + 'o'],
        opc_variables['QualityCheckOP390_' + machine_num + 'o'],
        opc_variables['QualityCheckScoutPartTracking_' + machine_num + 'o'],
        opc_variables['LoadProgram_' + machine_num + 'o'],
        opc_variables['StartProgram_' + machine_num + 'o'],
        opc_variables['EndProgram_' + machine_num + 'o'],
        opc_variables['AbortProgram_' + machine_num + 'o'],
        opc_variables['Reset_' + machine_num + 'o'],
        
        ],

        [ua.Variant(opc_translated_values['PartType'][1], ua.VariantType.UInt32),
        ua.Variant(opc_translated_values['PartProgram'][1], ua.VariantType.UInt32),
        ua.Variant(opc_translated_values['ScanNumber'][1], ua.VariantType.UInt32),
        ua.Variant(opc_translated_values['PUN'], ua.VariantType.String),
        ua.Variant(opc_translated_values['GMPartNumber'], ua.VariantType.String),
        ua.Variant(opc_translated_values['Module'], ua.VariantType.String),
        ua.Variant(opc_translated_values['PlantCode'], ua.VariantType.String),
        ua.Variant(opc_translated_values['Month'][1], ua.VariantType.UInt32),
        ua.Variant(opc_translated_values['Day'][1], ua.VariantType.UInt32),
        ua.Variant(opc_translated_values['Year'][1], ua.VariantType.UInt32),
        ua.Variant(opc_translated_values['Hour'][1], ua.VariantType.UInt32),
        ua.Variant(opc_translated_values['Minute'][1], ua.VariantType.UInt32),
        ua.Variant(opc_translated_values['Second'][1], ua.VariantType.UInt32),
        ua.Variant(opc_translated_values['QualityCheckOP110'], ua.VariantType.String), 
        ua.Variant(opc_translated_values['QualityCheckOP120'], ua.VariantType.String),
        ua.Variant(opc_translated_values['QualityCheckOP130'], ua.VariantType.String),
        ua.Variant(opc_translated_values['QualityCheckOP140'], ua.VariantType.String),
        ua.Variant(opc_translated_values['QualityCheckOP150'], ua.VariantType.String),
        ua.Variant(opc_translated_values['QualityCheckOP310'], ua.VariantType.String),
        ua.Variant(opc_translated_values['QualityCheckOP320'], ua.VariantType.String),
        ua.Variant(opc_translated_values['QualityCheckOP330'], ua.VariantType.String),
        ua.Variant(opc_translated_values['QualityCheckOP340'], ua.VariantType.String),
        ua.Variant(opc_translated_values['QualityCheckOP360'], ua.VariantType.String),
        ua.Variant(opc_translated_values['QualityCheckOP370'], ua.VariantType.String),
        ua.Variant(opc_translated_values['QualityCheckOP380'], ua.VariantType.String),
        ua.Variant(opc_translated_values['QualityCheckOP390'], ua.VariantType.String),
        ua.Variant(opc_translated_values['QualityCheckScoutPartTracking'], ua.VariantType.String),
        ua.Variant(opc_translated_values['LoadProgram'], ua.VariantType.Boolean),
        ua.Variant(opc_translated_values['StartProgram'], ua.VariantType.Boolean),
        ua.Variant(opc_translated_values['EndProgram'], ua.VariantType.Boolean),
        ua.Variant(opc_translated_values['AbortProgram'], ua.VariantType.Boolean),
        ua.Variant(opc_translated_values['Reset'], ua.VariantType.Boolean)

        ])

    #print("Great success!")




def write_opc_dict(plc_read_dict, client, machine_num, debug_msgs):

    #dictionary to hold all processed information, allowing bulk write
    opc_translated_values = {}

    #url = opc_server_ip
    if debug_msgs == True:
        print("Writing to OPC...")
    #print(url)
    #with Client(url=url) as client:
    #print("Connected to OPC")
    uri = 'http://phoeniximaging.com'
    idx = client.get_namespace_index(uri)

    #print("writing cmd")
    for key in tagCmds:
        value = plc_read_dict[key].value
        #confirming datatype of 'cmd' variables, should be type 'bool'
        if type(value) == bool:
            value = bool(plc_read_dict[key].value)
            #print("Writing cmd key: " + key + " => " + str(value))
        else:
            value = False
            #if debug_msgs == True:
            #    print("Invalid Value for: " + key + "...setting to \'False\'")

        #populating dictionary full of processed values
        opc_translated_values[key] = value
        #print(opc_translated_values)
        #opc_write_value(client, idx, machine_num, key, value, ua.VariantType.Boolean)


    #opc_variables['Month_' + machine_num + 'o'].set_value(plc_read_results[12].value, ua.VariantType.UInt32)
    for key in tagDateTime:
        #value = ua.Variant(Value=plc_read_dict[key].value, VariantType=ua.VariantType.UInt32)
        value = plc_read_dict[key]
        #confirming datatype of 'DateTime' variables, should be some form of integer
        if type(value) == int or DINT or UINT:
            #print(value[1])
            #print("Writing date-time key: " + key + " => " + str(value[1]))
            pass
        else:
            value = 0
            #if debug_msgs == True:
            #    print("Invalid Value for: " + key + "...setting to 0")
        opc_translated_values[key] = value
        #opc_write_value(client, idx, machine_num, key, value[1], ua.VariantType.UInt32)

        #CHUCKS SOLUTION **********************************************************************
        #writeNodeList.append(opc_variables[key])
        #writeVariantList.append(ua.Variant(value[1], ua.VariantType.UInt32))

    for key in tagInt:
        #value = ua.Variant(Value=plc_read_dict[key].value, VariantType=ua.VariantType.UInt32)
        value = plc_read_dict[key]
        #confirming datatype of 'Int' variables, should be some form of integer (same as DateTime)
        if type(value) == int or DINT or UINT:
            #print("Writing int key: " + key + " => " + str(value[1]))
            pass
        else:
            #if debug_msgs == True:
            #    print("Invalid Value for: " + key + " (" + str(value) + ")...setting to 0")
            value = 0
        opc_translated_values[key] = value
        #opc_write_value(client, idx, machine_num, key, value[1], ua.VariantType.UInt32)

    #writing to OPC as 'chr', translates from PLC (int) to 'human-readable' form
    for key in tagChar:
        value = plc_read_dict[key].value
        #if DECIMAL value is between 33 and 126, this is a valid character in ASCII
        if 33 <= value <= 126:
            value = chr(plc_read_dict[key].value)
            #print("Writing char key: " + key + " => " + str(value))
        else:
            #if debug_msgs == True:
            #    print("Invalid Value for: " + key + " (" + str(value) + ")...setting to \'!\'")
            value = '!'
        opc_translated_values[key] = value
        #opc_write_value(client, idx, machine_num, key, value, ua.VariantType.String)

    #'PUN' and 'GMPartNumber' are read from the PLC as an array of INT but 
    # need to be translated (to ASCII) then concatenated into a singular string for the OPC
    for key in tagStringInt:
        value_dec = plc_read_dict[key].value
        #print(value_dec[0])
        #print(type(value_dec[0]))
        value = intArray_to_str(plc_read_dict[key].value)
        #print(key)
        #print(value)
        if (len(value) == 8 or 64) and (33 <= value_dec[0] <= 126):
            #print("Writing string key: " + key + " => " + str(value))
            #value = str(value)
            pass
        else:
            #if debug_msgs == True:
            #    print("Invalid Value for: " + key + " (" + str(value) + ")...setting to \'!\'")
            value = '!'
        opc_translated_values[key] = value
        #opc_write_value(client, idx, machine_num, key, value, ua.VariantType.String)

    #print(opc_translated_values)
    return opc_translated_values

#function to translate PLC int-arrays into ASCII str for OPC
def intArray_to_str(intArray):
    strReturn = ""
    #print(intArray)

    #reads each 'int' from array then appends to 'str' array in char form (per element)
    for i in range(len(intArray)):
        strReturn += chr(intArray[i])

    #print(strReturn)
    return strReturn



#writing out read PLC values to OPC server
#REPLACED by 'write_opc_values' function above
def write_opc(plc_read_results, client, machine_num, opc_variables):
    #url = 'opc.tcp://localhost:26543'
    #url = opc_server_ip

    #print("Writing to OPC...")
    #print(url)
    
    #client = await Client(url=url)
    #with Client(url=url) as client:

    #print("Connected to OPC")

    uri = 'http://phoeniximaging.com'
    idx = client.get_namespace_index(uri)

    # used for nonce
    #plc_PLANTCODE    = await client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.I.PlantCode"])

    #print("Writing first tag")
    #plc_LOAD        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.LoadProgram"])
    #plc_LOAD.set_value(bool(plc_read_results[0].value))
    opc_variables['LoadProgram_' + machine_num + 'o'].set_value(bool(plc_read_results[0].value))
    #print("First tag written")

    #plc_START       = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.StartProgram"])
    #plc_START.set_value(bool(plc_read_results[1].value))
    opc_variables['StartProgram_' + machine_num + 'o'].set_value(bool(plc_read_results[1].value))
    #await plc_START.set_value(True)

    #plc_END         = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.EndProgram"])
    #plc_END.set_value(bool(plc_read_results[2].value))
    opc_variables['EndProgram_' + machine_num + 'o'].set_value(bool(plc_read_results[2].value))

    #plc_ABORT        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.AbortProgram"])
    #plc_ABORT.set_value(bool(plc_read_results[3].value))
    opc_variables['AbortProgram_' + machine_num + 'o'].set_value(bool(plc_read_results[3].value))

    #plc_RESET        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.Reset"])
    #plc_RESET.set_value(bool(plc_read_results[4].value))
    opc_variables['Reset_' + machine_num + 'o'].set_value(bool(plc_read_results[4].value))
    
    #DINT are read literally from PLC
    #plc_PartTypeO        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.PartType"])
    #plc_PartTypeO.set_value(plc_read_results[5].value, ua.VariantType.UInt32)
    opc_variables['PartType_' + machine_num + 'o'].set_value(plc_read_results[5].value, ua.VariantType.UInt32)

    #print(chr(plc_read_results[5].value))
    #plc_PartProgramO        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.PartProgram"])
    #plc_PartProgramO.set_value(plc_read_results[6].value, ua.VariantType.UInt32)
    opc_variables['PartProgram_' + machine_num + 'o'].set_value(plc_read_results[6].value, ua.VariantType.UInt32)

    #plc_ScanNumberO        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.ScanNumber"])
    #plc_ScanNumberO.set_value(plc_read_results[7].value, ua.VariantType.UInt32)
    opc_variables['ScanNumber_' + machine_num + 'o'].set_value(plc_read_results[7].value, ua.VariantType.UInt32)
    

    #'PUN' and 'GMPartNumber' are read from the PLC as an array of INT but need to be translated (to ASCII) then concatenated into a singular string for the OPC
    #plc_PUNO        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.PUN"])
    #await plc_PUNO.set_value(await intArray_to_strArray(plc_read_results[8].value))
    #print("Converting PUN to ASCII string")
    PUN_ascii = intArray_to_strArray(plc_read_results[8].value)
    PUN_ascii_merged = ''
    #merging all elements from array 'PUN_ascii' into 'PUN_ascii_merged' to load as one string into OPC
    for i in range(len(PUN_ascii)):
        PUN_ascii_merged+=PUN_ascii[i]

    #print("Merged PUN ASCII below:")
    #print(PUN_ascii_merged)
    #print(PUN_ascii[1])
    #print(plc_read_results[8].value)
    #plc_PUNO.set_value(PUN_ascii_merged)
    opc_variables['PUN_' + machine_num + 'o'].set_value(PUN_ascii_merged)

    #plc_GMPartNumberO        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.GMPartNumber"])
    #await plc_GMPartNumberO.set_value(plc_read_results[9].value)
    GMP_ascii = intArray_to_strArray(plc_read_results[9].value)
    GMP_ascii_merged = '' 
    #print(GMP_ascii)
    for i in range(len(GMP_ascii)):
        GMP_ascii_merged+=GMP_ascii[i]

    #print(GMP_ascii_merged)
    #plc_GMPartNumberO.set_value(GMP_ascii_merged)
    opc_variables['GMPartNumber_' + machine_num + 'o'].set_value(GMP_ascii_merged)


    #plc_ModuleO        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.Module"])
    #print(plc_read_results[10].value)
    #print(chr(plc_read_results[10].value))
    #plc_ModuleO.set_value(chr(plc_read_results[10].value))
    opc_variables['Module_' + machine_num + 'o'].set_value(chr(plc_read_results[10].value))

    
    
    #requires 'chr' casting to go from PLC(int) to 'human-readable'
    #plc_PlantCodeO        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.PlantCode"])
    #THIS IS SUSPECT, why 'str' now?
    #plc_PlantCodeO.set_value(str(plc_read_results[11].value))
    #opc_variables['PlantCode_' + machine_num + 'o'].set_value(str(plc_read_results[11].value))
    opc_variables['PlantCode_' + machine_num + 'o'].set_value(chr(plc_read_results[11].value))
    
    #plc_MonthO        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.Month"])
    #plc_MonthO.set_value(plc_read_results[12].value, ua.VariantType.UInt32)
    opc_variables['Month_' + machine_num + 'o'].set_value(plc_read_results[12].value, ua.VariantType.UInt32)

    #plc_DayO        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.Day"])
    #plc_DayO.set_value(plc_read_results[13].value, ua.VariantType.UInt32)
    opc_variables['Day_' + machine_num + 'o'].set_value(plc_read_results[13].value, ua.VariantType.UInt32)

    #plc_YearO        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.Year"])
    #plc_YearO.set_value(plc_read_results[14].value, ua.VariantType.UInt32)
    opc_variables['Year_' + machine_num + 'o'].set_value(plc_read_results[14].value, ua.VariantType.UInt32)

    #plc_HourO        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.Hour"])
    #plc_HourO.set_value(plc_read_results[15].value, ua.VariantType.UInt32)
    opc_variables['Hour_' + machine_num + 'o'].set_value(plc_read_results[15].value, ua.VariantType.UInt32)

    #plc_MinuteO        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.Minute"])
    #plc_MinuteO.set_value(plc_read_results[16].value, ua.VariantType.UInt32)
    opc_variables['Minute_' + machine_num + 'o'].set_value(plc_read_results[16].value, ua.VariantType.UInt32)

    #plc_SecondO        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.Second"])
    #plc_SecondO.set_value(plc_read_results[17].value, ua.VariantType.UInt32)
    opc_variables['Second_' + machine_num + 'o'].set_value(plc_read_results[17].value, ua.VariantType.UInt32)


    #writing to OPC as 'chr', translates from PLC (int) to 'human-readable' form
    #plc_QualityCheckOP110_O        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.QualityCheckOP110"])
    #plc_QualityCheckOP110_O .set_value(chr(plc_read_results[18].value))
    opc_variables['QualityCheckOP110_' + machine_num + 'o'].set_value(chr(plc_read_results[18].value))

    #print(chr(plc_read_results[18].value))

    #plc_QualityCheckOP120_O        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.QualityCheckOP120"])
    #plc_QualityCheckOP120_O .set_value(chr(plc_read_results[19].value))
    opc_variables['QualityCheckOP120_' + machine_num + 'o'].set_value(chr(plc_read_results[19].value))

    #plc_QualityCheckOP130_O        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.QualityCheckOP130"])
    #plc_QualityCheckOP130_O .set_value(chr(plc_read_results[20].value))
    opc_variables['QualityCheckOP130_' + machine_num + 'o'].set_value(chr(plc_read_results[20].value))

    #plc_QualityCheckOP140_O        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.QualityCheckOP140"])
    #plc_QualityCheckOP140_O .set_value(chr(plc_read_results[21].value))
    opc_variables['QualityCheckOP140_' + machine_num + 'o'].set_value(chr(plc_read_results[21].value))

    #plc_QualityCheckOP150_O        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.QualityCheckOP150"])
    #plc_QualityCheckOP150_O .set_value(chr(plc_read_results[22].value))
    opc_variables['QualityCheckOP150_' + machine_num + 'o'].set_value(chr(plc_read_results[22].value))

    #plc_QualityCheckOP310_O        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.QualityCheckOP310"])
    #plc_QualityCheckOP310_O .set_value(chr(plc_read_results[23].value))
    opc_variables['QualityCheckOP310_' + machine_num + 'o'].set_value(chr(plc_read_results[23].value))

    #plc_QualityCheckOP320_O        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.QualityCheckOP320"])
    #plc_QualityCheckOP320_O .set_value(chr(plc_read_results[24].value))
    opc_variables['QualityCheckOP320_' + machine_num + 'o'].set_value(chr(plc_read_results[24].value))

    #plc_QualityCheckOP330_O        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.QualityCheckOP330"])
    #plc_QualityCheckOP330_O .set_value(chr(plc_read_results[25].value))
    opc_variables['QualityCheckOP330_' + machine_num + 'o'].set_value(chr(plc_read_results[25].value))

    #plc_QualityCheckOP340_O        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.QualityCheckOP340"])
    #plc_QualityCheckOP340_O .set_value(chr(plc_read_results[26].value))
    opc_variables['QualityCheckOP340_' + machine_num + 'o'].set_value(chr(plc_read_results[26].value))

    #plc_QualityCheckOP360_O        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.QualityCheckOP360"])
    #plc_QualityCheckOP360_O .set_value(chr(plc_read_results[27].value))
    opc_variables['QualityCheckOP360_' + machine_num + 'o'].set_value(chr(plc_read_results[27].value))

    #plc_QualityCheckOP370_O        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.QualityCheckOP370"])
    #plc_QualityCheckOP370_O .set_value(chr(plc_read_results[28].value))
    opc_variables['QualityCheckOP370_' + machine_num + 'o'].set_value(chr(plc_read_results[28].value))

    #plc_QualityCheckOP380_O        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.QualityCheckOP380"])
    #plc_QualityCheckOP380_O .set_value(chr(plc_read_results[29].value))
    opc_variables['QualityCheckOP380_' + machine_num + 'o'].set_value(chr(plc_read_results[29].value))

    #plc_QualityCheckOP390_O        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.QualityCheckOP390"])
    #plc_QualityCheckOP390_O .set_value(chr(plc_read_results[30].value))
    opc_variables['QualityCheckOP390_' + machine_num + 'o'].set_value(chr(plc_read_results[30].value))

    #plc_QualityCheckScoutPartTracking_O        = client.nodes.root.get_child(["0:Objects", f"{idx}:HM1450_VS" + machine_num, f"{idx}:VPC1.O.QualityCheckScoutPartTracking"])
    #plc_QualityCheckScoutPartTracking_O .set_value(chr(plc_read_results[31].value))
    opc_variables['QualityCheckScoutPartTracking_' + machine_num + 'o'].set_value(chr(plc_read_results[31].value))

        

    print("Finished writing OPC...")
    #client.close_session

#end 'write_opc'

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

#end intArray_to_strArray

#function to translate OPC str-arrays into PLC int-arrays
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

#end strArray_to_intArray

def TriggerKeyence(server_address_tuple):

    trigger_start_time_total = datetime.datetime.now()

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address =  server_address_tuple #`('localhost', 10000)
    print('connecting to %s port %s' % server_address)
    trigger_start_time = datetime.datetime.now()
    sock.connect(server_address)
    trigger_end_time = datetime.datetime.now()
    time_diff = (trigger_end_time - trigger_start_time)
    execution_time = time_diff.total_seconds() * 1000
    print("Keyence Connected in: " + str(execution_time))

    try:
        # Send data
        message = 'T1\r\n' #'This is the message.  It will be repeated.'
        print('sending "%s"' % message)
        sock.sendall(message.encode())

        data = sock.recv(32)
        print('received "%s"' % data)

        # Look for the response
#        amount_received = 0
#        amount_expected = len(message)
#                                    
#        while amount_received < amount_expected:
#            data = sock.recv(16)
#            amount_received += len(data)
#            print('received "%s"' % data)

    finally:
        print('closing socket')
        sock.close()
        trigger_end_time_total = datetime.datetime.now()
        time_diff = (trigger_end_time_total - trigger_start_time_total)
        execution_time = time_diff.total_seconds() * 1000
        print("Keyence \'TriggerKeyence\' total time: " + str(execution_time))


ready_flag = False

def main():

    #Variable to determine if console output is displayed during run
    global debug_msgs
    global retries
    global ready_flag

    global ready14_OLD
    global ready15_OLD

    ''' CONFIG settings
    #TODO: need to copy in config.txt if 'connector' directory exists

    #variable to see if manual config file exists in 'connector' directory
    config_path = 'connector/config.txt'
    is_config = os.path.isfile(config_path)
    #print(is_config)


    #if config.txt exists in the connector directory, overwrite config.txt file
    if(is_config):
        print("Manual config file detected, overwriting...\n")
        #reading in manual config file
        new_config = open('connector/config.txt', 'r+').read()
        #print(new_config)

        #overwriting 'config/config.txt' with contents of 'connector/config.txt'
        with open('config/config.txt', 'r+') as original_config:
            #sets file's current position to '0' (start)
            original_config.seek(0)
            original_config.write(new_config)
            original_config.truncate()


    #reading config.txt file
    with open('config.txt') as config_file:
        config_data = config_file.read()
        #print(config_data)
        #print(config_data[0][0])
        config_vars = json.loads(config_data)
        #print(config_vars)

        #testing data type from dictionary, probably should recast as int/bool later
        #print(type(config_vars['read_plc_phoenix']))

    #setting variable for PLC connection
    #plc = LogixDriver(config_vars['plc_ip'])

    #if config file specifies printing all from PLC
    if(config_vars['read_plc_all'] == 1):
        with LogixDriver(config_vars['plc_ip']) as plc:
            plc.open()
            print("PLC: ")
            print(plc)
            print()
            print("PLC Info: ")
            print(plc.info)
            print()
            print("Tags(blob)")
            print(plc._tags) #prints tags

            for tag in plc.tags:
                print("Tags: ")
                print(tag + ": ")
                print()

            #result = plc.read('Program:MainProgram.VPC1_14.VPC1.I.Ready') #reading 1 field from PLC
            #print(result)
            plc.close
    '''
    #setting OPC connection / variables
    #opc_variables = {}
    #opc_variables = connect_opc(config_vars['opc_server_ip'])
    #print(opc_variables)
    #print()
    #print(opc_variables['LoadProgram_14o'])

    #pause to stop exception throwing on startup?
    #throws exceptions because OPC server takes a few moments to start
    print("Alive...")
    time.sleep(5)

    print("Connecting to PLC")
    #with LogixDriver(config_vars['plc_ip']) as plc:
    with LogixDriver("120.123.230.39/0") as plc:
        print()
        print("Initializing! Current Timestamp: " + str(datetime.datetime.now()))

        #if config file specifies to read from PLC (always?)
        #if(config_vars['read_plc_phoenix'] == 1):
        if(1 == 1):
            try:
                #PLC connection
                #with LogixDriver(config_vars['plc_ip']) as plc:

                isLoaded_14 = False
                isLoaded_15 = False
                
                while(True):

                    debug_msgs = False
                    rand_value = randrange(75)
                    #random.seed(10)
                    #print("Random Value:")
                    #print(rand_value)
                    #print("**************")
                    
                    #lottery debug msg output
                    if (rand_value == 1):
                        #print("\n\n\n\n\n\nIt happened!\n\n\n\n\n\n")
                        debug_msgs = True

                    
                    if debug_msgs == True:
                        print("Has reconnected: " + str(retries) + ' times')

                    start_time_total = datetime.datetime.now()

                    #test_results = opc_variables.get_values()
                    #print(test_results)
                    #print('**************************')

                    start_time_total = datetime.datetime.now()
                    

                    #logging how long the 'read' takes
                    start_time = datetime.datetime.now()
                    #populating current tags/values w/ custom read function
                    #results_14 = read_plc(plc, '14')
                    results_14_dict = read_plc_dict(plc, '1')
                    print(results_14_dict)
                    print()
                    for result in results_14_dict:
                        print(result)
                        print()
                    time.sleep(100)
                    #print(results_14[0].value)
                    end_time = datetime.datetime.now()
                    time_diff = (end_time - start_time)
                    execution_time = time_diff.total_seconds() * 1000

                    #if(results_14_dict['LoadProgram'][1] == True) and (isLoaded_14 == False):
                    if not isLoaded_14 and results_14_dict['LoadProgram'][1]:
                        print("isLoaded_14 is set@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                        isLoaded_14 = True
                    #else:
                    #    print("results_14_dict['LoadProgram'][1]: ", results_14_dict['LoadProgram'][1], "; isLoaded_14: ", isLoaded_14)




                    '''
                    #disabling writing to PLC if 'LoadProgram' is false
                    if results_14_dict['LoadProgram'][1] == False:
                        #disabling writing to PLC if 'LoadProgram' goes low
                        config_vars['write_plc'] = 0

                    #re-enables writing to plc once 'EndProgram' is set high (True)
                    if results_14_dict['EndProgram'][1] == True:
                        #enabling writing to PLC once 'EndProgram' is set high
                        config_vars['write_plc'] = 1

                    #if (results_14_dict['StartProgram'][1] == True) and (isLoaded_14 == True):
                    if isLoaded_14 and results_14_dict['StartProgram'][1]:
                        print("Keyence trigger 14 ##################")
                        isLoaded_14 = False
                        #TriggerKeyence(('172.19.145.80', 8500))
                    #else:
                    #    print("results_14_dict['StartProgram'][1]: ", results_14_dict['StartProgram'][1], "; isLoaded_14: ", isLoaded_14)
                    '''

                    if debug_msgs == True:
                        print("Phoenix PLC read tags (14) in: " + str(execution_time) + " ms")

                    #printing one OPC tag VALUE
                    #print(opc_variables['Ready_14i'].get_value())

                    #for key in opc_variables:
                        #print('*')
                        #print(key)
                        #print('*')


                    #BULK SET TEST
                    #self.ro_clt.set_values([v1, v2, v3], [4, 5, 6])
                    #client.set_values([opc_variables['QualityCheckOP110_14i'], 
                    #opc_variables['QualityCheckOP120_14i'], 
                    #opc_variables['QualityCheckOP130_14i']], 
                    #['B', 
                    #'C', 
                    #'D']
                    #)
                    #print(test_list)
                    #gets ALL values from the list, single-shot
                    #test_results = client.get_values(test_list)
                    #print(test_results)

                    #time.sleep(1)

                    


                    '''
                    if (opc_variables['Ready_14i'].get_value() == False) and ready_flag == False:
                        ready_timer = datetime.datetime.now()
                        ready_flag = True

                    if (opc_variables['Ready_14i'].get_value() == True) and ready_flag == True:
                        ready_execution_time = (datetime.datetime.now() - ready_timer).total_seconds() * 1000
                        print("Ready went from False to True in: " + str(ready_execution_time) + " ms")
                        ready_flag = False
                    '''
                    
                    

                    #if config asks to write to OPC server, start 'write_opc' func with all results from PLC
                    if(config_vars['write_opc'] == 1):
                        #writing to OPC server
                        #print("Writing read \'.O\' PLC values to OPC server")
                        #write_opc(results_14, config_vars['opc_server_ip'], '14')
                        ###NEW TESTING###
                        #write_opc(results_14, client, '14', opc_variables)
                        start_time_OPC = datetime.datetime.now()
                        opc_translated_values = write_opc_dict(results_14_dict, client, '14', debug_msgs)
                        end_time_OPC = datetime.datetime.now()
                        time_diff = (end_time_OPC - start_time_OPC)
                        execution_time = time_diff.total_seconds() * 1000

                        if debug_msgs == True:
                            print("OPC \'write_opc_dict\' (14) in: " + str(execution_time) + " ms")


                        start_time_OPC = datetime.datetime.now()
                        #opc_write_values(client, idx, machine_num, key, value, datatype, opc_variables, opc_translated_values)
                        opc_write_values(client, '14', opc_variables, opc_translated_values)
                        #print(opc_translated_values)
                        end_time_OPC = datetime.datetime.now()
                        time_diff = (end_time_OPC - start_time_OPC)
                        execution_time = time_diff.total_seconds() * 1000
                        if debug_msgs == True:
                            print("OPC \'opc_write_values\' (14) in: " + str(execution_time) + " ms")


                    if(config_vars['write_plc'] == 1):
                        start_time_plc = datetime.datetime.now()
                        #writing OPC '.I' variable-values back to PLC
                        #write_plc(plc, client, '14', opc_variables)
                        plc_write_shim(plc,client,'14',opc_variables)


                        end_time_plc = datetime.datetime.now()

                        #comparing 'Ready' value from last-read for testing purposes
                        #if opc_variables['Ready_14i'].get_value() != ready14_OLD:
                        #    print('\"Ready\" value has changed for 14')
                        #    print('Was: ' + str(ready14_OLD) + ' Now: ' + str(opc_variables['Ready_14i'].get_value()))
                        #    ready14_OLD = opc_variables['Ready_14i']

                        time_diff = (end_time_plc - start_time_plc)
                        execution_time = time_diff.total_seconds() * 1000
                        if debug_msgs == True:
                            print("PLC \'write_plc\' (14) in: " + str(execution_time) + " ms")

                    #time.sleep(5) #artificial time between changes

                    #print()
                    
                    #logging how long the 'read' takes
                    start_time = datetime.datetime.now()
                    #populating current tags/values w/ custom read function
                    #results_15 = read_plc(plc, '15')
                    results_15_dict = read_plc_dict(plc, '15')
                    #print(results_15[0].value)
                    end_time = datetime.datetime.now()
                    time_diff = (end_time - start_time)
                    execution_time = time_diff.total_seconds() * 1000


                    #if(results_15_dict['LoadProgram'][1] == True) and (isLoaded_15 == False):
                    if not isLoaded_15 and results_15_dict['LoadProgram'][1]:
                        print("isLoaded_15 is set@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
                        isLoaded_15 = True
                    #else:
                    #    print("results_15_dict['LoadProgram'][1]: ", results_15_dict['LoadProgram'][1], "; isLoaded_15: ", isLoaded_15)

                    '''
                    if results_15_dict['LoadProgram'][1] == False:
                        #disabling writing to PLC if 'LoadProgram' goes low
                        config_vars['write_plc'] = 0

                    if results_15_dict['EndProgram'][1] == True:
                        #enabling writing to PLC once 'EndProgram' is set high
                        config_vars['write_plc'] = 1


                    #if (results_15_dict['StartProgram'][1] == True) and (isLoaded_15 == True):
                    if isLoaded_15 and results_15_dict['StartProgram'][1]:
                        print("Keyence trigger 15 ##################")
                        isLoaded_15 = False
                        #TriggerKeyence(('172.19.146.81', 8500))
                    #else:
                    #    print("results_15_dict['StartProgram'][1]: ", results_15_dict['StartProgram'][1], "; isLoaded_15: ", isLoaded_15)
                    '''

                    if debug_msgs == True:
                        print("\nPhoenix PLC read tags (15) in: " + str(execution_time) + " ms")
                    #print(execution_time)

                    #if config asks to write to OPC server, start 'write_opc' func with all results from PLC
                    if(config_vars['write_opc'] == 1):
                        #writing to OPC server
                        #print("Writing read \'.O\' PLC values to OPC server")
                        #write_opc(results_15, config_vars['opc_server_ip'], '15')
                        ###NEW TESTING###
                        #write_opc(results_15, client, '15', opc_variables)
                        start_time_OPC = datetime.datetime.now()
                        opc_translated_values = write_opc_dict(results_15_dict, client, '15', debug_msgs)
                        end_time_OPC = datetime.datetime.now()
                        time_diff = (end_time_OPC - start_time_OPC)
                        execution_time = time_diff.total_seconds() * 1000

                        if debug_msgs == True:
                            print("OPC \'write_opc_dict\' (15) in: " + str(execution_time) + " ms")


                        start_time_OPC = datetime.datetime.now()
                        #opc_write_values(client, idx, machine_num, key, value, datatype, opc_variables, opc_translated_values)
                        opc_write_values(client, '15', opc_variables, opc_translated_values)
                        #print(opc_translated_values)
                        end_time_OPC = datetime.datetime.now()
                        time_diff = (end_time_OPC - start_time_OPC)
                        execution_time = time_diff.total_seconds() * 1000
                        if debug_msgs == True:
                            print("OPC \'opc_write_values\' (15) in: " + str(execution_time) + " ms")

                    
                    if(config_vars['write_plc'] == 1):
                        start_time_plc = datetime.datetime.now()
                        #writing OPC '.I' variable-values back to PLC
                        #write_plc(plc, client, '15', opc_variables)
                        plc_write_shim(plc,client,'15',opc_variables)


                        end_time_plc = datetime.datetime.now()

                        #comparing 'Ready' value from last-read for testing purposes
                        #if opc_variables['Ready_15i'].get_value() != ready15_OLD:
                        #    print('\"Ready\" value has changed for 15')
                        #    ready15_OLD = opc_variables['Ready_15i']

                        time_diff = (end_time_plc - start_time_plc)
                        execution_time = time_diff.total_seconds() * 1000
                        if debug_msgs == True:
                            print("PLC \'write_plc\' (15) in: " + str(execution_time) + " ms")

                    end_time_total = datetime.datetime.now()
                    time_diff_total = (end_time_total - start_time_total)
                    execution_time_total = time_diff_total.total_seconds() * 1000

                    if debug_msgs == True:
                        #print(opc_variables['Ready_14i'].get_value())

                        #print('***')
                        print('[14]: ' + 'LoadProgram:' + str(results_14_dict['LoadProgram'].value) + ',EndProgram:' + str(results_14_dict['EndProgram'].value) + ',StartProgram:' + str(results_14_dict['StartProgram'].value) + ',AbortProgram:' + str(results_14_dict['AbortProgram'].value) + ',Reset:' + str(results_14_dict['Reset'].value) + ',Ready:' + str(opc_variables['Ready_14i'].get_value()) + ',Busy:' + str(opc_variables['Busy_14i'].get_value()) + ',Done:' + str(opc_variables['Done_14i'].get_value()) + ',Pass:' + str(opc_variables['Pass_14i'].get_value()) + ',Fail:' + str(opc_variables['Fail_14i'].get_value()) + ',Faulted:' + str(opc_variables['Faulted_14i'].get_value()))
                        #print('^^^')
                        print('[15]: ' + 'LoadProgram:' + str(results_15_dict['LoadProgram'].value) + ',EndProgram:' + str(results_15_dict['EndProgram'].value) + ',StartProgram:' + str(results_15_dict['StartProgram'].value) + ',AbortProgram:' + str(results_15_dict['AbortProgram'].value) + ',Reset:' + str(results_15_dict['Reset'].value) + ',Ready:' + str(opc_variables['Ready_15i'].get_value()) + ',Busy:' + str(opc_variables['Busy_15i'].get_value()) + ',Done:' + str(opc_variables['Done_15i'].get_value()) + ',Pass:' + str(opc_variables['Pass_15i'].get_value()) + ',Fail:' + str(opc_variables['Fail_15i'].get_value()) + ',Faulted:' + str(opc_variables['Faulted_15i'].get_value()))
                        #print('***')
                        print()
                        print("14 & 15 Complete!")
                        print()
                        print("Final Debug Output! Current Timestamp: " + str(datetime.datetime.now()))
                        #time.sleep(.5) #artificial time between changes
                        print("\nTotal Loop Time: " + str(execution_time_total) + " ms\n")

                        #print("Artificial Wait 10ms...")
                    #time.sleep(.01)

            except Exception as e:
                #special case for when OPC(?) doesn't respond correctly
                #if str(e) == 'failed to receive reply':
                #    client.close_session
                #    plc.close
                #    #main()

                print("\nexception thrown...")
                print(e)
                print()
                print()
                print("Exception! Current Timestamp: " + str(datetime.datetime.now()))

                #closing OPC & PLC connections when an exception is thrown, reinitialized when 'main()' is started again
                client.close_session
                plc.close

                #capping possible sleep time at 19 seconds
                #if retries < 10:
                #    #incrementing number of connection attempts
                #    retries = retries + 1

                #print("Sleeping for: " + str(retries+10) + " seconds")
                #time.sleep(retries)
                #main()
                
        #condition if config file specifies NOT to read from PLC
        else:
            print("\n\'read_plc\' is not set to 1...")
    
if __name__ == '__main__':
    main()
