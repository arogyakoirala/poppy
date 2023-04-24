import numpy as np
import pandas as pd
import os


tables_dir = "server/2020_2/tables"
ground_truth_csv = "inputs/poppy_1994-2020.csv"
year = "2020"
poppy_cluster = 1

files = os.listdir(tables_dir)

predictions= {}

for f in files: 
    d = pd.read_csv(f'{tables_dir}/{f}')
    d = d[d['cluster']==poppy_cluster]
    if len(d) > 0:
        acreage = d['clustering_ha'].to_numpy()[0]
        dist_id = f.split("_")[0]
        if dist_id in predictions:
            predictions[dist_id] += acreage
        else:
            predictions[dist_id] = acreage

df = []
for k in predictions:
    df_ = {}
    df_['distid'] = k
    df_['predicted_ha'] = predictions[k]
    df.append(df_)

df = pd.DataFrame(df)
df['distid'] = df['distid'].astype(int)
# print(df)


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


