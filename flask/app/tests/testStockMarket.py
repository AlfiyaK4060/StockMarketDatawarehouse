import unittest
import json
from app import app, db
from models import Stock, Market

class StockMarketAPITestCase(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.create_all()
            cls.seed_test_data()
    
    @classmethod
    def seed_test_data(cls):
        market = Market(name='NASDAQ')
        db.session.add(market)
        db.session.commit()
        stock1 = Stock(ticker='AAPL', name='Apple Inc.', market_id=market.id, price=150.0)
        stock2 = Stock(ticker='TSLA', name='Tesla Inc.', market_id=market.id, price=700.0)
        db.session.add_all([stock1, stock2])
        db.session.commit()

    def test_get_stocks(self):
        response = self.client.get('/api/stocks')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(data['stocks']), 0)
    
    def test_get_single_stock(self):
        response = self.client.get('/api/stocks/AAPL')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['ticker'], 'AAPL')
    
    def test_get_market(self):
        response = self.client.get('/api/markets')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(data['markets']), 0)
    
    def test_pagination(self):
        response = self.client.get('/api/stocks?page=1&limit=1')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['stocks']), 1)
    
    def test_stock_filter_by_price(self):
        response = self.client.get('/api/stocks?min_price=100&max_price=200')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        for stock in data['stocks']:
            self.assertTrue(100 <= stock['price'] <= 200)
    
    def test_stock_not_found(self):
        response = self.client.get('/api/stocks/INVALID')
        self.assertEqual(response.status_code, 404)
    
    def test_add_stock(self):
        response = self.client.post('/api/stocks', json={
            'ticker': 'GOOGL',
            'name': 'Alphabet Inc.',
            'market_id': 1,
            'price': 2800.0
        })
        self.assertEqual(response.status_code, 201)
    
    def test_invalid_stock_creation(self):
        response = self.client.post('/api/stocks', json={})
        self.assertEqual(response.status_code, 400)
    
    def test_update_stock(self):
        response = self.client.put('/api/stocks/AAPL', json={'price': 160.0})
        self.assertEqual(response.status_code, 200)
        updated_stock = self.client.get('/api/stocks/AAPL')
        data = json.loads(updated_stock.data)
        self.assertEqual(data['price'], 160.0)
    
    def test_delete_stock(self):
        response = self.client.delete('/api/stocks/AAPL')
        self.assertEqual(response.status_code, 204)
    
    def test_delete_nonexistent_stock(self):
        response = self.client.delete('/api/stocks/XYZ')
        self.assertEqual(response.status_code, 404)
    
    def test_update_nonexistent_stock(self):
        response = self.client.put('/api/stocks/XYZ', json={'price': 200.0})
        self.assertEqual(response.status_code, 404)
    
    def test_filter_market_stocks(self):
        response = self.client.get('/api/stocks?market=NASDAQ')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(data['stocks']), 0)
    
    def test_get_invalid_market(self):
        response = self.client.get('/api/markets/INVALID')
        self.assertEqual(response.status_code, 404)
    
    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.session.remove()
            db.drop_all()

if __name__ == '__main__':
    unittest.main()