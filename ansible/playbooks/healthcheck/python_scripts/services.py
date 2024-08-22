#!/usr/bin/python3.9

import subprocess

def get_enabled_services():
    try:
        output = subprocess.check_output(['chkconfig', '--list'])
        lines = output.decode('utf-8').split('\n')
        enabled_services = [line.split()[0] for line in lines if '3:on' in line]
        return enabled_services
    except subprocess.CalledProcessError:
        return []


def is_service_running(service_name):
    exceptions = ['iptables', 'network']
    try:
        if service_name in exceptions:
            return True
        else:
            output = subprocess.check_output(['service', service_name, 'status'])
            return "running" in output.decode('utf-8')  
    except subprocess.CalledProcessError:
        return False


enabled_services = get_enabled_services()

for service_name in enabled_services:
    if is_service_running(service_name):
        continue
    else:
        print(f"{service_name} is enabled but not running.")
