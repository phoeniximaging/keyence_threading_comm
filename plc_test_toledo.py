from pycomm3 import LogixDriver
from pycomm3.cip.data_types import DINT, UINT
import time

with LogixDriver("120.123.230.39/0") as plc:
            plc.open()

            plc.write('Program:CM080CA01.PorosityInspect.CAM01.I.PART_TYPE', 0)
            print('Wrote TRUE to CAM01(FAULTED)')

            time.sleep(100)

            '''
            print("PLC: ")
            print(plc)
            print()
            print("PLC Info: ")
            print(plc.info)
            print()
            #print("Tags(blob):")
            #print(plc._tags) #prints tags

            for tag in plc.tags:
                print("Tags: ")
                print(tag + ": ")
                print()
            '''
            
            tags = ['Program:CM080CA01.PorosityInspect.CAM01.O.LOAD_PROGRAM',
                    'Program:CM080CA01.PorosityInspect.CAM01.O.START_PROGRAM',
                    'Program:CM080CA01.PorosityInspect.CAM01.O.END_PROGRAM',
                    'Program:CM080CA01.PorosityInspect.CAM01.O.ABORT_PROGRAM',
                    'Program:CM080CA01.PorosityInspect.CAM01.O.RESET',
                    'Program:CM080CA01.PorosityInspect.CAM01.O.HEARTBEAT',
                    'Program:CM080CA01.PorosityInspect.CAM01.O.MASTER_PART',
                    'Program:CM080CA01.PorosityInspect.CAM01.O.PART_TYPE',
                    'Program:CM080CA01.PorosityInspect.CAM01.O.PART_PROGRAM',
                    'Program:CM080CA01.PorosityInspect.CAM01.O.PUN',
                    'Program:CM080CA01.PorosityInspect.CAM01.O.MODULE',
                    'Program:CM080CA01.PorosityInspect.CAM01.O.PLANTCODE',
                    'Program:CM080CA01.PorosityInspect.CAM01.O.TIMESTAMP_MONTH',
                    'Program:CM080CA01.PorosityInspect.CAM01.O.TIMESTAMP_DAY',
                    'Program:CM080CA01.PorosityInspect.CAM01.O.TIMESTAMP_YEAR',
                    'Program:CM080CA01.PorosityInspect.CAM01.O.TIMESTAMP_HOUR',
                    'Program:CM080CA01.PorosityInspect.CAM01.O.TIMESTAMP_MINUTE',
                    'Program:CM080CA01.PorosityInspect.CAM01.O.TIMESTAMP_SECOND']

            
            #result = plc.read('Program:CM080CA01.PorosityInspect') #reading 1 field from PLC *VALID RESULTS
            #result = plc.read('Program:CM080CA01.PorosityInspect.CAM01.O.LOAD_PROGRAM')
            #print(result)

            #print('GrobPLCToPhoenix Tags:')
            for tag in tags:
                result = plc.read(tag)
                #print(f'{tag}: {result[1]} | {type(result[1])}')
            #print()

            tags = ['Program:CM080CA01.PorosityInspect.CAM01.I.READY',
                    'Program:CM080CA01.PorosityInspect.CAM01.I.BUSY',
                    'Program:CM080CA01.PorosityInspect.CAM01.I.DONE',
                    'Program:CM080CA01.PorosityInspect.CAM01.I.PASS',
                    'Program:CM080CA01.PorosityInspect.CAM01.I.FAIL',
                    'Program:CM080CA01.PorosityInspect.CAM01.I.HEARTBEAT',
                    'Program:CM080CA01.PorosityInspect.CAM01.I.MASTER_PART',
                    'Program:CM080CA01.PorosityInspect.CAM01.I.PART_TYPE',
                    'Program:CM080CA01.PorosityInspect.CAM01.I.PART_PROGRAM',
                    'Program:CM080CA01.PorosityInspect.CAM01.I.PUN',
                    'Program:CM080CA01.PorosityInspect.CAM01.I.MODULE',
                    'Program:CM080CA01.PorosityInspect.CAM01.I.PLANTCODE',
                    'Program:CM080CA01.PorosityInspect.CAM01.I.TIMESTAMP_MONTH',
                    'Program:CM080CA01.PorosityInspect.CAM01.I.TIMESTAMP_DAY',
                    'Program:CM080CA01.PorosityInspect.CAM01.I.TIMESTAMP_YEAR',
                    'Program:CM080CA01.PorosityInspect.CAM01.I.TIMESTAMP_HOUR',
                    'Program:CM080CA01.PorosityInspect.CAM01.I.TIMESTAMP_MINUTE',
                    'Program:CM080CA01.PorosityInspect.CAM01.I.TIMESTAMP_SECOND',
                    'Program:CM080CA01.PorosityInspect.CAM01.I.DEFECT_NUMBER',
                    'Program:CM080CA01.PorosityInspect.CAM01.I.DEFECT_SIZE',
                    'Program:CM080CA01.PorosityInspect.CAM01.I.DEFECT_ZONE']
            #print('PhoenixToGrobPLC Tags:')
            for tag in tags:
                result = plc.read(tag)
                #print(f'{tag}: {result[1]} | {type(result[1])}')
            #print()

            #toggle booleans True/False 3 times
            for x in range(3):
                plc_display_single = plc.read('Program:CM080CA01.PorosityInspect.CAM01.I.READY')
                print(f'READY was: {plc_display_single[1]} {type(plc_display_single[1])}')
                #flip TRUE/FALSE each run
                if(plc_display_single[1] == 0):
                    print('Writing READY = True')
                    try:
                        plc.write(('Program:CM080CA01.PorosityInspect.CAM01.I.READY', 1),
                                  ('Program:CM080CA01.PorosityInspect.CAM01.I.BUSY', 1),
                                  ('Program:CM080CA01.PorosityInspect.CAM01.I.DONE', 1),
                                  ('Program:CM080CA01.PorosityInspect.CAM01.I.PASS', 1),
                                  ('Program:CM080CA01.PorosityInspect.CAM01.I.FAIL', 1))
                    except Exception as e:
                        print(e)
                    print('Write Complete!')
                else:
                    print('Writing READY = False')
                    plc.write(('Program:CM080CA01.PorosityInspect.CAM01.I.READY', 0),
                                  ('Program:CM080CA01.PorosityInspect.CAM01.I.BUSY', 0),
                                  ('Program:CM080CA01.PorosityInspect.CAM01.I.DONE', 0),
                                  ('Program:CM080CA01.PorosityInspect.CAM01.I.PASS', 0),
                                  ('Program:CM080CA01.PorosityInspect.CAM01.I.FAIL', 0))
                    
                plc_display_booleans = plc.read('Program:CM080CA01.PorosityInspect.CAM01.I.READY',
                                              'Program:CM080CA01.PorosityInspect.CAM01.I.BUSY',
                                              'Program:CM080CA01.PorosityInspect.CAM01.I.DONE',
                                              'Program:CM080CA01.PorosityInspect.CAM01.I.PASS',
                                              'Program:CM080CA01.PorosityInspect.CAM01.I.FAIL')
                for result in plc_display_booleans:
                    print(f'{result[0]} : {result[1]}')
                #print(f'READY now: {plc_display_single[1]}')

                time.sleep(3) #artificial pause between flips

            print('Closing PLC connection')
            plc.close
