import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean

def main():
    parser = argparse.ArgumentParser(description="Analisa os resultados brutos e gera o CSV formatado para o Excel.")
    parser.add_argument('--input', default='results/raw_results.csv', help="Caminho do arquivo de dados brutos")
    parser.add_argument('--output', default='results/summary.csv', help="Caminho de saida para o CSV formatado para o Excel")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Erro: O arquivo '{input_path}' nao foi encontrado. Execute os experimentos primeiro.")
        return

    groups = defaultdict(list)
    with open(input_path, newline='', encoding='utf-8') as f:
        sample = f.read(2048)
        f.seek(0)
        delimiter = ';' if ';' in sample and ',' not in sample else ','
        reader = csv.DictReader(f, delimiter=delimiter)
        for r in reader:
            arch = r['architecture']
            file_mb = r['file_mb']
            clients = r['clients']
            sec = float(r['seconds'].replace(',', '.'))
            groups[(arch, file_mb, clients)].append(sec)

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Salva diretamente no CSV formatado para o Excel (separador ';' e virgula decimal)
    try:
        with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
            f.write("sep=;\n")
            w = csv.writer(f, delimiter=';')
            w.writerow(['Arquitetura', 'Tamanho_MB', 'Clientes', 'Tempo_Minimo_s', 'Tempo_Medio_s', 'Tempo_Maximo_s'])
            for key, times in sorted(groups.items()):
                min_val = f"{min(times):.6f}".replace('.', ',')
                mean_val = f"{mean(times):.6f}".replace('.', ',')
                max_val = f"{max(times):.6f}".replace('.', ',')
                w.writerow([*key, min_val, mean_val, max_val])
        print(f"Resumo para o Excel salvo com sucesso em: {out_path}")
    except PermissionError:
        print(f"ATENCAO: Nao foi possivel salvar '{out_path}' pois ele esta aberto no Excel. Feche o arquivo no Excel e execute novamente.")

if __name__ == '__main__':
    main()
