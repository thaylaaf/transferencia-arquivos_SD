"""Script para executar a bateria completa de testes automaticamente.
Sintaxe: python experiments/run_all.py [--runs 1] [--clients 2 4 8] [--sizes 5 50 500]
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description="Executa toda a matriz de testes do experimento.")
    parser.add_argument('--sizes', nargs='+', type=int, default=[5, 50, 500], help="Tamanhos dos arquivos em MB")
    parser.add_argument('--clients', nargs='+', type=int, default=[2, 4, 8], help="Quantidades de clientes a testar")
    parser.add_argument('--runs', type=int, default=1, help="Número de repetições por configuração")
    parser.add_argument('--n-pool', type=int, default=4, help="Valor N do ThreadPool")
    args = parser.parse_args()

    print("=== 1. Gerando arquivos de teste ===")
    subprocess.run([sys.executable, str(ROOT / 'experiments' / 'generate_files.py'), '--sizes'] + [str(s) for s in args.sizes], check=True)

    print("\n=== 2. Iniciando Bateria de Experimentos ===")
    architectures = ['sequential', 'concurrent', 'pool', 'p2p']
    
    total = len(args.sizes) * len(args.clients) * len(architectures) * args.runs
    count = 0

    for size in args.sizes:
        for clients in args.clients:
            for arch in architectures:
                for r in range(1, args.runs + 1):
                    count += 1
                    print(f"\n[{count}/{total}] Executando: Arch={arch} | Size={size}MB | Clients={clients} | Run={r}")
                    cmd = [
                        sys.executable, str(ROOT / 'experiments' / 'run_experiment.py'),
                        '--architecture', arch,
                        '--file-mb', str(size),
                        '--clients', str(clients),
                        '--run', str(r)
                    ]
                    if arch == 'pool':
                        cmd += ['--n', str(args.n_pool)]
                    
                    try:
                        subprocess.run(cmd, check=True)
                    except subprocess.CalledProcessError as e:
                        print(f"ERRO ao executar a configuração {arch} {size}MB {clients} clients: {e}")

    print("\n=== 3. Gerando Resumo dos Resultados (Min, Médio, Max) ===")
    subprocess.run([sys.executable, str(ROOT / 'experiments' / 'analyze_results.py')], check=True)
    print("\n✅ Bateria de testes concluída! Confira os resultados em 'results/summary.csv'.")


if __name__ == '__main__':
    main()
