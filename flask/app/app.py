from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text, desc, func
import os
import sys
import traceback
import time
from datetime import datetime, timedelta

# Import models
from models import db, DimDate, DimCompany, FactMarketMetrics

# Print startup message for debugging
print("Starting Flask application...", file=sys.stderr)

# Initialize Flask app
app = Flask(__name__)

# Database configuration - use SQLite as fallback
database_url = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with app
db.init_app(app)
migrate = Migrate(app, db)

# Default route
@app.route('/')
def home():
    db_status = "connected" 
    try:
        # Try simple query to check connection
        with app.app_context():
            db.session.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "message": "Welcome to Stock Market API",
        "database_status": db_status,
        "endpoints": {
            "market_data": "/api/market",
            "stock_data": "/api/stock/<ticker>"
        }
    })

# Route to view all tables
@app.route('/tables')
def view_tables():
    try:
        # Use text() function explicitly
        query = text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
        
        # Execute with explicit connection
        with db.engine.connect() as conn:
            result = conn.execute(query)
            tables = [row[0] for row in result]
        
        return jsonify({"tables": tables})
    except Exception as e:
        print(f"Error in view_tables: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({"error": str(e)}), 500

# User Story 1: Retrieve Stock Market Data for ML Model
@app.route('/api/market')
def get_market_data():
    start_time = time.time()
    try:
        # Get parameters with defaults
        days = request.args.get('days', '60')
        to_date = request.args.get('to', datetime.now().strftime('%Y-%m-%d'))
        from_date = request.args.get('from', None)
        country = request.args.get('country', 'US')
        
        # Convert 'to' to datetime
        try:
            to_datetime = datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            to_datetime = datetime.now()
            
        # Calculate 'from' date based on days parameter if not provided
        if from_date is None:
            if days.lower() == 'all':
                from_datetime = datetime(1900, 1, 1)  # Far past date to get all records
            else:
                try:
                    days_int = int(days)
                    from_datetime = to_datetime - timedelta(days=days_int)
                except ValueError:
                    from_datetime = to_datetime - timedelta(days=60)  # Default
        else:
            try:
                from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
            except ValueError:
                from_datetime = to_datetime - timedelta(days=60)  # Default
        
        # Query for market data
        query = db.session.query(
            FactMarketMetrics, 
            DimDate, 
            DimCompany
        ).join(
            DimDate, 
            FactMarketMetrics.fk_date_id == DimDate.sk_date_id
        ).join(
            DimCompany, 
            FactMarketMetrics.fk_company_id == DimCompany.sk_company_id
        ).filter(
            DimCompany.country == country,
            DimDate.datetime >= from_datetime,
            DimDate.datetime <= to_datetime
        ).order_by(
            DimCompany.symbol,
            DimDate.datetime
        )
        
        # Execute query
        results = query.all()
        
        # Format the results
        formatted_results = []
        for metric, date, company in results:
            formatted_results.append({
                'symbol': company.symbol,
                'company_name': company.company_name,
                'sector': company.sector,
                'industry': company.industry,
                'date': date.date,
                'datetime': date.datetime.isoformat() if date.datetime else None,
                'current_price': float(metric.current_price) if metric.current_price else None,
                'change': float(metric.change) if metric.change else None,
                'change_percentage': float(metric.change_percentage) if metric.change_percentage else None,
                'volume': metric.volume,
                'day_low': float(metric.day_low) if metric.day_low else None,
                'day_high': float(metric.day_high) if metric.day_high else None,
                'market_cap': float(metric.market_cap) if metric.market_cap else None
            })
        
        execution_time = time.time() - start_time
        record_count = len(formatted_results)
        
        # Log details
        print(f"Market data query: retrieved {record_count} records in {execution_time:.2f} seconds", file=sys.stderr)
        
        return jsonify({
            'data': formatted_results,
            'metadata': {
                'record_count': record_count,
                'execution_time_seconds': execution_time,
                'parameters': {
                    'days': days,
                    'to_date': to_date,
                    'from_date': from_date if from_date else from_datetime.strftime('%Y-%m-%d'),
                    'country': country
                }
            }
        })
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"Error in get_market_data: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({
            "error": str(e),
            'metadata': {
                'execution_time_seconds': execution_time,
                'parameters': request.args
            }
        }), 500

