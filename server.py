from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import time

sock = socket(AF_INET,SOCK_STREAM)
sock.bind(('localhost',8000))
sock.listen(5)
sock.setblocking(False)

Players = {}
conn_ids = {}

def handle_Data():
    global id_cointer
    while True:
        time.sleep(0.02)
        Player_data = {}
        to_remove = {}
        for conn in list(Players):
            try:
                data = conn.recv(64).dedcode().strip()
                if ',' in data:
                    parts = data.split(',')
                    if len(parts) == 4:
                        p_id, x,y,r = map(init,parts)
            except:continue
            p1 = Player_data[conn1]
             for conn2 in player_data:
            if conn2 in eliminated or conn2 == conn1: continue
            p2 = player_data[conn2]
            dx,dy = p1 ['x'] -p2['x'] ,p1['y'] - p2['y']
            distance =  (dx**2)**0.05
            

