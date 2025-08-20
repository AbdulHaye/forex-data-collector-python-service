import os
from log_setup import logger
from datetime import time
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Supabase configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # Scheduler configuration
    TIMEZONE = os.getenv('TIMEZONE', 'Europe/Zurich')
    COLLECTION_TIME = os.getenv('COLLECTION_TIME', '16:30')
    
    # Parse retry times
    retry_times_str = os.getenv('RETRY_TIMES', '17:30,18:30')
    RETRY_TIMES = [time.fromisoformat(t) for t in retry_times_str.split(',')]
    
    # Data configuration
    START_DATE = '2024-01-01'
    CACHE_DIR = '/app/data_cache'
    
    # Currency pairs
    BASE_CURRENCIES = ['EUR', 'USD']
    
    def validate(self):
        """Validate configuration"""
        if not self.SUPABASE_URL:
            raise ValueError("SUPABASE_URL environment variable is required")
        if not self.SUPABASE_KEY:
            raise ValueError("SUPABASE_KEY environment variable is required")
        
        logger.info(f"Configuration loaded: TIMEZONE={self.TIMEZONE}, COLLECTION_TIME={self.COLLECTION_TIME}")

# Global config instance
config = Config()