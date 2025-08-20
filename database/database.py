from log_setup import logger
from datetime import datetime
from typing import List, Dict, Any
from supabase import create_client, Client
from config.config import config

class DatabaseManager:
    def __init__(self):
        self.client: Client = None
        self.connected = False
        
    def connect(self) -> bool:
        """Connect to Supabase database"""
        try:
            self.client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
            # Test connection
            self.client.table('exchange_rates').select('count', count='exact').limit(1).execute()
            self.connected = True
            logger.info("Successfully connected to Supabase")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Supabase: {e}")
            self.connected = False
            return False
    
    def insert_exchange_rates(self, rates: List[Dict[str, Any]]) -> bool:
        """Insert multiple exchange rates into database"""
        if not self.connected:
            logger.error("Database not connected")
            return False
        
        try:
            # Use upsert to handle duplicates
            result = self.client.table('exchange_rates').upsert(rates).execute()
            logger.info(f"Inserted/updated {len(rates)} exchange rates")
            return True
        except Exception as e:
            logger.error(f"Failed to insert exchange rates: {e}")
            return False
    
    def get_latest_date(self) -> datetime:
        """Get the latest date with data in the database"""
        if not self.connected:
            return None
        
        try:
            result = self.client.table('exchange_rates') \
                .select('date') \
                .order('date', desc=True) \
                .limit(1) \
                .execute()
            
            if result.data and len(result.data) > 0:
                return datetime.fromisoformat(result.data[0]['date']).date()
            return None
        except Exception as e:
            logger.error(f"Failed to get latest date: {e}")
            return None
    
    def check_date_exists(self, date: str, base_currency: str, target_currency: str) -> bool:
        """Check if data for specific date and currency pair exists"""
        if not self.connected:
            return False
        
        try:
            result = self.client.table('exchange_rates') \
                .select('id') \
                .eq('date', date) \
                .eq('base_currency', base_currency) \
                .eq('target_currency', target_currency) \
                .execute()
            
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Failed to check date existence: {e}")
            return False

# Global database instance
db_manager = DatabaseManager()