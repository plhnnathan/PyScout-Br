import pandas as pd
from thefuzz import process, fuzz
import os

folder_path = "data"
stats_path = os.path.join(folder_path, "brasileirao_stats.csv")
values_path = os.path.join(folder_path, "brasileirao_values.csv")
output_path = os.path.join(folder_path, "dataset_bi.csv")

try:
    df_stats = pd.read_csv(stats_path, sep=';')
    df_values = pd.read_csv(values_path, sep=';')
    
    if 'xg' in df_stats.columns:
        df_stats['xg'] = df_stats['xg'].apply(lambda x: float(str(x).replace(',', '.')) if isinstance(x, str) else x)

    if 'market_value_euro' in df_values.columns:
         df_values['market_value_euro'] = df_values['market_value_euro'].apply(lambda x: float(str(x).replace(',', '.')) if isinstance(x, str) else x)

    print(f"Stats loaded: {len(df_stats)} records")
    print(f"Values loaded: {len(df_values)} records")

except FileNotFoundError:
    print("Files not found in 'data' directory.")
    exit()

df_stats['tm_name_match'] = "N/A"
df_stats['market_value_euro'] = 0.0
df_stats['tm_position'] = "N/A"
df_stats['last_update'] = "N/A"

tm_names_list = df_values['tm_name'].tolist()
matches_count = 0

print("Iniciando cruzamento de dados...")

for index, row in df_stats.iterrows():
    player_name = row['player']
    
    match = process.extractOne(player_name, tm_names_list, scorer=fuzz.token_sort_ratio, score_cutoff=80)
    
    if match:
        best_match_name = match[0]
        
        player_data = df_values[df_values['tm_name'] == best_match_name].iloc[0]
        
        df_stats.at[index, 'tm_name_match'] = best_match_name
        df_stats.at[index, 'market_value_euro'] = player_data['market_value_euro']
        df_stats.at[index, 'tm_position'] = player_data['tm_position']
        df_stats.at[index, 'last_update'] = player_data['last_update']
        
        matches_count += 1

print(f"Matches found: {matches_count}")


df_stats['kpi_cost_per_goal'] = df_stats.apply(
    lambda x: x['market_value_euro'] / x['goals'] if x['goals'] > 0 else 0.0, axis=1
)

df_stats['kpi_moneyball'] = df_stats.apply(
    lambda x: ((x['goals'] + x['assists'] + x['xg']) / x['market_value_euro']) * 10_000_000 
    if x['market_value_euro'] > 0 else 0.0, axis=1
)

cols_to_round = ['market_value_euro', 'xg', 'kpi_cost_per_goal', 'kpi_moneyball']
for col in cols_to_round:
    if col in df_stats.columns:
        df_stats[col] = df_stats[col].round(2)

df_stats.to_csv(output_path, index=False, sep=';', encoding='utf-8-sig', decimal='.')

print(f"File saved successfully: {output_path}")