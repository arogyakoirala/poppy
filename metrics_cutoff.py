import rasterio
import numpy as np
import pandas as pd
import os
import rioxarray as rxr
import argparse
import matplotlib.pyplot as plt
import seaborn as sns

parser = argparse.ArgumentParser()
parser.add_argument("--pred_dir", help="Preds Dir")
parser.add_argument("--csv", help="Path to ground truth CSV")
parser.add_argument("--year", help="Year")
parser.add_argument("--cluster", help="Cluster Number")
parser.add_argument("--cutoff", help="Score cutoff")
parser.add_argument("name", help="Name")

args = parser.parse_args()


scores_dir = "server/2020_2/predictions"
ground_truth_csv = "inputs/poppy_1994-2020.csv"
year = "2020"
poppy_cluster = 1
cutoff = 0.7
results_dir = "results/{args.label}"

if args.pred_dir:
    scores_dir = args.pred_dir

if args.csv:
    ground_truth_csv = args.csv

if args.year:
    year = args.year

if args.cluster:
    poppy_cluster = int(args.cluster)

if args.cutoff:
    cutoff = float(args.cutoff)

folders = [f for f in os.listdir(scores_dir) if f not in '.DS_Store']


predictions= {}
for folder in folders:
    src = rasterio.open(f'{scores_dir}/{folder}/scores.tif')
    # r = rxr.open_rasterio()
    img = src.read(poppy_cluster+1).flatten()
    poppy = (img > cutoff).sum() / 100.0


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

print("Correlation (pearson)", j['predicted_ha'].corr(j['actual_ha']))
print("Log correlation (pearson)", np.log(j['predicted_ha']).corr(np.log(j['actual_ha'])))

print("Correlation (spearman)", j['predicted_ha'].corr(j['actual_ha'], method="spearman"))
print("Log correlation (spearman)", np.log(j['predicted_ha']).corr(np.log(j['actual_ha']), method="spearman"))


j.to_csv(f"{results_dir}/acreage.csv", index=False)

fig, ax = plt.subplots(1,1,dpi=300, figsize=(15,7))
sns.scatterplot(x=j['actual_ha'], y=j['predicted_ha'])
X_plot = np.linspace(0, np.max(j['actual_ha']), 100)
plt.plot(X_plot, X_plot, color='r')
ax.set_xlabel("log(Actual Production (UNODC) in Hectares)")
ax.set_ylabel("log(Predicted Production (k-Means) in Hectares)")
plt.tight_layout()
plt.savefig(f"{results_dir}/scatterplot.png")