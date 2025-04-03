#!/usr/bin/env python3

import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

# --- Alunos devem implementar as funções abaixo --- #

def get_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
    return int(uptime_seconds)

def get_cpu_info():
    with open('/proc/cpuinfo', 'r') as f:
        for line in f:
            if line.startswith('model name'):
                model = line.split(':')[1].strip()
            if line.startswith('cpu MHz'):
                speed_mhz = float(line.split(':')[1].strip())
                break
    return {
        "model": model,
        "speed_mhz": speed_mhz,
        "usage_percent": 0.0  # A implementação do cálculo do uso da CPU será feita depois
    }

def get_memory_info():
    with open('/proc/meminfo', 'r') as f:
        lines = f.readlines()
        total_mem = int(lines[0].split()[1]) // 1024
        free_mem = int(lines[1].split()[1]) // 1024
        used_mem = total_mem - free_mem
    return {
        "total_mb": total_mem,
        "used_mb": used_mem
    }

def get_os_version():
    with open('/proc/version', 'r') as f:
        return f.read().strip()

def get_process_list():
    import os
    processes = []
    for pid in os.listdir('/proc'):
        if pid.isdigit():
            try:
                with open(f'/proc/{pid}/comm', 'r') as f:
                    name = f.read().strip()
                processes.append({"pid": int(pid), "name": name})
            except:
                continue
    return processes

def get_disks():
    with open('/proc/partitions', 'r') as f:
        lines = f.readlines()[2:]
        disks = []
        for line in lines:
            words = line.strip().split()
            if len(words) == 4:
                device = words[3]
                size_mb = int(words[2]) // 1024
                disks.append({"device": device, "size_mb": size_mb})
    return disks

def get_usb_devices():
    return []  # Implementar depois

def get_network_adapters():
    return []  # Implementar depois

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
