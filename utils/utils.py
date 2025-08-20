from log_setup import logger
from datetime import datetime, date, timedelta
import time
from typing import List, Dict, Any
from database.database import db_manager
from currency_service.currency_service import currency_service
from config.config import config

def collect_daily_rates(target_date: date = None) -> bool:
    """Collect exchange rates for a specific date"""
    if target_date is None:
        target_date = date.today()
    
    logger.info(f"Starting data collection for {target_date}")
    
    # Initialize currency service with fresh data
    if not currency_service.initialize_converter(force_download=True):
        logger.error("Failed to initialize currency converter")
        return False
    
    # Check if data is available for the target date
    available_date = currency_service.get_available_date(target_date)
    
    if available_date != target_date:
        logger.warning(f"No data available for {target_date}, using {available_date}")
        target_date = available_date
    
    if target_date is None:
        logger.error("No available data found")
        return False
    
    # Get all rates for the date
    rates = currency_service.get_all_rates_for_date(target_date)
    
    if not rates:
        logger.error("No rates retrieved")
        return False
    
    logger.info(f"Retrieved {len(rates)} exchange rates for {target_date}")
    
    # Filter out rates that already exist in database
    new_rates = []
    for rate in rates:
        if not db_manager.check_date_exists(rate['date'], 
                                          rate['base_currency'], 
                                          rate['target_currency']):
            new_rates.append(rate)
    
    if not new_rates:
        logger.info("All rates already exist in database")
        return True
    
    # Insert new rates into database
    success = db_manager.insert_exchange_rates(new_rates)
    
    if success:
        logger.info(f"Successfully stored {len(new_rates)} new exchange rates")
    else:
        logger.error("Failed to store exchange rates")
    
    return success

def backfill_historical_data() -> None:
    """Backfill historical data from start date to yesterday"""
    logger.info("Starting historical data backfill")
    
    # Initialize currency service
    if not currency_service.initialize_converter():
        logger.error("Failed to initialize currency converter")
        return
    
    # Get start and end dates
    start_date = date.fromisoformat(config.START_DATE)
    end_date = date.today() - timedelta(days=1)
    
    # Get latest date from database
    latest_db_date = db_manager.get_latest_date()
    if latest_db_date and latest_db_date > start_date:
        start_date = latest_db_date + timedelta(days=1)
        logger.info(f"Resuming backfill from {start_date}")
    
    # Get business days
    business_days = currency_service.get_business_days(start_date, end_date)
    
    if not business_days:
        logger.info("No business days to process")
        return
    
    logger.info(f"Processing {len(business_days)} business days")
    
    # Process each business day
    for i, business_day in enumerate(business_days, 1):
        logger.info(f"Processing day {i}/{len(business_days)}: {business_day}")
        
        # Check if data already exists for this day
        if db_manager.check_date_exists(business_day.isoformat(), 'EUR', 'USD'):
            logger.info(f"Data already exists for {business_day}, skipping")
            continue
        
        success = collect_daily_rates(business_day)
        
        if not success:
            logger.warning(f"Failed to process {business_day}")
        
        # Small delay to avoid overwhelming the system
        time.sleep(0.1)
    
    logger.info("Historical data backfill completed")