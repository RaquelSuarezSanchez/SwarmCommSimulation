import numpy as np
import matplotlib.pyplot as plt
import json
import os

from RobotNode import RobotNode
from config import get_dist

def get_user_inputs(cx, cy, config_file=None):
    if config_file is not None:
        if os.path.exists(config_file):
            parametros = _extract_arguments_file(cx, cy, config_file)
            if parametros is not None:
                return parametros
        else:
            print(f"\n[!] File {config_file} does not exist.")
            
    return _extract_arguments_console(cx, cy)

def _extract_arguments_console(cx, cy):
    print("\n[!] Starting manual configuration...")
    try:
        entrada_n = input('Introduce number of rovers (between 3 and 7), by default 3: ')
        N = int(entrada_n) if entrada_n.strip() != "" else 3
    except ValueError:
        N = 3

    sv_input = input('Offset X,Y of SV in meters (Ex: 100, -50 or enter for center): ')
    if sv_input.strip() == "":
        sv_x, sv_y = cx, cy
    else:
        try:
            partes = sv_input.split(',')
            sv_x = cx + float(partes[0].strip())
            sv_y = cy + float(partes[1].strip())
        except (ValueError, IndexError):
            print("Incorrect format. Using default coordinates.")
            sv_x, sv_y = cx, cy

    area_input = input('Introduce size of exploration area in meters (Ex: 120) [by default 120]: ')
    try:
        play_area_size = float(area_input) if area_input.strip() != "" else 120.0
    except ValueError:
        print("Incorrect format. Using 120 meters by default.")
        play_area_size = 120.0

    modo_input = input('Choose exploration mode (1: Free, 2: Fixed) [by default 2]: ')
    modo = 1 if modo_input.strip() == "1" else 2

    return N, sv_x, sv_y, play_area_size, modo

def _extract_arguments_file(cx, cy, config_file):
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print(f"\n[+] Loading data from file: {config_file}")
        
        N = config.get("num_rovers", 3)
        desplazamiento_x = config.get("offset_sv_x", 0.0)
        desplazamiento_y = config.get("offset_sv_y", 0.0)
        sv_x = cx + desplazamiento_x
        sv_y = cy + desplazamiento_y
        play_area_size = config.get("area_size", 120.0)
        modo = config.get("exploration_mode", 1)
        
        return N, sv_x, sv_y, play_area_size, modo
        
    except Exception as e:
        print(f"\n[!] Error reading file: {e}")
        return None


def create_robots(N, sv_x, sv_y):
    cmap = plt.get_cmap('tab10')
    colors = [cmap(i) for i in range(N + 1)]

    robots = [RobotNode("SV", colors[0], is_sv=True)]
    robots[0].pos = np.array([sv_x, sv_y]) 

    for i in range(1, N + 1):
        r = RobotNode(f"A{i}", colors[i])
        r.pos = np.array([sv_x + np.random.uniform(-5, 5), sv_y + np.random.uniform(-5, 5)])
        
        vector_inicio = r.pos - robots[0].pos 
        angulo_inicio = np.arctan2(vector_inicio[1], vector_inicio[0])
        speed = np.linalg.norm(r.vel) if hasattr(r, 'vel') else 1.0
        new_angle = np.random.uniform(angulo_inicio - np.pi/4, angulo_inicio + np.pi/4)
        r.vel = np.array([np.cos(new_angle), np.sin(new_angle)]) * speed
        
        robots.append(r)
        robots[0].latest_metrics[f"A{i}"] = {"battery": 100}
        
    return robots

def build_routing_tree(robots, sv, umbral): #BFS
    assigned_relays = {}
    visitados = {sv.name}
    cola = [sv]
    
    while cola:
        nodo_actual = cola.pop(0)
        
        # Robots within reach of current rover
        for vecino in robots:
            # If neighbour hasn't been visited yet, it is a candidate.
            if vecino.name not in visitados:
                distancia = get_dist(nodo_actual.pos, vecino.pos)
                
                if distancia < umbral:
                    batt = sv.latest_metrics.get(nodo_actual.name, {}).get('battery', 100)
                    if nodo_actual.is_sv or batt > 20:
                        visitados.add(vecino.name)
                        assigned_relays[vecino.name] = nodo_actual.name
                        cola.append(vecino)
                        
    return assigned_relays

def update_network_relays(robots, sv, assigned_relays, new_assigned_relays, host):
    """Update relays, send update commands, change directions."""
    for r in robots:
        if r.is_sv: continue
        new_relay_name = new_assigned_relays[r.name]
        
        if assigned_relays[r.name] != new_relay_name:
            assigned_relays[r.name] = new_relay_name

            # Robots change directions after changing relays
            speed = np.linalg.norm(r.vel) 
            vector_alejamiento = r.pos - sv.pos 
            angulo_base = np.arctan2(vector_alejamiento[1], vector_alejamiento[0])
            new_angle = np.random.uniform(angulo_base - np.pi/2, angulo_base + np.pi/2)
            r.vel = np.array([np.cos(new_angle), np.sin(new_angle)]) * speed

            nuevo_rele_obj = next(rob for rob in robots if rob.name == new_relay_name)
            cmd = {"origin": "SV", "target": r.name, "read": False,
                   "payload": {"new_relay_port": nuevo_rele_obj.port, "new_relay_name": new_relay_name}}
            sv.sock.sendto(json.dumps(cmd).encode('utf-8'), (host, r.port))

def update_robots_movement(robots, current_strategy, exp_map, x_lims, y_lims, DT, EXPLORATION_RADIUS, active_relays):
    """Manage rovers' movements and send telemetry. Return True if map was expanded this time."""
    map_expanded_this_time = False
    sv = robots[0]

    for r in robots:
        if not r.is_sv:
            if r.name not in active_relays:
               if current_strategy.manageMove(r, exp_map, x_lims, y_lims, DT, EXPLORATION_RADIUS):
                    map_expanded_this_time = True
            
            r.send_telemetry()
            sv.send_status_to_robot(r)
            exp_map.update(r.pos, radius=EXPLORATION_RADIUS)
            
    return map_expanded_this_time

def process_network_turn(robots, sv, assigned_relays, UMBRAL, host):
    """ Calculate new routes, check disconnections. Return True if someone disconnected."""
    new_assigned_relays = build_routing_tree(robots, sv, UMBRAL) 
    disconnected = []
    
    for r in robots:
        if not r.is_sv and r.name not in new_assigned_relays:
            disconnected.append(r.name)

    if disconnected:
        names_disc = ", ".join(disconnected)
        return True, f"The robots {names_disc} have lost connection (no possible way to SV)."

    update_network_relays(robots, sv, assigned_relays, new_assigned_relays, host)
    return False, ""