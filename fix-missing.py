import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("dir", help="Location of out dir to check")
args = parser.parse_args()


DIR = args.out_dir

dirs = os.listdir(DIR)
print(f"Found {len(dirs)} directories.")
for d in dirs:
    print(d)
    if f'{d}.tif' in os.listdir(d):
        print(f'Found TIF for {d}')
