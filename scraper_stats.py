import pandas as pd
import cloudscraper
import os
from bs4 import BeautifulSoup, Comment
from io import StringIO
from objects import PlayerPerformance

URL = "https://fbref.com/en/comps/24/stats/Serie-A-Stats"

def scrape_performance_data():
    print("Starting Scraper(FBref)...")
    
    try:
        scraper = cloudscraper.create_scraper()
        print(f"📡 Connecting to: {URL}")
        response = scraper.get(URL)
        
        if response.status_code != 200:
            print(f"❌ HTTP Error {response.status_code}.")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("🔍 Locating hidden stats container...")
        
        stats_div = soup.find('div', id='all_stats_standard')
        
        if not stats_div:
            print("❌ Container 'all_stats_standard' not found. Page structure might have changed.")
            return None

        comment = stats_div.find(string=lambda text: isinstance(text, Comment))
        
        if not comment:
            print("❌ No commented table found inside the container.")
            return None
            
        print("✅ Hidden table found! Extracting HTML...")
        
        df = pd.read_html(StringIO(str(comment)), header=1)[0]
        
        if 'Rk' in df.columns:
            df = df[df['Rk'] != 'Rk']
        
        col_check = 'Player' if 'Player' in df.columns else 'Jogador'
        if col_check in df.columns:
            df = df[df[col_check].notna()]

        column_mapping = {
            'Player': 'player', 'Nation': 'nationality', 'Pos': 'position', 
            'Squad': 'team', 'Age': 'age', 'MP': 'matches', 
            'Min': 'minutes', 'Gls': 'goals', 'Ast': 'assists', 'xG': 'xg',
            'Jogador': 'player', 'Nação': 'nationality', 'Pos.': 'position',
            'Equipe': 'team', 'Idade': 'age', 'Min.': 'minutes',
        }
        
        existing_cols = {k: v for k, v in column_mapping.items() if k in df.columns}
        df = df[list(existing_cols.keys())].rename(columns=existing_cols)
        
        print(f"⚙️ Validating {len(df)} players with objects.py...")
        
        validated_data = []
        for record in df.to_dict(orient='records'):
            try:
                clean_record = {k: (None if pd.isna(v) else v) for k,v in record.items()}
                
                player_obj = PlayerPerformance(**clean_record)
                validated_data.append(player_obj.model_dump())
            except Exception:
                continue 

        return pd.DataFrame(validated_data)

    except Exception as e:
        print(f"❌ Critical Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    df = scrape_performance_data()
    
    if df is not None:
        os.makedirs("data", exist_ok=True)
        file_path = os.path.join("data", "brasileirao_stats.csv")
        
        df.to_csv(file_path, index=False, sep=';', encoding='utf-8-sig')
        print(f"💾 Success! Saved {len(df)} players to: {file_path}")