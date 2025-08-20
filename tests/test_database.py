import unittest
from unittest.mock import patch, MagicMock
from database.database import DatabaseManager

class TestDatabaseManager(unittest.TestCase):
    
    @patch('database.create_client')
    def test_connect_success(self, mock_create_client):
        """Test successful database connection"""
        mock_client = MagicMock()
        mock_client.table.return_value.select.return_value.limit.return_value.execute.return_value = MagicMock()
        mock_create_client.return_value = mock_client
        
        manager = DatabaseManager()
        result = manager.connect()
        
        self.assertTrue(result)
        self.assertTrue(manager.connected)
    
    @patch('database.create_client')
    def test_connect_failure(self, mock_create_client):
        """Test failed database connection"""
        mock_create_client.side_effect = Exception("Connection failed")
        
        manager = DatabaseManager()
        result = manager.connect()
        
        self.assertFalse(result)
        self.assertFalse(manager.connected)

if __name__ == '__main__':
    unittest.main()