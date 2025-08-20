import unittest
from datetime import date
from unittest.mock import patch, MagicMock
from currency_service.currency_service import CurrencyService

class TestCurrencyService(unittest.TestCase):
    
    @patch('currency_service.requests.get')
    @patch('currency_service.CurrencyConverter')
    def test_initialize_converter(self, mock_converter, mock_get):
        """Test initializing currency converter"""
        mock_response = MagicMock()
        mock_response.content = b'test content'
        mock_get.return_value = mock_response
        
        service = CurrencyService()
        result = service.initialize_converter(force_download=True)
        
        self.assertTrue(result)
        mock_get.assert_called_once()
    
    def test_get_business_days(self):
        """Test getting business days"""
        service = CurrencyService()
        start_date = date(2024, 1, 1)  # Monday
        end_date = date(2024, 1, 7)    # Sunday
        
        business_days = service.get_business_days(start_date, end_date)
        
        # Should get 5 business days (Mon-Fri)
        self.assertEqual(len(business_days), 5)
        self.assertEqual(business_days[0], date(2024, 1, 1))
        self.assertEqual(business_days[-1], date(2024, 1, 5))

if __name__ == '__main__':
    unittest.main()