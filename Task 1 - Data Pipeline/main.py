import pandas as pd
from agent_functions import enrich_all, batch_iterable

if __name__ == "__main__":
    df = pd.read_excel("Input/Golden Chick_DE_Takehome.xlsx")
    print("Original Sample:")
    print(df[['Franchisee', 'City', 'State']].head())
    enriched_rows = []
    for batch in batch_iterable(df.index.tolist(), 10):
        batch_df = df.loc[batch]
        enriched_batch = enrich_all(batch_df)
        enriched_rows.append(enriched_batch)
    enriched_df = pd.concat(enriched_rows, ignore_index=True)
    enriched_df.to_excel("Output/enriched_franchisees_gemini.xlsx", index=False)
    print("\nSaved enriched data to enriched_franchisees_gemini.xlsx")
    print(enriched_df[['Franchisee', 'Type', 'owner_name', 'legal_corporate_name', 'corporate_address', 'Source URLs used for enrichment']].head())