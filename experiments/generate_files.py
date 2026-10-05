import argparse
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))
from common.file_utils import create_test_file

p=argparse.ArgumentParser(); p.add_argument('--sizes',nargs='+',type=int,default=[5,50,500]); p.add_argument('--out',default='data')
args=p.parse_args()
for size in args.sizes:
    path=create_test_file(Path(args.out)/f'arquivo_{size}MB.bin',size)
    print(f'{path} criado ({size} MB)')
