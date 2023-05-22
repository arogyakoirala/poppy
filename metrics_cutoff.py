import rasterio
import numpy as np
import pandas as pd
import os
import rioxarray as rxr
import argparse
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--pred_dir", help="Preds Dir")
parser.add_argument("--csv", help="Path to ground truth CSV")
parser.add_argument("--year", help="Year")
parser.add_argument("--cluster", help="Cluster Number")
parser.add_argument("--cutoff", help="Score cutoff")
parser.add_argument("name", help="Name")

args = parser.parse_args()


preds_dir = "server/2020_2/predictions"
ground_truth_csv = "inputs/poppy_1994-2020.csv"
year = "2020"
poppy_cluster = 0
cutoff = 0.7
results_dir = f"results/{args.name}"

Path(results_dir).mkdir(exist_ok=True, parents=True)

if args.pred_dir:
    preds_dir = args.pred_dir

if args.csv:
    ground_truth_csv = args.csv

if args.year:
    year = args.year

if args.cluster:
    poppy_cluster = int(args.cluster)

if args.cutoff:
    cutoff = float(args.cutoff)

folders = [f for f in os.listdir(preds_dir) if f not in '.DS_Store']


subset_dict = {
    "2019_3": [2308,2302,2306,2304,2303,2407,2307,2311,1906,1905,2601,2312,2605,2105,1608,1606,2416,2313,1115,2604,2301,2205,2305,3106,2106,2111,2415,1607,1116,2706,809,2406,2408,2603,804,1711,2705],
    "2019_2": [1103,2309,1903,1803,1904,2405,813,2102,905,805,1102,1124,2103,3404,1808,1907,2602,1015,2006,3101,1014,1703,1701,3102,1804,2404,3409,112,901,815,2505,2709,903,1302,2707,3402],
    "2020_3": [2308,2302,2306,2304,1906,2303,2407,1905,2311,2307,1903,2601,2105,2312,2313,1904,1115,2416,2605,2205,2604,2106,1608,2305,2415,1606,3106,2111,1803,2705,2301,1607,805,1116,2603,2406,2309,2408,2103,2405],
    "2021_3": [2308,2302,2304,2309,2303,2311,2407,2307,2105,2312,2313,2106,2601,2605,1905,1906,2415,2305,2205,2604,1115,2301,2111,2306,2416,1904,3106,2405,2406,2705,2506,804,805,1607,2103,1608,1606,2403,1116]
}

subsets = [f for f in folders if int(f.split("_")[0]) in subset_dict("2019_3") ]
print("Subsets", subsets)


predictions= {}
for folder in folders:
    src = rasterio.open(f'{preds_dir}/{folder}/scores.tif')
    # r = rxr.open_rasterio()
    img = src.read(poppy_cluster+1).flatten()
    poppy = (img > cutoff).sum() / 100.0

    print(folder)
    dist_id = folder.split("_")[0]
    if dist_id in predictions:
            predictions[dist_id] += poppy
    else:
        predictions[dist_id] = poppy


df = []
for k in predictions:
    df_ = {}
    df_['distid'] = k
    df_['predicted_ha'] = predictions[k]
    df.append(df_)

df = pd.DataFrame(df)
df['distid'] = df['distid'].astype(int)


gt = pd.read_csv(ground_truth_csv)
gt = gt[['distid', f'X{year}']]
gt.columns = ['distid', 'actual_ha']
gt = gt.dropna()

j = pd.merge(gt, df)
j['year'] = year
j['ratio'] = j['predicted_ha']/j['actual_ha']
print(j.sort_values(by='actual_ha', ascending=False))
j.to_csv(f"{results_dir}/acreage.csv", index=False)

print("Correlation (pearson)", j['predicted_ha'].corr(j['actual_ha']))
print("Log correlation (pearson)", np.log(j['predicted_ha']).corr(np.log(j['actual_ha'])))

print("Correlation (spearman)", j['predicted_ha'].corr(j['actual_ha'], method="spearman"))
print("Log correlation (spearman)", np.log(j['predicted_ha']).corr(np.log(j['actual_ha']), method="spearman"))


f = open(f"{results_dir}/correlations.txt", "w")
f.write(f"Correlation (pearson): {j['predicted_ha'].corr(j['actual_ha'])}\n")
f.write(f"Log Correlation (pearson): {np.log(j['predicted_ha']).corr(np.log(j['actual_ha']))}\n")
f.write(f"Correlation (spearman): {j['predicted_ha'].corr(j['actual_ha'], method='spearman')}\n")
f.write(f"Log Correlation (spearman): {np.log(j['predicted_ha']).corr(np.log(j['actual_ha']), method='spearman')}\n")
f.close()

fig, ax = plt.subplots(1,1,dpi=300, figsize=(15,7))
sns.scatterplot(x=j['actual_ha'], y=j['predicted_ha'])
X_plot = np.linspace(0, np.max(j['actual_ha']), 100)
plt.plot(X_plot, X_plot, color='r')
ax.set_xlabel("Actual Production (UNODC) in Hectares")
ax.set_ylabel("Predicted Production (k-Means) in Hectares")
plt.tight_layout()
plt.savefig(f"{results_dir}/scatterplot.png")