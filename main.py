import os
import logging
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
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


def _load_env_file(path: Path) -> None:
    """Load simple KEY=VALUE pairs from .env without adding another dependency."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


_load_env_file(BASE_DIR / ".env")

app = FastAPI(title="Fake Review Detection System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def _preview(text: str, limit: int = 72) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= limit else f"{text[:limit]}..."

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


@app.get("/firebase-config")
async def firebase_config():
    """Expose Firebase browser config from environment variables."""
    return {
        "apiKey": os.getenv("VITE_FIREBASE_API_KEY", ""),
        "authDomain": os.getenv("VITE_FIREBASE_AUTH_DOMAIN", ""),
        "projectId": os.getenv("VITE_FIREBASE_PROJECT_ID", ""),
        "storageBucket": os.getenv("VITE_FIREBASE_STORAGE_BUCKET", ""),
        "messagingSenderId": os.getenv("VITE_FIREBASE_MESSAGING_SENDER_ID", ""),
        "appId": os.getenv("VITE_FIREBASE_APP_ID", ""),
        "measurementId": os.getenv("VITE_FIREBASE_MEASUREMENT_ID", ""),
    }

@app.post("/predict")
async def predict_ensemble(data: EnsembleRequest):
    """Full Ensemble Prediction (RoBERTa + Random Forest)"""
    try:
        print(
            f"Ensemble request received: rating {data.RATING}, verified {data.VERIFIED_PURCHASE}.",
            flush=True,
        )
        print(f"Review preview: {_preview(data.REVIEW_TEXT)}", flush=True)
        result = run_ensemble_inference(
            text=data.REVIEW_TEXT,
            rating=data.RATING,
            verified=data.VERIFIED_PURCHASE
        )
        print(
            f"Ensemble complete: {result['final_label']} with {result['final_confidence']:.2%} confidence.",
            flush=True,
        )
        return result
    except Exception as e:
        logger.error(f"Ensemble Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/text")
async def predict_text(data: TextOnlyRequest):
    """RoBERTa-only Prediction with Saliency (Highlights)"""
    try:
        print("Text-only request received.", flush=True)
        print(f"Review preview: {_preview(data.REVIEW_TEXT)}", flush=True)
        result = predict_text_only(data.REVIEW_TEXT)
        print(
            f"Text-only complete: {result['prediction']} with {result['confidence']:.2%} confidence.",
            flush=True,
        )
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
        print("Product lookup started.", flush=True)
        print(f"Amazon input: {_preview(data.url)}", flush=True)
        logger.info(f"Scraping URL: {data.url}")
        result = analyse(raw_input=data.url, api_key=my_key)
        
        if not result:
            raise HTTPException(status_code=404, detail="Could not retrieve product data.")

        review_count = len(result.get("reviews", []))
        title = result.get("product", {}).get("title") or "product"
        print(f"Product lookup complete: {review_count} reviews found for {_preview(title)}", flush=True)
            
        return result
    except Exception as e:
        logger.error(f"Scraper Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# # --- Local Server Execution ---
# if __name__ == "__main__":
#     import uvicorn
#     # Start server: python main.py
#     uvicorn.run(app, host="0.0.0.0", port=8000)
