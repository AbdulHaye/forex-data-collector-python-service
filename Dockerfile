FROM python:3.10-slim

WORKDIR /

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for caching ECB data
RUN mkdir -p /data_cache

CMD ["python", "-u", "main.py"]