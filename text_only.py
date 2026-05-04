import logging
from model_handler import get_model_handler
from inference import grade_fake_probability

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

def predict_text_only(text: str):
    """
    Core function for UI/API to get RoBERTa predictions and token importance.
    """
    # 1. Access the singleton model handler
    text_expert = get_model_handler()
    
    # 2. Run Inference + Saliency (Word Attribution)
    # This calls the .backward() logic we built in model_handler.py
    raw_result = text_expert.predict_and_explain(text)
    fake_probability = (
        raw_result["confidence"]
        if raw_result["prediction"] == "FAKE"
        else 1 - raw_result["confidence"]
    )
    grade, trust_level, status = grade_fake_probability(fake_probability)
    
    # 3. Format the response for the UI
    # We want a clean list of 'word' and 'score' for easy mapping
    return {
        "prediction": raw_result['prediction'],
        "confidence": round(float(raw_result['confidence']), 4),
        "fake_probability": round(float(fake_probability), 4),
        "grade": grade,
        "trust_level": trust_level,
        "status": status,
        "important_words": [
            {
                "word": item['word'],
                "score": round(float(item['importance_score']), 4)
            } 
            for item in raw_result['important_words']
        ],
        "full_token_map": [
            {
                "word": item['word'],
                "score": round(float(item['importance_score']), 4)
            }
            for item in raw_result['full_highlights']
        ]
    }

# ===========================================================================
# UI MOCKUP / TEST CASE
# ===========================================================================
if __name__ == "__main__":
    print("\n--- Testing UI-Ready Function ---")
    
    sample_review = "This product is a total scam. It broke after one use and the seller is ignoring me!"
    
    # This is exactly what your FastAPI route will return
    response = predict_text_only(sample_review)
    
    print(f"\nFinal Label: {response['prediction']}")
    print(f"Confidence: {response['confidence']:.2%}")
    
    print("\nTop Contributing Words (UI Highlights):")
    for item in response['important_words']:
        print(f" -> {item['word']}: {item['score']}")
