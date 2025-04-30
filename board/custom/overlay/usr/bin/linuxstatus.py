#!/usr/bin/env python3

import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

# --- Funções para coletar informações do sistema --- #

def get_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
    return int(uptime_seconds)


def get_cpu_info():
    cpu_info = {}
    with open('/proc/cpuinfo', 'r') as f:
        for line in f:
            if line.startswith('model name'):
                cpu_info['model'] = line.split(':')[1].strip()
            if line.startswith('cpu MHz'):
                cpu_info['speed_mhz'] = float(line.split(':')[1].strip())
                break

    # Calcular uso da CPU
    with open('/proc/stat', 'r') as f:
        line = f.readline()
        cpu_times = list(map(int, line.split()[1:]))
        idle_time = cpu_times[3]
        total_time = sum(cpu_times)
        
    time.sleep(0.1)
    
    with open('/proc/stat', 'r') as f:
        line = f.readline()
        cpu_times = list(map(int, line.split()[1:]))
        idle_time_2 = cpu_times[3]
        total_time_2 = sum(cpu_times)
        
    idle_diff = idle_time_2 - idle_time
    total_diff = total_time_2 - total_time

    usage_percent = 100 * (1 - (idle_diff / total_diff))

    cpu_info['usage_percent'] = round(usage_percent, 2)
    
    return cpu_info


def get_memory_info():
    mem_info = {}
    with open('/proc/meminfo', 'r') as f:
        mem_total = 0
        mem_free = 0
        for line in f:
            if line.startswith('MemTotal'):
                mem_total = int(line.split()[1]) / 1024
            elif line.startswith('MemAvailable'):
                mem_free = int(line.split()[1]) / 1024
                break
        mem_info['total_mb'] = round(mem_total, 2)
        mem_info['used_mb'] = round(mem_total - mem_free, 2)
    return mem_info


def get_os_version():
    with open('/proc/version', 'r') as f:
        return f.read().strip()


def get_process_list():
    processes = []
    for pid in os.listdir('/proc'):
        if pid.isdigit():
            try:
                with open(f'/proc/{pid}/comm', 'r') as f:
                    process_name = f.readline().strip()
                    processes.append({"pid": int(pid), "name": process_name})
            except FileNotFoundError:
                continue
    return processes


def get_disks():
    disks = []
    with open('/proc/partitions', 'r') as f:
        for line in f.readlines()[2:]:
            parts = line.split()
            if len(parts) == 4:
                device = parts[3]
                size_mb = int(parts[2]) / 1024
                disks.append({"device": f"/dev/{device}", "size_mb": round(size_mb, 2)})
    return disks


def get_usb_devices():
    devices = []
    usb_path = '/sys/bus/usb/devices/'
    for device in os.listdir(usb_path):
        dev_path = os.path.join(usb_path, device)
        try:
            with open(os.path.join(dev_path, 'product'), 'r') as f:
                description = f.read().strip()
                devices.append({"port": device, "description": description})
        except FileNotFoundError:
            continue
    return devices


def get_network_adapters():
    adapters = []
    with open('/proc/net/dev', 'r') as f:
        for line in f.readlines()[2:]:
            if ':' in line:
                interface = line.split(':')[0].strip()
                try:
                    with open(f'/sys/class/net/{interface}/address', 'r') as f:
                        ip_address = f.read().strip()
                    adapters.append({"interface": interface, "ip_address": ip_address})
                except FileNotFoundError:
                    adapters.append({"interface": interface, "ip_address": "N/A"})
    return adapters


# --- Servidor HTTP --- #

class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/status":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            return

        response = {
            "datetime": get_datetime(),
            "uptime_seconds": get_uptime(),
            "cpu": get_cpu_info(),
            "memory": get_memory_info(),
            "os_version": get_os_version(),
            "processes": get_process_list(),
            "disks": get_disks(),
            "usb_devices": get_usb_devices(),
            "network_adapters": get_network_adapters()
        }

        data = json.dumps(response, indent=2).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

def run_server(port=8080):
    print(f"Servidor disponível em http://0.0.0.0:{port}/status")
    server = HTTPServer(("0.0.0.0", port), StatusHandler)
    server.serve_forever()

if __name__ == "__main__":
    run_server()
