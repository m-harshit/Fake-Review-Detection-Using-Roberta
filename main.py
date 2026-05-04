import os
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Import your custom inference logic
from inference import run_ensemble_inference
from text_only import predict_text_only
from scraper import analyse

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(title="Fake Review Detection System")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# --- Pydantic Models for Input Validation ---

class EnsembleRequest(BaseModel):
    REVIEW_TEXT: str
    RATING: int
    VERIFIED_PURCHASE: str  # "Y" or "N"

class TextOnlyRequest(BaseModel):
    REVIEW_TEXT: str

class ScraperRequest(BaseModel):
    url: str

# --- Endpoints ---

@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")

@app.post("/predict")
async def predict_ensemble(data: EnsembleRequest):
    """Full Ensemble Prediction (RoBERTa + Random Forest)"""
    try:
        result = run_ensemble_inference(
            text=data.REVIEW_TEXT,
            rating=data.RATING,
            verified=data.VERIFIED_PURCHASE
        )
        return result
    except Exception as e:
        logger.error(f"Ensemble Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/text")
async def predict_text(data: TextOnlyRequest):
    """RoBERTa-only Prediction with Saliency (Highlights)"""
    try:
        result = predict_text_only(data.REVIEW_TEXT)
        return result
    except Exception as e:
        logger.error(f"Text Prediction Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/home")
async def get_product_details(data: ScraperRequest):
    """Scrapes Amazon product details and reviews using a URL"""
    my_key = os.getenv("SERPAPI_KEY")
    if not my_key:
        raise HTTPException(status_code=500, detail="SERPAPI_KEY not found in environment.")

    try:
        logger.info(f"Scraping URL: {data.url}")
        result = analyse(raw_input=data.url, api_key=my_key)
        
        if not result:
            raise HTTPException(status_code=404, detail="Could not retrieve product data.")
            
        return result
    except Exception as e:
        logger.error(f"Scraper Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# # --- Local Server Execution ---
# if __name__ == "__main__":
#     import uvicorn
#     # Start server: python main.py
#     uvicorn.run(app, host="0.0.0.0", port=8000)
