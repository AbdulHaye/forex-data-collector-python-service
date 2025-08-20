from log_setup import logger
import os
import requests
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Set
from currency_converter import CurrencyConverter, ECB_URL
from dateutil.rrule import rrule, DAILY, MO, TU, WE, TH, FR
from config.config import config

class CurrencyService:
    def __init__(self):
        self.converter = None
        self.available_currencies = set()
        self.last_download_date = None
        
    def initialize_converter(self, force_download: bool = False) -> bool:
        """Initialize currency converter with fresh data"""
        try:
            cache_file = self._get_cache_filename()
            
            if force_download or not os.path.exists(cache_file):
                logger.info("Downloading fresh ECB data...")
                self._download_ecb_data(cache_file)
            
            self.converter = CurrencyConverter(cache_file, 
                                             fallback_on_missing_rate=True,
                                             fallback_on_wrong_date=True)
            
            self.available_currencies = self.converter.currencies
            logger.info(f"Available currencies: {len(self.available_currencies)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize currency converter: {e}")
            return False
    
    def _get_cache_filename(self) -> str:
        """Get cache filename with current date"""
        today = date.today().isoformat()
        return os.path.join(config.CACHE_DIR, f"ecb_data_{today}.zip")
    
    def _download_ecb_data(self, cache_file: str) -> None:
        """Download ECB data and save to cache file"""
        try:
            response = requests.get(ECB_URL, timeout=30)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(cache_file), exist_ok=True)
            with open(cache_file, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"ECB data downloaded and cached to {cache_file}")
            
        except requests.RequestException as e:
            logger.error(f"Failed to download ECB data: {e}")
            raise
    
    def get_business_days(self, start_date: date, end_date: date) -> List[date]:
        """Get list of business days between two dates"""
        business_days = list(rrule(DAILY, 
                                 dtstart=start_date, 
                                 until=end_date,
                                 byweekday=(MO, TU, WE, TH, FR)))
        return [d.date() for d in business_days]
    
    def get_exchange_rate(self, base_currency: str, target_currency: str, 
                         rate_date: date) -> float:
        """Get exchange rate for specific currency pair and date"""
        try:
            if base_currency == target_currency:
                return 1.0
            
            rate = self.converter.convert(1.0, base_currency, target_currency, 
                                        date=rate_date)
            return round(rate, 6)
            
        except Exception as e:
            logger.warning(f"Failed to get rate for {base_currency}->{target_currency} "
                          f"on {rate_date}: {e}")
            return None
    
    def get_all_rates_for_date(self, rate_date: date) -> List[Dict[str, Any]]:
        """Get all required exchange rates for a specific date"""
        rates = []
        
        for base_currency in config.BASE_CURRENCIES:
            for target_currency in self.available_currencies:
                if base_currency == target_currency:
                    continue
                
                rate = self.get_exchange_rate(base_currency, target_currency, rate_date)
                
                if rate is not None:
                    rates.append({
                        'date': rate_date.isoformat(),
                        'base_currency': base_currency,
                        'target_currency': target_currency,
                        'exchange_rate': rate
                    })
        
        return rates
    
    def get_available_date(self, target_date: date) -> date:
        """Get the most recent available date with data"""
        current_date = target_date
        
        # Try up to 7 days back to find available data
        for _ in range(7):
            try:
                # Test if we can get a rate for this date
                test_rate = self.get_exchange_rate('EUR', 'USD', current_date)
                if test_rate is not None:
                    return current_date
            except:
                pass
            
            current_date -= timedelta(days=1)
        
        return None

# Global currency service instance
currency_service = CurrencyService()