# Task 1 - Data Pipeline

## Overview
This task involves building a Python-based data enrichment pipeline. The pipeline is designed to automate the process of enriching franchisee data using external data sources.

## Data Enrichment Considerations
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
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up your `.env` file with the required API keys and paths.
3. Run the pipeline:
   ```bash
   python main.py
   ```

## Notes
- For larger datasets, consider upgrading to a premium Opencorporates API plan to avoid rate limiting.

## Environment Variables
- `GOOGLE_API_KEY`: Your Google Generative AI API key
- `SERPER_API_KEY`: Your Serper API key

## Notes
- The pipeline processes data in batches of 10 for efficiency.
- Make sure your API keys are valid and have sufficient quota. 
- OpenCorporates could be used.
