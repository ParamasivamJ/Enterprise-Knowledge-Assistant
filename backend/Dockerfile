# Use official slim Python image
FROM python:3.11-slim

# Set work directory
WORKDIR /workspace

# Install system dependencies (build-essential needed for some python packages if compiling)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app/ ./app/

# Create directory for file uploads
RUN mkdir -p uploads

# Expose port 8000
EXPOSE 8000

# Start FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
