import argparse
import socket
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.protocol import send_json, send_file, recv_json


def handle(conn, file_path):
    try:
        with conn:
            request=recv_json(conn)
            if request.get('type')!='download': return
            send_json(conn, {'type':'file','size':file_path.stat().st_size,'name':file_path.name})
            send_file(conn,file_path)
    except Exception as e:
        print(f'ERRO_POOL: {e}', flush=True)


def main():
    p=argparse.ArgumentParser(); p.add_argument('--host',default='0.0.0.0'); p.add_argument('--port',type=int,default=5003)
    p.add_argument('--file',required=True); p.add_argument('--max-clients',type=int,required=True)
    args=p.parse_args(); path=Path(args.file)
    if args.max_clients < 1: raise SystemExit('--max-clients deve ser >= 1')
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1); s.bind((args.host,args.port)); s.listen()
        print(f'POOL_READY {args.port} N={args.max_clients}',flush=True)
        with ThreadPoolExecutor(max_workers=args.max_clients) as pool:
            while True:
                conn,_=s.accept(); pool.submit(handle,conn,path)

if __name__=='__main__': main()
