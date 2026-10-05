# Avaliação de Desempenho: Cliente-Servidor e P2P

Este repositório contém a implementação e a suite de testes para a avaliação de desempenho no processo de transferência de arquivos, comparando diferentes variações da arquitetura **Cliente-Servidor** e uma arquitetura **Peer-to-Peer (P2P)**.

---

## 📌 Arquiteturas Implementadas

### 1. Cliente-Servidor — Sequencial (1 por vez)
* **Arquivo:** `client_server/server_sequential.py`
* **Descrição:** O servidor atende um único download de cada vez de forma síncrona. Clientes adicionais aguardam na fila de conexões TCP até que o cliente anterior conclua.

### 2. Cliente-Servidor — Concorrente (Thread por cliente)
* **Arquivo:** `client_server/server_concurrent.py`
* **Descrição:** Para cada nova conexão de cliente, o servidor dispara uma nova thread (`threading.Thread`) dedicada para realizar a transferência de forma simultânea.

### 3. Cliente-Servidor — Limite N (Pool de Threads)
* **Arquivo:** `client_server/server_pool.py`
* **Descrição:** O servidor utiliza um pool de threads gerenciado via `ThreadPoolExecutor(max_workers=N)`. Atende até no máximo $N$ clientes simultâneos; requisições excedentes aguardam no pool.

### 4. Arquitetura P2P (Peer-to-Peer)
* **Arquivos:** `p2p/tracker.py` e `p2p/peer.py`
* **Descrição:**
  * **Tracker:** Servidor centralizado leve apenas para registro de presenças e controle do catálogo de peers ativos e blocos disponíveis.
  * **Peers:** O arquivo é fatiado em blocos (ex: 1 MB). Um nó inicial (`seed`) disponibiliza o arquivo completo. À medida que outros peers baixam blocos, eles registram no tracker e passam a disponibilizar esses blocos para download por outros peers na rede.

---

## 📂 Estrutura do Projeto

```text
p2p_transfer_project/
├── client_server/             # Scripts dos servidores e cliente CS
│   ├── client.py              # Cliente CS (descarte de dados na memória)
│   ├── server_sequential.py   # Servidor 1 cliente por vez
│   ├── server_concurrent.py   # Servidor Thread por cliente
│   └── server_pool.py         # Servidor Pool de Threads (N)
├── p2p/                       # Scripts da arquitetura P2P
│   ├── tracker.py             # Rastreador de catálogo de peers
│   └── peer.py                # Nó peer (download/upload de blocos)
├── common/                    # Protocolos e utilitários compartilhados
│   ├── file_utils.py          # Gerador e manipulador de arquivos
│   ├── protocol.py            # Protocolo TCP customizado em JSON + binário
│   └── stats.py               # Cálculos estatísticos (Min, Média, Max)
├── experiments/               # Scripts de automação de testes
│   ├── generate_files.py      # Gerador dos arquivos de 5MB, 50MB e 500MB
│   ├── run_experiment.py      # Executor de um experimento individual
│   ├── run_all.py             # Executor automático de toda a matriz de testes
│   └── analyze_results.py     # Processador estatístico dos resultados
├── data/                      # Armazenamento dos arquivos binários de teste
├── results/                   # Resultados brutos e estatísticas geradas
└── docs/                      # Modelo e documentação do relatório
```

---

## 🛠️ Requisitos e Pré-requisitos

* **Python 3.10** ou superior.
* Apenas bibliotecas padrão do Python (não requer `pip install` de pacotes externos).

---

## 🚀 Como Executar os Experimentos

### Opção A: Executar toda a Bateria de Testes Automática (Recomendado)

1. Para gerar os arquivos de teste (5MB, 50MB, 500MB), executar todas as 4 arquiteturas variando o número de clientes e calcular o resumo estatístico, rode:

```bash
python experiments/run_all.py
```

Você pode customizar os parâmetros se desejar:
```bash
python experiments/run_all.py --sizes 5 50 500 --clients 2 4 8 --runs 3 --n-pool 4
```

---

### Opção B: Executar Experimentos Individuais Manualmente

#### 1. Gerar os arquivos de teste:
```bash
python experiments/generate_files.py
```

#### 2. Rodar uma configuração específica:
```bash
# Cliente-Servidor Sequencial (5MB com 4 clientes)
python experiments/run_experiment.py --architecture sequential --file-mb 5 --clients 4 --run 1

# Cliente-Servidor Concorrente (5MB com 4 clientes)
python experiments/run_experiment.py --architecture concurrent --file-mb 5 --clients 4 --run 1

# Cliente-Servidor Pool N (5MB com 4 clientes e N=4)
python experiments/run_experiment.py --architecture pool --file-mb 5 --clients 4 --n 4 --run 1

# P2P (5MB com 4 clientes)
python experiments/run_experiment.py --architecture p2p --file-mb 5 --clients 4 --run 1
```

#### 3. Processar estatísticas dos resultados:
```bash
python experiments/analyze_results.py
```

---

## 📊 Resultados e Métricas

Os dados brutos coletados são armazenados em `results/raw_results.csv`. 

Após a execução do script `analyze_results.py`, o arquivo `results/summary.csv` é gerado com as seguintes estatísticas por configuração:
* **`min_s`**: Tempo Mínimo de conclusão da transferência (em segundos).
* **`mean_s`**: Tempo Médio de conclusão da transferência (em segundos).
* **`max_s`**: Tempo Máximo de conclusão da transferência (em segundos).

---
