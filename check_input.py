import pandas as pd

df = pd.read_csv('outputs/team_season_xt_clustering_features.csv')
cols = [c for c in df.columns if 'smooth_created_z' in c]

print(f'Total columns: {len(df.columns)}')
print(f'Smooth feature columns: {len(cols)}')
print(f'First 5 cols: {df.columns[:5].tolist()}')
print(f'Has smooth_created_z000: {"smooth_created_z000" in df.columns}')
print(f'Has smooth_created_z191: {"smooth_created_z191" in df.columns}')
print(f'Dataset shape: {df.shape}')
print(f'\nColumn names sample:')
print(df.columns[:10].tolist())
