import logging

# Using absolute imports for the local flat structure
from model_handler import get_model_handler
from meta_handler import get_meta_handler

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

def grade_fake_probability(p_fake: float):
    """
    Maps fake probability to a Nullfake-style grade and visible status.
    """
    if p_fake <= 0.25:
        return "A", "Trustworthy", "TRUSTWORTHY"
    if p_fake <= 0.40:
        return "B", "Good", "TRUSTWORTHY"
    if p_fake <= 0.70:
        return "C", "Caution", "CAUTION"
    if p_fake <= 0.80:
        return "D", "Suspicious", "CAUTION"
    return "F", "High Risk", "HIGH RISK"

def run_ensemble_inference(text: str, rating: int, verified: str):
    """
    Coordinates Deep Learning (RoBERTa) and Metadata (Random Forest) 
    to produce a UI-ready ensemble prediction.
    """
    print("Ensemble inference started.", flush=True)

    # 1. Get Expert Instances
    text_expert = get_model_handler()
    meta_expert = get_meta_handler()
    
    # 2. RoBERTa Prediction + Saliency
    print("Reading the review with RoBERTa.", flush=True)
    text_res = text_expert.predict_and_explain(text)
    
    # Convert prediction to probability of being REAL (Class 1)
    if text_res['prediction'] == "REAL":
        text_prob = text_res['confidence']
    else:
        text_prob = 1 - text_res['confidence']
    print(f"Text model says real probability is {text_prob:.4f}.", flush=True)

    # 3. Metadata Random Forest Prediction
    input_data = {
        "REVIEW_TEXT": text,
        "RATING": rating,
        "VERIFIED_PURCHASE": verified
    }
    print("Checking rating and purchase metadata.", flush=True)
    meta_prob = meta_expert.predict_real_probability(input_data)
    print(f"Metadata model says real probability is {meta_prob:.4f}.", flush=True)

    # 4. Late Fusion Logic
    # Adjust alpha weight based on RoBERTa's certainty (abs distance from 0.5)
    alpha_used = 0.7 if abs(text_prob - 0.5) > 0.25 else 0.5
    
    final_real_prob = (alpha_used * text_prob) + ((1 - alpha_used) * meta_prob)
    
    final_label = "REAL" if final_real_prob > 0.5 else "FAKE"
    final_confidence = final_real_prob if final_real_prob > 0.5 else 1 - final_real_prob
    fake_probability = 1 - final_real_prob
    grade, trust_level, status = grade_fake_probability(fake_probability)
    print(
        f"Final ensemble verdict: {final_label}, grade {grade}, fake probability {fake_probability:.4f}.",
        flush=True,
    )

    # 5. UI-Ready Response Mapping
    return {
        "final_label": final_label,
        "final_confidence": round(float(final_confidence), 4),
        "fake_probability": round(float(fake_probability), 4),
        "grade": grade,
        "trust_level": trust_level,
        "status": status,
        "individual_scores": {
            "text_model_real_prob": round(float(text_prob), 4),
            "meta_model_real_prob": round(float(meta_prob), 4),
            "weight_applied": alpha_used
        },
        # Top 5 most influential words for summary
        "top_indicators": [
            {"word": item['word'], "score": round(float(item['importance_score']), 4)}
            for item in text_res['important_words']
        ],
        # Full mapping for word-by-word highlighting in UI
        "full_token_map": [
            {"word": item['word'], "score": round(float(item['importance_score']), 4)}
            for item in text_res['full_highlights']
        ]
    }

# ===========================================================================
# TEST SUITE
# ===========================================================================
if __name__ == "__main__":
    print("\n--- Running Ensemble UI-Response Test ---\n")
    
    test_suite = [
        ("Incredible quality, a must buy for everyone!", 5, "N", "FAKE"),
        ("This is my first Mac ever! I have iPhones and iPads though. This computer is great, fast, and looks awesome. I’m coming from a probably 12 year old windows computer. It took me a second to get used to, I didn’t know how to scroll etc lol but I figured it out. I also downloaded the Sims 4 on it and it was probably the fastest download I’ve ever seen. I was also super happy even though I purchased Sims originally for my windows computer it was still able to download all on Mac (through EA), so that was a big plus (not sure if that’s common knowledge but still). I originally was going to purchase the pink Neo but chose this one instead and glad I did, a pretty color doesn’t matter as much as having a better computer for only a couple hundred more. I did get starlight color but I’m getting a pink case anyway so it’s not that big of a deal. Worth the buy though!", 5, "Y", "REAL")
    ]

    for text, rating, verified, expected in test_suite:
        res = run_ensemble_inference(text, rating, verified)
        # print(res["full_token_map"])
        status = "PASS" if res['final_label'] == expected else "FAIL"
        
        print(f"Result: {res['final_label']} | Conf: {res['final_confidence']:.2%} | {status}")
        print(f"Top Word: {res['top_indicators'][0]['word']} ({res['top_indicators'][0]['score']})")
        print("-" * 50)