# User Story 2: Retrieve Single Stock Data for ML Model
@app.route('/api/stock/<ticker>')
def get_stock_data(ticker):
    start_time = time.time()
    try:
        # Get parameters with defaults
        days = request.args.get('days', '60')
        to_date = request.args.get('to', datetime.now().strftime('%Y-%m-%d'))
        from_date = request.args.get('from', None)
        
        # Convert 'to' to datetime
        try:
            to_datetime = datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            to_datetime = datetime.now()
            
        # Calculate 'from' date based on days parameter if not provided
        if from_date is None:
            if days.lower() == 'all':
                from_datetime = datetime(1900, 1, 1)  # Far past date to get all records
            else:
                try:
                    days_int = int(days)
                    from_datetime = to_datetime - timedelta(days=days_int)
                except ValueError:
                    from_datetime = to_datetime - timedelta(days=60)  # Default
        else:
            try:
                from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
            except ValueError:
                from_datetime = to_datetime - timedelta(days=60)  # Default
        
        # First verify the stock exists
        company = DimCompany.query.filter_by(symbol=ticker.upper()).first()
        if not company:
            return jsonify({
                "error": f"Stock with ticker '{ticker}' not found",
                'metadata': {
                    'execution_time_seconds': time.time() - start_time,
                    'parameters': {
                        'ticker': ticker,
                        'days': days,
                        'to_date': to_date,
                        'from_date': from_date
                    }
                }
            }), 404
        
        # Query for specific stock data
        query = db.session.query(
            FactMarketMetrics, 
            DimDate
        ).join(
            DimDate, 
            FactMarketMetrics.fk_date_id == DimDate.sk_date_id
        ).filter(
            FactMarketMetrics.fk_company_id == company.sk_company_id,
            DimDate.datetime >= from_datetime,
            DimDate.datetime <= to_datetime
        ).order_by(
            DimDate.datetime
        )
        
        # Execute query
        results = query.all()
        
        # Format the results
        formatted_results = []
        for metric, date in results:
            formatted_results.append({
                'date': date.date,
                'datetime': date.datetime.isoformat() if date.datetime else None,
                'current_price': float(metric.current_price) if metric.current_price else None,
                'change': float(metric.change) if metric.change else None,
                'change_percentage': float(metric.change_percentage) if metric.change_percentage else None,
                'volume': metric.volume,
                'day_low': float(metric.day_low) if metric.day_low else None,
                'day_high': float(metric.day_high) if metric.day_high else None,
                'year_low': float(metric.year_low) if metric.year_low else None,
                'year_high': float(metric.year_high) if metric.year_high else None,
                'price_average_50': float(metric.price_average_50) if metric.price_average_50 else None,
                'price_average_200': float(metric.price_average_200) if metric.price_average_200 else None,
                'market_cap': float(metric.market_cap) if metric.market_cap else None
            })
        
        execution_time = time.time() - start_time
        record_count = len(formatted_results)
        
        # Log details
        print(f"Stock data query for {ticker}: retrieved {record_count} records in {execution_time:.2f} seconds", file=sys.stderr)
        
        return jsonify({
            'data': formatted_results,
            'company': {
                'symbol': company.symbol,
                'name': company.company_name,
                'sector': company.sector,
                'industry': company.industry,
                'country': company.country,
                'beta': float(company.beta) if company.beta else None,
                'market_cap': float(company.mkt_cap) if company.mkt_cap else None
            },
            'metadata': {
                'record_count': record_count,
                'execution_time_seconds': execution_time,
                'parameters': {
                    'ticker': ticker,
                    'days': days,
                    'to_date': to_date,
                    'from_date': from_date if from_date else from_datetime.strftime('%Y-%m-%d')
                }
            }
        })
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"Error in get_stock_data: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({
            "error": str(e),
            'metadata': {
                'execution_time_seconds': execution_time,
                'parameters': {
                    'ticker': ticker,
                    **request.args
                }
            }
        }), 500

# Run the app
if __name__ == '__main__':
    print("Flask app is starting...", file=sys.stderr)
    app.run(host='0.0.0.0', debug=True)