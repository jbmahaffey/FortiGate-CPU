#!/usr/bin/env python3

import csv
import requests
import argparse
import ssl
import datetime
import time
import pprint
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings() 

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--fortigate', default='192.168.101.201:14000', help='Firewall IP Address')
    parser.add_argument('--token', default='', help='API Token')
    parser.add_argument('--interval', default='1', help='Time period to query cpu stats 1-min, 10-min, 30-min, 1-hour, 12-hour')
    parser.add_argument('--devlist', default='cpu.csv', help='CPU usage over time.')
    parser.add_argument('--version', default='6.4', help='Fortigate version')
    args = parser.parse_args()
    
    if args.version >= '7.0':
        try:
            address_url = 'https://{}/api/v2/monitor/system/performance/status'.format(args.fortigate)
            headers = {
                'Authorization': 'Bearer' + args.token, 
                'content-type': 'application/json'
                }

        except:
            print('Error logging into Fortigate')

        # Write logs to csv file
        data_file = open('cpu.csv', 'a')
        csv_writer = csv.writer(data_file)

        count = 0
        proclist = []
        endTime = datetime.datetime.now() + datetime.timedelta(minutes=int(args.interval))
        while True:
            if datetime.datetime.now() >= endTime:
                break
            else:
                try:
                    cpu = requests.get(address_url, headers=headers, verify=False)
                except:
                    print('Invalid response')
                user = cpu.json()['results']['cpu']['user']
                kernel = cpu.json()['results']['cpu']['system']
                nice = cpu.json()['results']['cpu']['system']
                idle = cpu.json()['results']['cpu']['idle']
                iowait = cpu.json()['results']['cpu']['iowait']
                process = {
                    'user': user,
                    'kernel': kernel,
                    'nice': nice,
                    'idle': idle,
                    'iowait': iowait
                }
                proclist.append(process)
                for proc in proclist:
                    if count == 0:
                        header = proc.keys()
                        csv_writer.writerow(header)
                        count += 1
                    csv_writer.writerow(proc.values())
                time.sleep(10)

        # Close Log File
        data_file.close()
    
    elif args.version < '7.0': 
        try:
            address_url = 'https://{}/api/v2/monitor/system/vdom-resource?vdom=root'.format(args.fortigate)
            headers = {
                'Authorization': 'Bearer' + args.token, 
                'content-type': 'application/json'
                }

        except:
            print('Error logging into Fortigate')
        
        endTime = datetime.datetime.now() + datetime.timedelta(minutes=int(args.interval))
        while True:
            if datetime.datetime.now() >= endTime:
                break
            else:
                try:
                    cpu = requests.get(address_url, headers=headers, verify=False)
                except:
                    print('Invalid response')
                # Write logs to csv file
                data_file = open('cpu.csv', 'a+')
                csv_writer = csv.writer(data_file)
                csv_writer.writerow([str(cpu.json()['results']['cpu']), 'Current CPU Percentage', datetime.datetime.now()])
                time.sleep(10)
        # Close Log File
        data_file.close()

if __name__ == '__main__':
   main()