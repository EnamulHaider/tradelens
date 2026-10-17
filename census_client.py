import json
import os
import sys 
import time 
from pathlib import Path 
import requests 
from dotenv import load_dotenv
#-------------------------------------------------------------
#Enamul 10/11/2026 the client talks to API and sends the data
#-------------------------------------------------------------

load_dotenv()

BASE_URL = "https://api.census.gov/data/timeseries/intltrade/imports/hs"
FIELDS = "CTY_CODE,CTY_NAME,I_COMMODITY,I_COMMODITY_LDESC,GEN_VAL_MO,GEN_QY1_MO"

def fetch_month(year: int, month: int, commodity: str="7601*",retries :int=3)-> list: 
    """Fetch one month of import data. Returns the raw JSON(a list of rows)."""
    api_key= os.getenv('CENSUS_API_KEY')
    if  api_key:
        print("API key allocated.")
    else:
        raise RuntimeError("API key not found. Check you environment file.")

    params = {
        "get": FIELDS,
        "COMM_LVL":"HS6",
        "I_COMMODITY":commodity,
        "time": f"{year}-{month:02d}",
        "key":api_key
    }
    for attempt in range(1,retries+1):
        try:
            response =requests.get(BASE_URL,params,timeout=30)
            print (response.json())
            response.raise_for_status()
            if response.status_code == 204 or not response.text.strip():
                return[]
            return response.json()
        except requests.RequestException as error: 
            if attempt == retries:
                raise
            wait = 2** attempt
            print( f"Attempt {attempt} failed ({error}).Retrying in {wait}s...")
            time.sleep(wait)

def save_raw (data: list, year: int, month: int) -> Path:
    """Save the raw reposne to a fixed path, so reruns the overwrite instead of duplicates"""
    folder = Path("data/bronze/imports")/ f"year = {year}"/ f"month = {month:02d}"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "data.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    print(path)

if __name__=="__main__":
    year = int(sys.argv[1]) if len(sys.argv)> 1 else 2024
    month = int(sys.argv[2]) if len(sys.argv) > 1 else 6
    data = fetch_month(year,month)
    path = save_raw(data,year,month)
    rows= max(len(data)-1,0)
    print(f"saved {rows} data rows to {path}")