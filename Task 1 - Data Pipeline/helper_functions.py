import re
import json
import pandas as pd
import time
import requests

def safe_enrich(func, *args, retries=3, delay=2, **kwargs):
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except (requests.ConnectionError, requests.exceptions.RequestException) as e:
            print(f"Connection error: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)
    print("Failed after retries.")
    return {}

def extract_json(text):
    cleaned = re.sub(r"^```json\s*|```$", "", text.strip(), flags=re.MULTILINE)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Cleaned text:\n{cleaned}")
        return {}

def format_name(name):
    name = re.sub(r'\s+', ' ', str(name).replace('\n', ' ')).strip().strip('"').strip("'")
    corp_terms = ['llc', 'inc', 'corp', 'ltd', 'company']
    if any(term in name.lower() for term in corp_terms):
        return name
    if ',' in name and name.count(',') == 1:
        last, first = name.split(',', 1)
        name = f"{first.strip()} {last.strip()}"
    return name

def clean_dataframe(df):
    df = df.copy()
    df.loc[:, 'Franchisee'] = df['Franchisee'].apply(format_name)
    df.loc[:, 'State'] = df['City'].str.strip() + ', ' + df['State'].str.strip()
    if 'FDD' in df.columns:
        df.loc[:, 'Franchise Name'] = df['FDD']
    return df.dropna(axis=1, how='all')

def batch_iterable(iterable, batch_size):
    l = len(iterable)
    for ndx in range(0, l, batch_size):
        yield iterable[ndx:min(ndx + batch_size, l)] 