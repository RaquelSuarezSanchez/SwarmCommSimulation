import numpy as np

HOST = '127.0.0.1'
BASE_PORT = 15000
UMBRAL = 50.0 
SIM_TIME = 25 
DT = 0.1 
EXPLORATION_RADIUS = 8.0

MAP_FILE = "n29_w014_1arc_v3_Caldera_Blanca.dt2" 

def get_dist(p1, p2):
    return np.sqrt(np.sum((p1 - p2)**2))