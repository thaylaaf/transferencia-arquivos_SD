import argparse
import socket
import time
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.protocol import send_json, send_file, recv_json


def handle(conn, file_path):
    with conn:
        request = recv_json(conn)
        if request.get('type') != 'download':
            return
        size = file_path.stat().st_size
        send_json(conn, {'type': 'file', 'size': size, 'name': file_path.name})
        send_file(conn, file_path)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--host', default='0.0.0.0')
    p.add_argument('--port', type=int, default=5001)
    p.add_argument('--file', required=True)
    args = p.parse_args()
    path = Path(args.file)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((args.host, args.port)); s.listen()
        print(f'SEQ_READY {args.port}', flush=True)
        while True:
            conn, _ = s.accept()
            try:
                handle(conn, path)
            except Exception as e:
                print(f'ERRO: {e}', flush=True)

if __name__ == '__main__':
    main()
