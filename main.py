#!/usr/bin/env python3
"""
Forex Data Collector - Main Application
Collects daily exchange rates from ECB and stores in Supabase
"""

import time
import signal
import sys
from datetime import date
from utils.utils import  collect_daily_rates, backfill_historical_data
from database.database import db_manager
from scheduler.scheduler import scheduler_manager
from config.config import config
from log_setup import logger

class ForexDataCollector:
    def __init__(self):
        self.running = True
        self.setup_signal_handlers()
    
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        scheduler_manager.shutdown()
        sys.exit(0)
    
    def initialize(self) -> bool:
        """Initialize the application"""
        try:
            logger.info("Initializing Forex Data Collector")
            
            # Validate configuration
            config.validate()
            
            # Connect to database
            if not db_manager.connect():
                logger.error("Failed to connect to database")
                return False
            
            logger.info("Application initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            return False
    
    def run_daily_collection(self):
        """Wrapper function for daily collection"""
        collect_daily_rates()
    
    def start(self):
        """Start the application"""
        if not self.initialize():
            sys.exit(1)
        
        try:
            # Run initial backfill
            logger.info("Running initial historical data backfill...")
            backfill_historical_data()
            
            # Schedule daily collection
            scheduler_manager.schedule_daily_task(self.run_daily_collection, config.COLLECTION_TIME)
            
            # Schedule retry tasks
            scheduler_manager.schedule_retry_tasks(self.run_daily_collection)
            
            # Start scheduler
            scheduler_manager.start()
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    app = ForexDataCollector()
    app.start()