import argparse
import json
import socket
import threading
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.protocol import send_json, recv_json

peers = {}
lock = threading.Lock()


def handle(conn):
    try:
        with conn:
            req = recv_json(conn)
            typ = req.get('type')
            with lock:
                if typ == 'register':
                    peers[req['peer_id']] = {
                        'host': req['host'], 'port': int(req['port']),
                        'size': int(req['size']), 'chunks': int(req['chunks']),
                        'have': set(req.get('have', [])),
                    }
                    send_json(conn, {'type':'ok'})
                elif typ == 'update':
                    if req['peer_id'] in peers:
                        peers[req['peer_id']]['have'].add(int(req['chunk']))
                    send_json(conn, {'type':'ok'})
                elif typ == 'list':
                    result=[]
                    for pid,p in peers.items():
                        result.append({'peer_id':pid,'host':p['host'],'port':p['port'],'have':list(p['have'])})
                    send_json(conn, {'type':'peers','peers':result})
                elif typ == 'unregister':
                    peers.pop(req['peer_id'],None); send_json(conn, {'type':'ok'})
                else:
                    send_json(conn, {'type':'error','message':'tipo desconhecido'})
    except Exception as e:
        print(f'TRACKER_ERROR {e}', flush=True)


def main():
    p=argparse.ArgumentParser(); p.add_argument('--host',default='0.0.0.0'); p.add_argument('--port',type=int,default=6000); args=p.parse_args()
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1); s.bind((args.host,args.port)); s.listen()
        print(f'TRACKER_READY {args.port}',flush=True)
        while True:
            c,_=s.accept(); threading.Thread(target=handle,args=(c,),daemon=True).start()

if __name__=='__main__': main()
