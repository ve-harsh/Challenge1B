# Use minimal Python image
FROM python:3.10-slim

# Set workdir
WORKDIR /app

# Copy files
COPY . .

# Install dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libgl1-mesa-glx gcc poppler-utils && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python deps
RUN pip install --no-cache-dir \
    fitz pymupdf \
    sentence-transformers \
    scikit-learn

# Default command
CMD ["python", "main.py"]
