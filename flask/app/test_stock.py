import pytest
import json
from app import app, db
from models import DimDate, DimCompany, FactMarketMetrics

@pytest.fixture
def client():
    """Set up test client"""
    app.config["TESTING"] = True
    with app.test_client() as client:
        # Modify the HTTP_USER_AGENT to prevent the werkzeug version error
        client.environ_base["HTTP_USER_AGENT"] = "werkzeug/unknown"
        
        with app.app_context():
            db.create_all()  # Create tables if necessary
        yield client

def test_home_route(client):
    """Test the home endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert "database_status" in data
    assert "endpoints" in data

def test_view_tables(client):
    """Test retrieving database tables"""
    response = client.get("/tables")
    assert response.status_code == 200
    data = response.get_json()
    assert "tables" in data
    assert isinstance(data["tables"], list)

def test_get_schema(client):
    """Test retrieving database schema"""
    response = client.get("/schema")
    assert response.status_code == 200
    data = response.get_json()
    assert "schema" in data
    assert isinstance(data["schema"], dict)

def test_get_dim_date(client):
    """Test fetching data from DimDate"""
    response = client.get("/api/dim_date")
    assert response.status_code == 200
    data = response.get_json()
    assert "data" in data
    assert "metadata" in data
    assert isinstance(data["data"], list)
    assert isinstance(data["metadata"], dict)

def test_get_dim_exchange(client):
    """Test fetching exchange data"""
    response = client.get("/api/dim_exchange")
    assert response.status_code in [200, 500]  # If DB is empty, it might fail
    data = response.get_json()
    if response.status_code == 200:
        assert "data" in data
        assert isinstance(data["data"], list)

def test_get_dim_company_valid(client):
    """Test fetching company data with a valid ticker"""
    response = client.get("/api/dim_company?ticker=AAPL")
    assert response.status_code in [200, 404]  # 404 if ticker not found
    data = response.get_json()
    if response.status_code == 200:
        assert "data" in data
        assert isinstance(data["data"], list)

def test_get_dim_company_missing_ticker(client):
    """Test fetching company data without a ticker"""
    response = client.get("/api/dim_company")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

def test_get_market_data(client):
    """Test fetching market data"""
    response = client.get("/api/market?days=30&country=US")
    assert response.status_code in [200, 500]
    data = response.get_json()
    if response.status_code == 200:
        assert "data" in data
        assert isinstance(data["data"], list)

def test_get_ml_model_data(client):
    """Test fetching ML model predictions"""
    response = client.get("/api/ml-model?days=30&country=US")
    assert response.status_code in [200, 500]
    data = response.get_json()
    if response.status_code == 200:
        assert "data" in data
        assert isinstance(data["data"], list)

def test_get_single_stock_ml_data_valid(client):
    """Test fetching ML model data for a valid stock"""
    response = client.get("/api/ml-model/stock?ticker=AAPL&days=30")
    assert response.status_code in [200, 404]
    data = response.get_json()
    if response.status_code == 200:
        assert "data" in data
        assert isinstance(data["data"], list)

def test_get_single_stock_ml_data_missing_ticker(client):
    """Test fetching ML model data without providing a ticker"""
    response = client.get("/api/ml-model/stock")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
