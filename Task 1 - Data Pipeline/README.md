# Task 1 - Data Pipeline

## Overview
This task involves building a Python-based data enrichment pipeline. The pipeline is designed to automate the process of enriching franchisee data using public data sources webcrawling with Google-Serper and the crawled results were reasoned and extracted insights with Gemini Model. 

Final Enriched franchisee details based on public datasource web crawl agent are stored in Excel : [enriched_franchisees_gemini (4).xlsx](https://github.com/Haripriya9851/DataEnrichment_Pipeline_with_GeminiAgent/blob/main/Task%201%20-%20Data%20Pipeline/enriched_franchisees_gemini%20(4).xlsx)

## Data Enrichment Considerations
- Gemini API key when run in batch works well. API limits has to be considered.
- The Opencorporates API was leveraged for enriching company data.
- Due to the lack of access to a premium Opencorporates API plan, the pipeline encountered rate limit errors when scaling up for large-scale web-scraping.
- As a result, the final pipeline results have been submitted for 50 franchisees only.

## Files
- `main.py`: Entry point for running the data pipeline.
- `agent_functions.py`: Contains core functions for data enrichment.
- `helper_functions.py`: Utility functions used throughout the pipeline.
- `requirements.txt`: Python dependencies for the pipeline.
- `.env`: Environment variables (API keys, paths, etc.).

## How to Run
1. Clone Repo and Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up your `.env` file with the required API keys and paths.
3. Run the pipeline:
   ```bash
   python main.py
   ```

## Notes
- For larger datasets, consider upgrading to a premium Serper and Gemini API plan to avoid rate limiting.

## Environment Variables
- `GOOGLE_API_KEY`: Your Google Generative AI API key
- `SERPER_API_KEY`: Your Serper API key

## Notes
- The pipeline processes data in batches of 10 for efficiency.
- Make sure your API keys are valid and have sufficient quota. 
- OpenCorporates could be used for authenticated result matching.

## References:
1. https://medium.com/google-cloud/ai-search-and-summary-app-with-gemini-2-flash-crew-ai-step-by-step-guide-b23fa39cdee5
2. https://serper.dev/
3. https://opencorporates.com/ - For Validation of Results
