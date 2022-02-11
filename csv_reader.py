import csv
import json
import time
import os

def csv_read():
    #csv file reader variable declaration
    #file = open('\\phoenix-101\homes\Howard.Roush\Drive\plc_dummy.csv') #Python doesn't like \\
    file = open('//phoenix-101/homes/Howard.Roush/Drive/plc_dummy.csv')
    csvreader = csv.reader(file)

    #creating two lists that will be combined in the dictionary 'plc_dict'
    header = []
    header = next(csvreader) # tag names
    values = []
    values = next(csvreader) # values

    #print(len(header))
    #print(values)

    plc_dict = {} # dictionary: key = tag name
    #setting relevant value for each tag
    for x in range(len(header)):
        plc_dict[header[x]] = int(values[x]) #populating dict, casting to int for simplicity

    #print(plc_dict)
    #print()
    #print(type(plc_dict['LOAD_PROGRAM']))
    return plc_dict
#END csv_read

def main():
    while(True):
        csv_results = csv_read()
        print(csv_results)
        time.sleep(3)

if __name__ == '__main__':
    main()