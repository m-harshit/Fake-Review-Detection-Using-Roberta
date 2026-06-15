FROM python:3.11-slim

WORKDIR /code

# Install system utilities needed for building packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch and ML dependencies
# Using the CPU-only PyTorch build keeps the image size small
RUN pip install --no-cache-dir \
    fastapi==0.111.0 \
    uvicorn==0.30.1 \
    pandas==2.2.2 \
    numpy==1.26.4 \
    scikit-learn==1.5.0 \
    joblib==1.4.2 \
    nltk==3.8.1 \
    textblob==0.18.0.post0 \
    pydantic==2.7.4 \
    torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu \
    transformers==4.41.2 \
    safetensors==0.4.3 \
    tokenizers==0.19.3

# Copy the rest of the application code
COPY . .

# Configure environment variables
ENV KMP_DUPLICATE_LIB_OK=TRUE
ENV PORT=7860

# Expose the port Hugging Face routes traffic to
EXPOSE 7860

# Start uvicorn server on port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
