import zarr
import argparse
import os
import math

parser = argparse.ArgumentParser()
parser.add_argument("dir", help="Location of root dir.")
args = parser.parse_args()




def make_tuple_pair(n, step_size):
    if step_size > n:
        return [(0,n)]
    iters = math.ceil(n/step_size*1.0)
    l = []
    for i in range(0, iters):
        if i == iters - 1:
            t = (i*step_size, n)
            l.append(t)
        else:
            t = (i*step_size, (i+1)*step_size)
            l.append(t)
    return l



DIR = args.dir
dirs = os.listdir(DIR)

print(f"Accumulating: {DIR}")

os.system(f"rm -rf {DIR}/sample.zarr")

for _dir in dirs:
    if os.path.exists(f"{DIR}/{_dir}/sample.zarr"):
        f = zarr.open(f"{DIR}/{_dir}/sample.zarr")
        pairs = make_tuple_pair(f.shape[0], 10000)
        print(f.shape)
        for pair in pairs:
            if os.path.exists(f'{DIR}/sample.zarr'):
                z = zarr.open(f'{DIR}/sample.zarr', mode='a')
                z.append(f[pair[0]:pair[1]])
            else:
                zarr.save(f'{DIR}/sample.zarr', f[pair[0]:pair[1]]) 

print("#### Final sample size: ", zarr.open(f'{DIR}/sample.zarr').shape)

