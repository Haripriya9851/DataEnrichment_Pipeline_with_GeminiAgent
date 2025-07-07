import os
from langchain_community.utilities import GoogleSerperAPIWrapper
import google.generativeai as genai
from helper_functions import extract_json, clean_dataframe, safe_enrich

# --- SETUP ---
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "your_google_api_key")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY", "your_serper_api_key")
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
gemini_model = genai.GenerativeModel('gemini-2.0-flash')
serper = GoogleSerperAPIWrapper()


def search_web(query: str):
    results = serper.results(query)
    if isinstance(results, dict) and results.get('organic'):
        return results['organic'][0]
    return {}

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
        import pandas as pd
        return pd.DataFrame(columns=["name", "type"])
    import pandas as pd
    return pd.DataFrame(data)

def enrich_individual(name, franchise, state):
    company_query = f"What company does {name} own that holds a {franchise} franchise in {state}?"
    result = search_web(company_query)
    snippet = result.get('snippet', '')
    url = result.get('link', '')
    title = result.get('title', '')

    legal_name_prompt = f"From the following search result, return the company name owned by {name} that is associated with {franchise}. If not found, return just '{name}'. No explanation.\n\nTitle: {title}\nSnippet: {snippet}\nURL: {url}"
    legal_name = gemini_model.generate_content(legal_name_prompt).text.strip()

    details_query = f"Details of {legal_name} in {state}, include corporate address, phone, and email"
    result2 = search_web(details_query)
    snippet2 = result2.get('snippet', '')
    url2 = result2.get('link', '')
    title2 = result2.get('title', '')

    extract_prompt = f"""From the following search result, extract corporate details and return JSON:
Title: {title2}
Snippet: {snippet2}
URL: {url2}

{{
  "legal_corporate_name": "{legal_name}",
  "corporate_address": "",
  "corporate_phone": "",
  "corporate_email": "",
  "owner_name": "{name}",
  "linkedin_url": "",
  "Source URLs used for enrichment": "{url2}"
}}
No backtics(```),No markdown. Return only JSON"""
    response = gemini_model.generate_content(extract_prompt)
    text = response.text.strip()
    result_json = extract_json(text)
    result_json["Source URLs used for enrichment"] = url2 if url2 else ""
    return result_json

def enrich_corporate(name, state):
    query = f"Who owns or manages {name} in {state}?"
    result = search_web(query)
    snippet = result.get('snippet', '')
    url = result.get('link', '')
    title = result.get('title', '')

    extract_prompt = f"""From the following search result, extract business info and return JSON:
Title: {title}
Snippet: {snippet}
URL: {url}

{{
  "legal_corporate_name": "{name}",
  "corporate_address": "",
  "corporate_phone": "",
  "corporate_email": "",
  "owner_name": "",
  "linkedin_url": "",
  "Source URLs used for enrichment": "{url}"
}}
No backtics and markdown."""
    response = gemini_model.generate_content(extract_prompt)
    text = response.text.strip()
    result_json = extract_json(text)
    result_json["Source URLs used for enrichment"] = url if url else ""
    return result_json

def enrich_all(df):
    df = clean_dataframe(df)
    names = df['Franchisee'].tolist()
    import pandas as pd
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