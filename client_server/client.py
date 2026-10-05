import argparse
import socket
import time
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.protocol import recv_json, receive_and_discard


def download(host, port):
    start=time.perf_counter()
    with socket.create_connection((host,port),timeout=60) as s:
        from common.protocol import send_json
        send_json(s, {'type':'download'})
        meta=recv_json(s)
        received=receive_and_discard(s, meta['size'])
    elapsed=time.perf_counter()-start
    return {'seconds':elapsed,'bytes':received,'file':meta.get('name','')}


def main():
    p=argparse.ArgumentParser(); p.add_argument('--host',default='127.0.0.1'); p.add_argument('--port',type=int,required=True); args=p.parse_args()
    r=download(args.host,args.port); print(f"CLIENT_RESULT seconds={r['seconds']:.6f} bytes={r['bytes']} file={r['file']}",flush=True)

if __name__=='__main__': main()
