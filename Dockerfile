FROM python:3.11-slim

WORKDIR /code

# Install system utilities needed for building packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 1. Install CPU-only PyTorch first
# (Specifying --index-url separately prevents pip from trying to resolve standard packages against the PyTorch registry)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# 2. Install all other ML and web dependencies from standard PyPI
# (We pin scikit-learn to 1.6.1 to match the metadata RF model's pickling version)
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    pandas \
    numpy \
    scikit-learn==1.6.1 \
    joblib \
    nltk \
    textblob \
    pydantic \
    transformers \
    safetensors \
    tokenizers

# Copy the rest of the application code
COPY . .

# Configure environment variables
ENV KMP_DUPLICATE_LIB_OK=TRUE
ENV PORT=7860

# Expose the port Hugging Face routes traffic to
EXPOSE 7860

# Start uvicorn server on port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
