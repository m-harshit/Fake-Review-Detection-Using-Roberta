import logging
import numpy as np
import pandas as pd
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from textblob import TextBlob

# ---------------------------------------------------------------------------
# Setup & Resource Management
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

def bootstrap_resources():
    """Ensures NLTK data is present before the app starts."""
    try:
        nltk.data.find("sentiment/vader_lexicon.zip")
    except (LookupError, AttributeError):
        logger.info("Downloading VADER lexicon...")
        nltk.download("vader_lexicon", quiet=True)

bootstrap_resources()
_SIA = SentimentIntensityAnalyzer()

# ---------------------------------------------------------------------------
# Constants & Training Stats
# ---------------------------------------------------------------------------
# Replace this with the actual mean 'review_char_len' from your training set
# This ensures 'len_anomaly' is calculated correctly for single requests.
TRAINING_CHAR_LEN_MEAN = 350.0 

# ---------------------------------------------------------------------------
# Feature Engineering Helpers
# ---------------------------------------------------------------------------

def _caps_ratio(text: str) -> float:
    return sum(1 for c in text if c.isupper()) / max(len(text), 1)

def _repetition_rate(text: str) -> float:
    words = text.lower().split()
    if not words:
        return 0.0
    return (len(words) - len(set(words))) / len(words)

def _rating_mismatch(rating: float, compound: float) -> int:
    if rating >= 4 and compound < -0.2:
        return 1
    if rating <= 2 and compound > 0.5:
        return 1
    return 0

# ---------------------------------------------------------------------------
# Core Inference Processor
# ---------------------------------------------------------------------------

def extract_features(data: dict) -> pd.DataFrame:
    """
    Converts a single request dictionary into a processed DataFrame.
    Matches the exact schema used during model training.
    """
    # 1. Basic Extraction & Type Coercion
    text = str(data.get("REVIEW_TEXT", ""))
    rating = float(data.get("RATING", 0))
    # Map 'Y'/'N' to 1/0
    verified = 1 if str(data.get("VERIFIED_PURCHASE")).upper() == "Y" else 0

    # 2. NLP Analysis
    blob = TextBlob(text)
    sentiment = _SIA.polarity_scores(text)
    compound = sentiment["compound"]

    # 3. Structural Features
    char_len = len(text)
    word_count = len(text.split())
    
    # 4. Assembly (Matching training column order is best practice)
    features = {
        "is_verified": verified,
        "rating": rating,
        "review_char_len": char_len,
        "word_count": word_count,
        "len_anomaly": abs(char_len - TRAINING_CHAR_LEN_MEAN),
        "caps_ratio": _caps_ratio(text),
        "exclamation_ratio": text.count("!") / max(char_len, 1),
        "repetition_rate": _repetition_rate(text),
        "digit_density": sum(c.isdigit() for c in text) / max(char_len, 1),
        "subjectivity": blob.sentiment.subjectivity,
        "pos_score": sentiment["pos"],
        "compound_score": compound,
        "neutrality": 1 - abs(compound),
    }

    # 5. Derived Cross-Features
    features["rating_mismatch"] = _rating_mismatch(rating, compound)

    return pd.DataFrame([features])

# ---------------------------------------------------------------------------
# Batch Processor (For testing or bulk uploads)
# ---------------------------------------------------------------------------

def preprocess_batch(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies the logic across a whole DataFrame. 
    Useful if you want to support CSV uploads in your API later.
    """
    results = []
    for _, row in df.iterrows():
        # Convert row to dict and extract
        feat_df = extract_features(row.to_dict())
        results.append(feat_df)
    
    return pd.concat(results, ignore_index=True)