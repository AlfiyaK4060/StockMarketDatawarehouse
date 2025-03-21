import pytest
from flask import Flask
from app import app, db
from models import DimCompany, DimDate, FactMarketMetrics
from datetime import datetime, timedelta

@pytest.fixture(scope="module")
def test_client():
    """Set up the test client and initialize the database."""
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"  # Use in-memory DB for testing
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()

def add_dummy_data():
    """Helper function to insert test data into the database."""
    company = DimCompany(
        sk_company_id=1, symbol="AAPL", company_name="Apple Inc.", sector="Technology",
        industry="Consumer Electronics", country="US"
    )
    date_entry = DimDate(
        sk_date_id=1, datetime=datetime.now(), date="2024-03-15", year=2024
    )
    market_metric = FactMarketMetrics(
        sk_market_metrics_id=1, fk_company_id=1, fk_date_id=1, current_price=150.0, volume=1000000
    )

    db.session.add_all([company, date_entry, market_metric])
    db.session.commit()

# ---- Test Cases ----

def test_home_route(test_client):
    """Test home route returns expected keys."""
    response = test_client.get("/")
    data = response.get_json()
    assert response.status_code == 200
    assert "message" in data
    assert "database_status" in data
    assert "endpoints" in data

def test_view_tables(test_client):
    """Test viewing available tables in the database."""
    response = test_client.get("/tables")
    data = response.get_json()
    assert response.status_code == 200
    assert "tables" in data

def test_market_data_default(test_client):
    """Test market data retrieval with default parameters."""
    add_dummy_data()
    response = test_client.get("/api/market")
    data = response.get_json()
    assert response.status_code == 200
    assert isinstance(data["data"], list)

def test_market_data_with_date_range(test_client):
    """Test market data retrieval within a specified date range."""
    response = test_client.get("/api/market?from=2024-01-01&to=2024-03-01")
    data = response.get_json()
    assert response.status_code == 200
    assert isinstance(data["data"], list)

def test_market_data_invalid_country(test_client):
    """Test market data retrieval for a non-existent country."""
    response = test_client.get("/api/market?country=XYZ")
    data = response.get_json()
    assert response.status_code == 200
    assert data["data"] == []

def test_stock_data_valid_ticker(test_client):
    """Test stock data retrieval for a valid ticker."""
    response = test_client.get("/api/stock/AAPL")
    data = response.get_json()
    assert response.status_code == 200
    assert data["company"]["symbol"] == "AAPL"

def test_stock_data_invalid_ticker(test_client):
    """Test stock data retrieval for an invalid ticker."""
    response = test_client.get("/api/stock/INVALID")
    data = response.get_json()
    assert response.status_code == 404
    assert "error" in data

def test_stock_data_with_date_range(test_client):
    """Test stock data retrieval within a specified date range."""
    response = test_client.get("/api/stock/AAPL?from=2024-01-01&to=2024-03-01")
    data = response.get_json()
    assert response.status_code == 200
    assert isinstance(data["data"], list)

def test_stock_data_large_time_frame(test_client):
    """Test retrieving stock data with a large time frame."""
    response = test_client.get("/api/stock/AAPL?days=365")
    data = response.get_json()
    assert response.status_code == 200
    assert isinstance(data["data"], list)

def test_api_performance(test_client):
    """Ensure API response time is within an acceptable range."""
    import time
    start_time = time.time()
    response = test_client.get("/api/market")
    elapsed_time = time.time() - start_time
    assert response.status_code == 200
    assert elapsed_time < 2  # Ensure response is under 2 seconds

