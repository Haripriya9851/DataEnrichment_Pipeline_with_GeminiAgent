# Enrichment Pipeline

This project enriches franchisee data using Google Serper and Gemini (Google Generative AI).

## Setup

1. Clone the repository and navigate to the `enrichment_pipeline` directory.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your environment variables. You can copy `.env` and fill in your API keys:
   ```bash
   cp .env .env.local
   # Edit .env.local and add your keys
   export $(cat .env.local | xargs)
   ```

## Usage

1. Place your input Excel file (e.g., `Golden Chick_DE_Takehome.xlsx`) in the parent directory.
2. Run the pipeline:
   ```bash
   python main.py
   ```
3. The enriched results will be saved to `enriched_franchisees_gemini.xlsx` in the same directory.

## Environment Variables
- `GOOGLE_API_KEY`: Your Google Generative AI API key
- `SERPER_API_KEY`: Your Serper API key

## Notes
- The pipeline processes data in batches of 10 for efficiency.
- Make sure your API keys are valid and have sufficient quota. 