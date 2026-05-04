import torch
import torch.nn.functional as F
import numpy as np
import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Setup logging
logger = logging.getLogger(__name__)

class ModelHandler:
    def __init__(self, model_path="fake_review_model"):
        """
        Initializes the model and tokenizer from the local fine-tuned directory.
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Loading model to device: {self.device}")
        
        try:
            # Load tokenizer and model from your local folder
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            self.model.to(self.device)
            self.model.eval()  # Crucial: Disable dropout for consistent inference
            logger.info("Model and tokenizer loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading model from {model_path}: {e}")
            raise e

    def predict_and_explain(self, text: str, max_length: int = 128):
        """
        Runs inference and calculates saliency scores (word importance).
        Returns prediction, confidence, and the list of important words.
        """
        # 1. Tokenization
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            truncation=True, 
            max_length=max_length
        ).to(self.device)
        
        input_ids = inputs["input_ids"]
        
        # 2. Prepare for Saliency (Gradient Tracking)
        self.model.zero_grad()
        emb_layer = self.model.get_input_embeddings()
        embeddings = emb_layer(input_ids)
        embeddings.retain_grad() # Track gradients on the embedding layer
        
        # 3. Forward Pass
        # We pass inputs_embeds instead of input_ids so we can backprop to the embeddings
        outputs = self.model(
            inputs_embeds=embeddings, 
            attention_mask=inputs["attention_mask"]
        )
        
        logits = outputs.logits
        probs = F.softmax(logits, dim=-1)
        pred_idx = torch.argmax(probs).item()
        confidence = probs[0, pred_idx].item()
        
        # 4. Backward Pass (Identify word influence)
        # We calculate gradients with respect to the predicted class
        logits[0, pred_idx].backward()
        
        # Importance = sum of absolute gradients across the embedding dimensions
        importance = embeddings.grad.abs().sum(dim=-1)[0]
        # Min-Max Normalize scores to [0, 1] for easier visualization
        importance = (importance / (importance.max() + 1e-8)).cpu().detach().numpy()
        
        # 5. Token Cleanup & Mapping
        raw_tokens = self.tokenizer.convert_ids_to_tokens(input_ids[0])
        highlights = []
        
        for i, token in enumerate(raw_tokens):
            # Clean RoBERTa-specific characters (Ġ represents a space)
            clean_token = token.replace('Ġ', '')
            
            # Filter out special BERT/RoBERTa tokens
            if clean_token not in ["<s>", "</s>", "<pad>"]:
                highlights.append({
                    "word": clean_token,
                    "importance_score": round(float(importance[i]), 4)
                })
        
        # Extract the top 5 most influential words for quick summary
        top_indicators = sorted(highlights, key=lambda x: x["importance_score"], reverse=True)[:5]

        return {
            "prediction": "FAKE" if pred_idx == 0 else "REAL",
            "confidence": round(confidence, 4),
            "important_words": top_indicators,
            "full_highlights": highlights
        }

# --- FastAPI Singleton Pattern ---

_handler_instance = None

def get_model_handler():
    """
    Ensures the ModelHandler is only instantiated once (Singleton).
    This prevents memory leaks and slow response times.
    """
    global _handler_instance
    if _handler_instance is None:
        # Assumes the 'fake_review_model' folder is in the same directory as this file
        _handler_instance = ModelHandler(model_path="fake_review_model")
    return _handler_instance