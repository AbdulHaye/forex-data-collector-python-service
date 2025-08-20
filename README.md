# Forex Data Collector

A Python service that collects daily exchange rates from the European Central Bank (ECB) and stores them in a Supabase database.

## Features

- Daily collection of 82 currency pairs (EUR→41 currencies + USD→41 currencies)
- Automatic backfill of historical data from January 1, 2024
- Handles ECB data availability (no updates on weekends/holidays)
- Scheduled collection with retry mechanism
- Docker containerization
- Robust error handling and logging

## Setup

### Prerequisites

- Python 3.10+ (for non-Docker setup)
- Docker (for Docker setup)
- Supabase account with database

### Environment Variables

Create a `.env` file in the project root directory:

```env
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
TIMEZONE=Europe/Zurich
COLLECTION_TIME=16:30
RETRY_TIMES=17:30,18:30
LOG_LEVEL=INFO
```

### Database Schema
You should be run this SQL query in your db.table in supabase

```SQL
CREATE TABLE exchange_rates (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    base_currency VARCHAR(3) NOT NULL,
    target_currency VARCHAR(3) NOT NULL,
    exchange_rate DECIMAL(18, 6) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(date, base_currency, target_currency)
);
```

### Run by using docker
Option 1: Running with Docker (Recommended)  
Step 1: Build the Docker Image  
bash  
# Build the Docker image  
docker build -t forex-data-collector .  

Step 2: Run the Container  
bash  
# Run the container in detached mode  
docker run -d \  
  --name forex-collector \  
  --env-file .env \  
  -v forex-data-cache:/data_cache \  
  forex-data-collector  

# Check the logs to see if it's working  
docker logs forex-collector  

# Follow logs in real-time  
docker logs -f forex-collector  



### Run without using docker

Option 2: Running without Docker  
# Create directory for caching ECB data  
mkdir -p data_cache  

Step 5: Run the Application  
bash  
python main.py  

Step 6: Run Tests (Optional)  
bash  
python -m pytest tests/ -v  
