import socket
import threading
import json
import numpy as np
import psutil
from datetime import datetime

from config import HOST, BASE_PORT

class RobotNode:
    def __init__(self, name, color, is_sv=False):
        self.name = name
        self.color = color
        self.is_sv = is_sv
        self.pos = np.array([0.0, 0.0])
        self.vel = np.array([0.0, 0.0]) if is_sv else np.random.uniform(-7.0, 7.0, 2)
        
        self.id_num = 0 if is_sv else int(name[1:])
        self.port = BASE_PORT + self.id_num
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False) 
        self.sock.bind((HOST, self.port))
        
        self.current_relay_port = BASE_PORT 
        self.current_relay_name = "SV"
        self.latest_metrics = {} 
        
        self.running = True
        threading.Thread(target=self.receiver_loop, daemon=True).start()

    def get_health_metrics(self):
        battery = psutil.sensors_battery()
        return {
            "battery": battery.percent if battery else 100,
            "pos": self.pos.tolist(),
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
    
    def receiver_loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(2048)
                packet = json.loads(data.decode('utf-8'))
                
                # Message for me
                if packet['target'] == self.name and not packet['read']:
                    if 'new_relay_port' in packet['payload'] and not self.is_sv:
                        self.apply_rule(packet)  # Change route
                        
                    elif 'battery' in packet['payload'] and packet['origin'] == "SV" and not self.is_sv:
                        self.process_sv_status(packet) # SV state
                        
                    elif self.is_sv:
                        self.latest_metrics[packet['origin']] = packet['payload']
                        packet['read'] = True # Receive telemetry from Ax

                # Message to SV (not me)
                elif packet['target'] == "SV" and not self.is_sv:
                    self.sock.sendto(json.dumps(packet).encode('utf-8'), (HOST, self.current_relay_port))

            except (BlockingIOError, Exception):
                continue

    def apply_rule(self, packet):
        rule = packet['payload']
        self.current_relay_port = rule['new_relay_port']
        self.current_relay_name = rule['new_relay_name']
        packet['read'] = True 
        print(f"!!! {self.name} confirmed new relay: {self.current_relay_name}")

    def send_telemetry(self):
        packet = {
            "origin": self.name, "target": "SV",
            "payload": self.get_health_metrics(), "read": False
        }
        self.sock.sendto(json.dumps(packet).encode('utf-8'), (HOST, self.current_relay_port))
    
    def send_status_to_robot(self, target_node): # From SV to others
        if not self.is_sv:
            return 

        packet = {
            "origin": self.name, 
            "target": target_node.name, # ej. "A1"
            "payload": self.get_health_metrics(),
            "read": False
        }
        
        self.sock.sendto(json.dumps(packet).encode('utf-8'), (HOST, target_node.port))

    def process_sv_status(self, packet): # I receive from SV
        sv_data = packet['payload']
        # print(f"[{self.name}] Info recibida del SV -> Batería: {sv_data['battery']}%, Posición: {sv_data['pos']}")
        packet['read'] = True

    def stop(self):
        """Deletes the existence of the rovers and frees the sockets"""
        self.running = False
        try:
            self.sock.close()
        except Exception as e:
            print(f"Error to close socket {self.name}: {e}")
