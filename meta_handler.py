import joblib
import pandas as pd
import logging
from utils import extract_features

logger = logging.getLogger(__name__)

class MetaHandler:
    def __init__(self, model_path="metadata_rf_model.pkl", cols_path="metadata_feature_cols.pkl"):
        """
        Loads the Random Forest model and the specific column order 
        required for the model to function correctly.
        """
        try:
            self.model = joblib.load(model_path)
            self.model_columns = joblib.load(cols_path)
            logger.info("Metadata Random Forest model and column sequence loaded.")
        except Exception as e:
            logger.error(f"Error loading metadata artifacts: {e}")
            self.model = None
            self.model_columns = None

    def predict_real_probability(self, data_dict: dict) -> float:
        """
        Takes a raw data dictionary, extracts features using utils.py,
        aligns them, and returns the probability of the review being 'REAL'.
        """
        if self.model is None or self.model_columns is None:
            logger.warning("Metadata model not loaded. Returning neutral 0.5 probability.")
            return 0.5

        # 1. Feature Engineering (using your established utils logic)
        # This returns a 1-row DataFrame
        features_df = extract_features(data_dict)

        # 2. Alignment & Imputation
        # Reindex ensures columns match training order; fill_value=0 handles any missing features
        aligned_df = features_df.reindex(columns=self.model_columns, fill_value=0)
        
        # 3. Inference
        # meta_model.predict_proba returns [prob_fake, prob_real]
        # We extract index 1 (Probability of being REAL)
        probs = self.model.predict_proba(aligned_df)[0]
        real_prob = float(probs[1])
        
        return real_prob

# --- Singleton Logic ---
_meta_instance = None

def get_meta_handler():
    """Returns a single shared instance of the MetaHandler."""
    global _meta_instance
    if _meta_instance is None:
        _meta_instance = MetaHandler()
    return _meta_instance