---
title: Amazon Review Detection
emoji: 🔍
colorFrom: yellow
colorTo: red
sdk: docker
app_port: 7860
pinned: false
---

# Fake Review Detection Using RoBERTa

An AI-based review analysis system that detects potentially fake product reviews and presents product-level trust insights using a RoBERTa text classifier, metadata-based ensemble scoring, and a simple web interface.

### Note

This uses SerpAPI, which only fetches top reviews from Amazon that are available. If you want deatailed analysis, prefer calling endpoints through a python script, manully paste the reviews or if possible web-scrap them.

## Features

- Classifies reviews as `REAL` or `FAKE`
- Uses RoBERTa-based text inference for review classification
- Combines text prediction with metadata features such as rating and verified purchase status
- Highlights important words contributing to the prediction
- Extracts Amazon product and review data using SerpAPI
- Calculates an overall product review grade
- Computes adjusted product rating by excluding reviews predicted as fake
- Provides FastAPI backend endpoints and a browser-based frontend

## Tech Stack

- Python
- FastAPI
- PyTorch
- Transformers
- Scikit-learn
- Pandas
- NLTK / TextBlob
- HTML, CSS, JavaScript
- Pixi for environment management

## Project Structure

```text
engine/
├── main.py                  # FastAPI app and routes
├── inference.py             # Ensemble prediction logic
├── text_only.py             # Text-only RoBERTa prediction
├── model_handler.py         # RoBERTa model loading and saliency explanation
├── meta_handler.py          # Metadata model loading and inference
├── scraper.py               # Amazon product/review extraction using SerpAPI
├── utils.py                 # Feature engineering utilities
├── static/                  # Frontend files
├── fake_review_model/       # Trained RoBERTa model files
├── metadata_rf_model.pkl    # Metadata Random Forest model
├── pixi.toml                # Pixi environment config
└── pixi.lock
```

## Setup



## Prerequisite

Install Pixi first:

```powershell
powershell -ExecutionPolicy ByPass -c "irm -useb https://pixi.sh/install.ps1 | iex"
```

Install dependencies using Pixi:

```powershell
cd D:\backend\engine
pixi install
```

Run the app:

```powershell
pixi run dev
```

Open in browser:

```text
http://127.0.0.1:8000/
```

## SerpAPI Setup

The product analysis flow uses SerpAPI to fetch Amazon product and review data.

Set your API key before running the app:

```powershell
$env:SERPAPI_KEY="your_serpapi_key_here"
pixi run dev
```

Without `SERPAPI_KEY`, manual review prediction still works, but Amazon product scraping will fail.

## API Endpoints

### Health / Frontend

```http
GET /
```

Serves the frontend UI.

### Text-only Prediction

```http
POST /text
```

Request:

```json
{
  "REVIEW_TEXT": "This product is absolutely amazing. Must buy!"
}
```

Response includes:

- prediction
- confidence
- fake probability
- trust grade
- important words
- full token highlight map

### Ensemble Prediction

```http
POST /predict
```

Request:

```json
{
  "REVIEW_TEXT": "This product is absolutely amazing. Must buy!",
  "RATING": 5,
  "VERIFIED_PURCHASE": "Y"
}
```

Response includes:

- final label
- final confidence
- fake probability
- grade
- trust level
- top indicators
- token-level highlights

### Product Analysis

```http
POST /home
```

Request:

```json
{
  "url": "https://www.amazon.com/dp/PRODUCT_ASIN"
}
```

Returns product details, reviews, ratings summary, purchase options, and similar products.

## Scoring Logic

The system converts fake probability into a review grade:

| Fake Probability | Grade | Trust Level |
|---|---|---|
| 0.00 - 0.10 | A | Trustworthy |
| 0.11 - 0.30 | B | Good |
| 0.31 - 0.60 | C | Caution |
| 0.61 - 0.85 | D | Suspicious |
| 0.86 - 1.00 | F | High Risk |

For product-level scoring, the system softens the grade when only a small number of reviews are available. This prevents the overall product grade from becoming too strict when SerpAPI returns only a limited review sample.

## Adjusted Rating

The adjusted rating is calculated by removing reviews predicted as `FAKE` and recomputing the average star rating from the remaining reviews.

This gives a cleaner estimate of product quality based on reviews considered more trustworthy.