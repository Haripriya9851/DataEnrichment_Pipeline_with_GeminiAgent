import os
import json
import re
import pandas as pd
from langchain_community.utilities import GoogleSerperAPIWrapper
import google.generativeai as genai
import time
import requests
from helper_functions import clean_dataframe,extract_json,batch_iterable,safe_enrich

# --- SETUP ---
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "AIzaSyC0_23sKydG3wlqHRgxQbWe6HV4k5hEKv4")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY", "4d17b38723a34498589c3edd102b7b4b175b65f3")
# os.environ["GOOGLE_API_KEY"] = "KEY"
# os.environ["SERPER_API_KEY"] = "KEY"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
gemini_model = genai.GenerativeModel('gemini-2.5-flash')
serper = GoogleSerperAPIWrapper()
search = GoogleSerperAPIWrapper()

def search_web(query: str):
    results = search.results(query)
    return results

def classify_franchisees(names):
    prompt = f"""Classify the following names as 'Individual' or 'Corporate':
{names}

Rules:
- Individual = Person name (John Doe)
- Corporate = Includes LLC, Inc, Ltd, Corp, Company, etc.

Return only valid JSON, in this format:
[{{"name": "Name", "type": "Individual/Corporate"}}]
No explanation. No markdown. No text before or after. If you cannot classify, return [].
"""
    response = gemini_model.generate_content(prompt)
    text = response.text.strip()
    data = extract_json(text)
    if not data:
        print("Gemini returned empty or invalid output. Falling back to empty DataFrame.")
        return pd.DataFrame(columns=["name", "type"])
    return pd.DataFrame(data)

def enrich_individual(name, franchise, state):
    company_query = f"What company does {name} own that holds a {franchise} franchise in {state}?"
    snippet = search_web(company_query)
    legal_name_prompt = f"From the following text, return the company name owned by {name} that is associated with {franchise}. If not found, return just '{name}'. No explanation.\n\n{snippet}"
    legal_name = gemini_model.generate_content(legal_name_prompt).text.strip()

    details_query = f"Details of {legal_name} in {state}, include corporate address, phone, and email"
    snippet2 = search_web(details_query)

    extract_prompt = f"""From the {snippet2}, extract corporate details along with Source URLs used for enrichment. return JSON:

{{
  "legal_corporate_name": "{legal_name}",
  "corporate_address": "",
  "corporate_phone": "",
  "corporate_email": "",
  "owner_name": "{name}",
  "linkedin_url": "",
  "Source URLs used for enrichment": ""
}}
No backtics(```),No markdown. Return only JSON"""
    response = gemini_model.generate_content(extract_prompt)
    text = response.text.strip()
    result = extract_json(text)
    return result

def enrich_corporate(name, state):
    query = f"Who owns or manages {name} in {state}?"
    snippet = search_web(query)
    extract_prompt = f"""From the following, extract business info along with Source URLs used for enrichment. return JSON:
{snippet}

{{
  "legal_corporate_name": "{name}",
  "corporate_address": "",
  "corporate_phone": "",
  "corporate_email": "",
  "owner_name": "",
  "linkedin_url": "",
  "Source URLs used for enrichment": ""
}}.
No backtics and markdown."""
    response = gemini_model.generate_content(extract_prompt)
    text = response.text.strip()
    print(f"Raw Gemini response:\n{text}")
    result = extract_json(text)
    return result

def enrich_all(df):
    df = clean_dataframe(df)
    print("\n\nCleaned DF:", df.head(5))
    names = df['Franchisee'].tolist()
    classifications_df = classify_franchisees(names)
    enriched_rows = []
    for _, row in df.iterrows():
        name = row['Franchisee']
        entity = classifications_df[classifications_df['name'].str.lower() == name.lower()]
        entity_type = entity['type'].values[0] if not entity.empty else "Unknown"
        state = row['State']
        franchise = row.get('Franchise Name', '')

        if entity_type == "Individual":
            enriched = safe_enrich(enrich_individual, name, franchise, state)
        elif entity_type == "Corporate":
            enriched = safe_enrich(enrich_corporate, name, state)
        else:
            enriched = {
                "legal_corporate_name": name,
                "corporate_address": "N/A",
                "corporate_phone": "N/A",
                "corporate_email": "N/A",
                "owner_name": "N/A",
                "linkedin_url": "N/A",
                "Source URLs used for enrichment": "N/A"
            }

        if isinstance(enriched, list):
            if len(enriched) > 0 and isinstance(enriched[0], dict):
                enriched = enriched[0]
            else:
                enriched = {}
        elif not isinstance(enriched, dict):
            enriched = {}

        default_keys = ["legal_corporate_name", "corporate_address", "corporate_phone", "corporate_email", "owner_name", "linkedin_url", "Source URLs used for enrichment"]
        for key in default_keys:
            if key not in enriched:
                enriched[key] = "N/A"

        enriched_rows.append({**row.to_dict(), "Type": entity_type, **enriched})

    return pd.DataFrame(enriched_rows)