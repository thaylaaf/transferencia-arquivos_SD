import json
import socket
import struct

HEADER = struct.Struct('!Q')
CHUNK_SIZE = 64 * 1024


def send_json(sock, payload):
    data = json.dumps(payload).encode('utf-8')
    sock.sendall(HEADER.pack(len(data)))
    sock.sendall(data)


def recv_exact(sock, size):
    chunks = []
    remaining = size
    while remaining:
        chunk = sock.recv(min(CHUNK_SIZE, remaining))
        if not chunk:
            raise ConnectionError('Conexão encerrada antes do recebimento completo.')
        chunks.append(chunk)
        remaining -= len(chunk)
    return b''.join(chunks)


def recv_json(sock):
    raw = recv_exact(sock, HEADER.size)
    (size,) = HEADER.unpack(raw)
    if size > 10 * 1024 * 1024:
        raise ValueError('Mensagem de controle excede o limite permitido.')
    return json.loads(recv_exact(sock, size).decode('utf-8'))


def send_file(sock, path):
    with open(path, 'rb') as f:
        while True:
            data = f.read(CHUNK_SIZE)
            if not data:
                break
            sock.sendall(data)


def receive_and_discard(sock, size):
    remaining = size
    received = 0
    while remaining:
        data = sock.recv(min(CHUNK_SIZE, remaining))
        if not data:
            raise ConnectionError('Conexão encerrada durante a transferência.')
        received += len(data)
        remaining -= len(data)
    return received
