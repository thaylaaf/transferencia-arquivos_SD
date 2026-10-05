"""Executa uma configuração experimental local e registra os tempos.

Exemplo:
python experiments/run_experiment.py --architecture sequential --file-mb 5 --clients 4 --run 1
python experiments/run_experiment.py --architecture concurrent --file-mb 5 --clients 4 --run 1
python experiments/run_experiment.py --architecture pool --file-mb 5 --clients 8 --n 4 --run 1
python experiments/run_experiment.py --architecture p2p --file-mb 5 --clients 4 --run 1
"""
import argparse
import csv
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
RESULTS = ROOT / 'results'
RAW = RESULTS / 'raw_results.csv'


def free_port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


def wait_ready(proc, pattern, timeout=10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        line = proc.stdout.readline()
        if line:
            print(line.rstrip())
            if re.search(pattern, line):
                return
        elif proc.poll() is not None:
            raise RuntimeError(f'Processo terminou prematuramente: {proc.returncode}')
    raise TimeoutError(f'Não foi recebido o sinal de inicialização: {pattern}')


def start(cmd):
    return subprocess.Popen(cmd, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)


def stop(proc):
    if proc and proc.poll() is None:
        proc.terminate()
        try: proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill(); proc.wait()


def parse_line(lines, prefix):
    for line in lines:
        if line.startswith(prefix):
            return line
    raise RuntimeError(f'Resultado não encontrado: {prefix}')


def run_client_server(kind, file_path, clients, n=None):
    ports = {'sequential': 5101, 'concurrent': 5102, 'pool': 5103}
    port = ports[kind]
    script = {'sequential':'client_server/server_sequential.py','concurrent':'client_server/server_concurrent.py','pool':'client_server/server_pool.py'}[kind]
    cmd=[sys.executable,script,'--file',str(file_path),'--port',str(port)]
    if kind=='pool': cmd += ['--max-clients',str(n)]
    server=start(cmd)
    results=[]
    try:
        wait_ready(server, r'_READY')
        procs=[start([sys.executable,'client_server/client.py','--host','127.0.0.1','--port',str(port)]) for _ in range(clients)]
        for i,p in enumerate(procs,1):
            out,_=p.communicate(timeout=300)
            print(out.rstrip())
            m=re.search(r'CLIENT_RESULT seconds=([0-9.]+) bytes=(\d+)',out)
            if not m: raise RuntimeError(f'Cliente {i} não retornou resultado: {out}')
            results.append((f'client{i}',float(m.group(1))))
    finally:
        stop(server)
    return results


def run_p2p(file_path, file_mb, clients, run_id):
    tracker_port=free_port()
    tracker=start([sys.executable,'p2p/tracker.py','--port',str(tracker_port)])
    peers=[]
    tempdir=ROOT/'data'/'p2p_runtime'
    tempdir.mkdir(exist_ok=True)
    try:
        wait_ready(tracker,r'TRACKER_READY')
        seed_port=free_port()
        seed=start([sys.executable,'p2p/peer.py','--peer-id',f'seed_{run_id}','--listen-host','127.0.0.1','--advertise-host','127.0.0.1','--listen-port',str(seed_port),'--tracker-port',str(tracker_port),'--file',str(file_path),'--size',str(file_mb*1024*1024),'--seed'])
        peers.append(seed)
        wait_ready(seed,r'PEER_READY')
        procs=[]
        for i in range(1,clients+1):
            port=free_port(); out=tempdir/f'peer_{run_id}_{i}_{file_mb}MB.bin'
            p=start([sys.executable,'p2p/peer.py','--peer-id',f'peer_{run_id}_{i}','--listen-host','127.0.0.1','--advertise-host','127.0.0.1','--listen-port',str(port),'--tracker-port',str(tracker_port),'--file',str(out),'--size',str(file_mb*1024*1024)])
            procs.append(p); peers.append(p)
        results=[]
        for i,p in enumerate(procs,1):
            out,_=p.communicate(timeout=600)
            print(out.rstrip())
            m=re.search(r'PEER_RESULT peer=.* seconds=([0-9.]+)',out)
            if not m: raise RuntimeError(f'Peer {i} não retornou resultado: {out}')
            results.append((f'peer{i}',float(m.group(1))))
        return results
    finally:
        for p in peers: stop(p)
        stop(tracker)
        # Limpeza automática de arquivos temporários do P2P
        if tempdir.exists():
            for f in tempdir.glob('*.bin'):
                try: f.unlink()
                except Exception: pass


def append_results(rows):
    RESULTS.mkdir(exist_ok=True)
    exists=RAW.exists()
    with RAW.open('a',newline='',encoding='utf-8') as f:
        w=csv.writer(f)
        if not exists: w.writerow(['architecture','file_mb','clients','run','client_id','seconds'])
        w.writerows(rows)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--architecture',choices=['sequential','concurrent','pool','p2p'],required=True)
    p.add_argument('--file-mb',type=int,required=True)
    p.add_argument('--clients',type=int,required=True)
    p.add_argument('--run',type=int,default=1)
    p.add_argument('--n',type=int,default=4)
    args=p.parse_args()
    if args.clients<1 or args.file_mb<1: raise SystemExit('clients e file-mb devem ser >= 1')
    if args.architecture=='pool' and args.n<1: raise SystemExit('N deve ser >= 1')
    file_path=DATA/f'arquivo_{args.file_mb}MB.bin'
    if not file_path.exists():
        raise SystemExit(f'Arquivo não encontrado: {file_path}. Execute generate_files.py.')
    if args.architecture=='p2p':
        results=run_p2p(file_path,args.file_mb,args.clients,args.run)
    else:
        results=run_client_server(args.architecture,file_path,args.clients,args.n)
    rows=[(args.architecture if args.architecture!='pool' else f'pool_n{args.n}',args.file_mb,args.clients,args.run,cid,seconds) for cid,seconds in results]
    append_results(rows)
    print('Resultados registrados em',RAW)

if __name__=='__main__': main()
