import argparse
import math
import socket
import threading
import time
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.protocol import send_json, recv_json, recv_exact, HEADER, CHUNK_SIZE


def tracker_request(host, port, payload):
    with socket.create_connection((host,port),timeout=10) as s:
        send_json(s,payload); return recv_json(s)


def serve_chunk(server, path, chunk_size, has_all, chunk_count, have_set, lock):
    while True:
        conn,_=server.accept()
        try:
            with conn:
                req=recv_json(conn)
                if req.get('type')!='get_chunk':
                    send_json(conn,{'type':'error'}); continue
                idx=int(req['chunk'])
                with lock:
                    available = has_all or idx in have_set
                if not available:
                    send_json(conn,{'type':'missing'}); continue
                offset=idx*chunk_size
                length=min(chunk_size, max(0, path.stat().st_size-offset))
                send_json(conn,{'type':'chunk','chunk':idx,'size':length})
                with path.open('rb') as f:
                    f.seek(offset)
                    remaining=length
                    while remaining:
                        data=f.read(min(CHUNK_SIZE,remaining))
                        if not data: raise ConnectionError('fim prematuro')
                        conn.sendall(data); remaining-=len(data)
        except Exception as e:
            print(f'PEER_SERVER_ERROR {e}',flush=True)


def get_peers(thost,tport):
    return tracker_request(thost,tport,{'type':'list'}).get('peers',[])


def fetch_chunk(peer, chunk_idx):
    with socket.create_connection((peer['host'],peer['port']),timeout=30) as s:
        send_json(s,{'type':'get_chunk','chunk':chunk_idx})
        meta=recv_json(s)
        if meta.get('type')!='chunk': raise RuntimeError('chunk indisponível')
        return recv_exact(s,meta['size'])


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--peer-id',required=True); p.add_argument('--tracker-host',default='127.0.0.1'); p.add_argument('--tracker-port',type=int,default=6000)
    p.add_argument('--listen-host',default='0.0.0.0'); p.add_argument('--advertise-host',default='127.0.0.1',help='IP/nome que os outros peers usarão para conectar')
    p.add_argument('--listen-port',type=int,required=True)
    p.add_argument('--file',required=True); p.add_argument('--size',type=int,required=True,help='tamanho esperado em bytes')
    p.add_argument('--seed',action='store_true'); p.add_argument('--chunk-size',type=int,default=1024*1024)
    args=p.parse_args(); path=Path(args.file); path.parent.mkdir(parents=True,exist_ok=True)
    chunk_count=math.ceil(args.size/args.chunk_size)
    have=set(range(chunk_count)) if args.seed else set()
    if not args.seed:
        with path.open('wb') as f: f.truncate(args.size)
    lock=threading.Lock()
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1); server.bind((args.listen_host,args.listen_port)); server.listen()
        threading.Thread(target=serve_chunk,args=(server,path,args.chunk_size,args.seed,chunk_count,have,lock),daemon=True).start()
        tracker_request(args.tracker_host,args.tracker_port,{'type':'register','peer_id':args.peer_id,'host':args.advertise_host,'port':args.listen_port,'size':args.size,'chunks':chunk_count,'have':list(have)})
        print(f'PEER_READY {args.peer_id} {args.listen_port}',flush=True)
        if args.seed:
            # Seed stays alive and serves chunks; it is not a download participant.
            while True: time.sleep(60)
        start=time.perf_counter()
        try:
            remaining=set(range(chunk_count))-have
            while remaining:
                peers=get_peers(args.tracker_host,args.tracker_port)
                progress=False
                for idx in list(remaining):
                    candidates=[x for x in peers if x['peer_id']!=args.peer_id and idx in x.get('have',[])]
                    if not candidates: continue
                    peer=candidates[idx % len(candidates)]
                    try:
                        data=fetch_chunk(peer,idx)
                        offset=idx*args.chunk_size
                        with path.open('r+b') as f:
                            f.seek(offset); f.write(data)
                        with lock: have.add(idx)
                        tracker_request(args.tracker_host,args.tracker_port,{'type':'update','peer_id':args.peer_id,'chunk':idx})
                        remaining.remove(idx); progress=True
                    except Exception:
                        continue
                if not progress:
                    time.sleep(0.05)
            elapsed=time.perf_counter()-start
            print(f'PEER_RESULT peer={args.peer_id} seconds={elapsed:.6f} bytes={args.size}',flush=True)
        finally:
            try: tracker_request(args.tracker_host,args.tracker_port,{'type':'unregister','peer_id':args.peer_id})
            except Exception: pass

if __name__=='__main__': main()
