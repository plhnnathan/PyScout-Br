from pydantic import BaseModel, field_validator
from typing import Optional

class PlayerPerformance(BaseModel):
    player: str
    nationality: str
    position: str
    team: str
    age: int
    matches: int = 0
    minutes: int = 0
    goals: int = 0
    assists: int = 0
    xg: float = 0.0

    @field_validator('position', mode='before')
    def translate_position(cls, v):
        if not v or str(v).strip() == "": return "N/A"
        abbr = str(v).split(',')[0].strip()
        mapping = {'GK': 'Goleiro', 'DF': 'Defensor', 'MF': 'Meio-Campista', 'FW': 'Atacante'}
        return mapping.get(abbr, abbr)

    @field_validator('nationality', mode='before')
    def clean_nationality(cls, v):
        return str(v).split(' ')[-1] if v else "N/A"

    @field_validator('age', mode='before')
    def clean_age(cls, v):
        try:
            return int(str(v)[:2])
        except:
            return 0

    @field_validator('matches', 'minutes', 'goals', 'assists', 'xg', mode='before')
    def clean_numbers(cls, v):
        if not v or v == "": return 0
        return v

class PlayerMarketValue(BaseModel):
    tm_name: str
    tm_position: str = "N/A"
    nationality: str = "N/A"
    age: int = 0
    club: str = "Sem Clube"
    last_update: str = "N/A"
    market_value_euro: float 

    @field_validator('market_value_euro', mode='before')
    def clean_money(cls, v):
        if not v or v == '€0' or v == '-' or v == "": 
            return 0.0
        
        clean_str = str(v).replace('€', '').strip()
        multiplier = 1.0
        
        if 'mi.' in clean_str or 'm' in clean_str:
            multiplier = 1_000_000.0
            clean_str = clean_str.replace('mi.', '').replace('m', '')
        elif 'mil.' in clean_str or 'k' in clean_str:
            multiplier = 1_000.0
            clean_str = clean_str.replace('mil.', '').replace('k', '')
            
        try:
            return float(clean_str) * multiplier
        except:
            return 0.0