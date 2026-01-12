import pandas as pd
import requests
import os
from bs4 import BeautifulSoup
import time
import random
from objects import PlayerMarketValue

BASE_URL = "https://www.transfermarkt.com.br/campeonato-brasileiro-serie-a/marktwerte/wettbewerb/BRA1/plus/1/page/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Referer": "https://www.google.com/"
}

def scrape_market_values():
    print("\nStarting Scraper(Transfermarkt)...")
    
    players_list = []
    total_pages = 20
    
    session = requests.Session()
    session.headers.update(HEADERS)
    
    for page in range(1, total_pages + 1):
        current_url = f"{BASE_URL}{page}"
        print(f"📄 Page {page}/{total_pages}...")
        
        try:
            response = session.get(current_url, timeout=20)
            
            if response.status_code != 200:
                print(f"⚠️ HTTP {response.status_code}. Retrying...")
                time.sleep(5)
                continue
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find("table", {"class": "items"})
            
            if not table:
                print("⚠️ Table not found.")
                continue
                
            rows = table.find_all("tr", {"class": ["odd", "even"]})
            
            for row in rows:
                try:
                    name_cell = row.find("td", {"class": "hauptlink"})
                    name = name_cell.find("a").get_text(strip=True) if name_cell and name_cell.find("a") else "N/A"
                    
                    position = "N/A"
                    inline_tab = row.find("table", {"class": "inline-table"})
                    if inline_tab:
                        trs = inline_tab.find_all("tr")
                        if len(trs) > 1:
                            position = trs[-1].get_text(strip=True)

                    center_cols = row.find_all("td", {"class": "zentriert"})
                    
                    nationality = "N/A"
                    if len(center_cols) > 1:
                        img = center_cols[1].find("img")
                        if img: nationality = img.get('title')
                        
                    age = 0
                    if len(center_cols) > 2:
                        age = center_cols[2].get_text(strip=True)
                        
                    club = "No Club"
                    if len(center_cols) > 3:
                        lnk = center_cols[3].find("a")
                        if lnk and lnk.find("img"):
                            club = lnk.find("img").get('title')
                        else:
                            club = center_cols[3].get_text(strip=True)
                            
                    last_update = "N/A"
                    if len(center_cols) > 4:
                        last_update = center_cols[-1].get_text(strip=True)
                        
                    value_col = row.find("td", {"class": "rechts hauptlink"})
                    raw_value = value_col.get_text(strip=True) if value_col else "€0"
                    
                    player = PlayerMarketValue(
                        tm_name=name,
                        tm_position=position,
                        nationality=nationality,
                        age=age,
                        club=club,
                        last_update=last_update,
                        market_value_euro=raw_value
                    )
                    
                    players_list.append(player.model_dump())

                except Exception:
                    continue

            time.sleep(random.uniform(2, 4))
            
        except Exception as e:
            print(f"❌ Connection Error: {e}")

    if players_list:
        df = pd.DataFrame(players_list)
        print("-" * 80)
        print(f"Total collected: {len(df)} players.")
        print("-" * 80)
        
        os.makedirs("data", exist_ok=True)
        file_path = os.path.join("data", "brasileirao_values.csv")
        
        df.to_csv(file_path, index=False, sep=';', encoding='utf-8-sig')
        print(f"💾 File saved successfully at: {file_path}")
    else:
        print("❌ No data collected.")

if __name__ == "__main__":
    scrape_market_values()