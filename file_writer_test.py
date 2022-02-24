import csv
import time

x = [0,1,2,3,4,5,6,7,8,9]

while(True):
    file = open('//phoenix-101/homes/Howard.Roush/Drive/phoenix_to_plc.csv', 'w')
    csv_writer = csv.writer(file)
    csv_writer.writerow(x)
    x[0] = x[0] + 10
    print(f'Write {x} to csv!')
    time.sleep(1)
