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

    #code being tested    
    #@app.route('/api/stocks')
    #def get_stocks():
    #stocks = Stock.query.all()
    #return jsonify({"stocks": [stock.to_dict() for stock in stocks]})

    def test_get_stocks(self):
        response = self.client.get('/api/stocks')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(data['stocks']), 0)
   
    #Test Passing Indication:
    #Status code 200
    #The number of stocks in the response is greater than 0

    #code being tested    
   # @app.route('/api/stocks/<ticker>')
#    def get_stock(ticker):
#     stock = Stock.query.filter_by(ticker=ticker).first()
#     if not stock:
#         return jsonify({"error": "Stock not found"}), 404
#     return jsonify(stock.to_dict())


    def test_get_single_stock(self):
        response = self.client.get('/api/stocks/AAPL')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['ticker'], 'AAPL')

# Test Passing Indication:
# Status code 200
# The stock returned has ticker "AAPL"


# Code being tested:
# @app.route('/api/markets')
# def get_markets():
#     markets = Market.query.all()
#     return jsonify({"markets": [market.to_dict() for market in markets]})
    
    def test_get_market(self):
        response = self.client.get('/api/markets')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(data['markets']), 0)
# Test Passing Indication:
# Status code 200
# The number of markets in the response is greater than 0

# Code being tested: 
# @app.route('/api/stocks')
# def get_stocks():
#     page = request.args.get('page', 1, type=int)
#     limit = request.args.get('limit', 10, type=int)
#     stocks = Stock.query.paginate(page, limit, False).items
#     return jsonify({"stocks": [stock.to_dict() for stock in stocks]})

    def test_pagination(self):
        response = self.client.get('/api/stocks?page=1&limit=1')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['stocks']), 1)
# Test Passing Indication:
# Status code 200
# Exactly 1 stock is returned in the response

# Code being tested:
# @app.route('/api/stocks')
# def get_stocks():
#     min_price = request.args.get('min_price', type=float)
#     max_price = request.args.get('max_price', type=float)
#     query = Stock.query
#     if min_price:
#         query = query.filter(Stock.price >= min_price)
#     if max_price:
#         query = query.filter(Stock.price <= max_price)
#     stocks = query.all()
#     return jsonify({"stocks": [stock.to_dict() for stock in stocks]})

    
    def test_stock_filter_by_price(self):
        response = self.client.get('/api/stocks?min_price=100&max_price=200')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        for stock in data['stocks']:
            self.assertTrue(100 <= stock['price'] <= 200)
# Test Passing Indication:
# Status code 200
# Each stock returned has a price between 100 and 200

# Code being tested:
# @app.route('/api/stocks/<ticker>')
# def get_stock(ticker):
#     stock = Stock.query.filter_by(ticker=ticker).first()
#     if not stock:
#         return jsonify({"error": "Stock not found"}), 404
#     return jsonify(stock.to_dict())
 
    def test_stock_not_found(self):
        response = self.client.get('/api/stocks/INVALID')
        self.assertEqual(response.status_code, 404)
# Test Passing Indication:
# Status code 404

  # Code being tested:
#   @app.route('/api/stocks', methods=['POST'])
# def add_stock():
#     data = request.get_json()
#     stock = Stock(**data)
#     db.session.add(stock)
#     db.session.commit()
#     return jsonify(stock.to_dict()), 201

    def test_add_stock(self):
        response = self.client.post('/api/stocks', json={
            'ticker': 'GOOGL',
            'name': 'Alphabet Inc.',
            'market_id': 1,
            'price': 2800.0
        })
        self.assertEqual(response.status_code, 201)
# Test Passing Indication:
# Status code 201

# Code being tested:
#  @app.route('/api/stocks', methods=['POST'])
# def add_stock():
#     data = request.get_json()
#     if not data.get('ticker'):
#         return jsonify({"error": "Missing ticker"}), 400
#     stock = Stock(**data)
#     db.session.add(stock)
#     db.session.commit()
#     return jsonify(stock.to_dict()), 201

    def test_invalid_stock_creation(self):
        response = self.client.post('/api/stocks', json={})
        self.assertEqual(response.status_code, 400)
# Test Passing Indication:
# Status code 400

  # Code being tested:
#   @app.route('/api/stocks/<ticker>', methods=['PUT'])
# def update_stock(ticker):
#     stock = Stock.query.filter_by(ticker=ticker).first()
#     if not stock:
#         return jsonify({"error": "Stock not found"}), 404
#     data = request.get_json()
#     stock.price = data.get('price', stock.price)
#     db.session.commit()
#     return jsonify(stock.to_dict())

    def test_update_stock(self):
        response = self.client.put('/api/stocks/AAPL', json={'price': 160.0})
        self.assertEqual(response.status_code, 200)
        updated_stock = self.client.get('/api/stocks/AAPL')
        data = json.loads(updated_stock.data)
        self.assertEqual(data['price'], 160.0)
# Test Passing Indication:
# Status code 200
# Stock price updates correctly

  # Code being tested:
#   @app.route('/api/stocks/<ticker>', methods=['DELETE'])
# def delete_stock(ticker):
#     stock = Stock.query.filter_by(ticker=ticker).first()
#     if not stock:
#         return jsonify({"error": "Stock not found"}), 404
#     db.session.delete(stock)
#     db.session.commit()
#     return '', 204

  
    def test_delete_stock(self):
        response = self.client.delete('/api/stocks/AAPL')
        self.assertEqual(response.status_code, 204)
# Test Passing Indication:
# Status code 204
# Stock is removed from database

    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.session.remove()
            db.drop_all()

if __name__ == '__main__':
    unittest.main()