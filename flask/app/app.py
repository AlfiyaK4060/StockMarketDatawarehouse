from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import text
import os
import sys
import traceback
import time
import logging
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from models import db, DimDate, DimCompany, FactMarketMetrics
import pytest
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
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/app/logs/api.log", mode='a'),  # Append logs to file
        logging.StreamHandler(sys.stdout)  # Print logs to console
    ]
)

# Default route
@app.route('/')
def home():
    db_status = "connected"
    try:
        # Try simple query to check connection
        with app.app_context():
            db.session.execute(text("SELECT 1"))
    except SQLAlchemyError as e:
        db_status = f"error: {str(e)}"

    return jsonify({
        "message": "Welcome to Stock Market API",
        "database_status": db_status,
        "endpoints": {
            "market_data": "/api/market",
            "stock_data": "/api/stock/<ticker>"
        }
    })


def log_request(endpoint, record_count, execution_time):
    logging.info(f"API: {endpoint} | Records Retrieved: {record_count} | Execution Time: {execution_time:.4f} seconds")

# Route to view all tables
@app.route('/tables')
def view_tables():
    try:
        # Adjust query for SQLite compatibility
        if "sqlite" in database_url:
            query = text("SELECT name FROM sqlite_master WHERE type='table'")
        else:
            query = text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")

        # Execute with explicit connection
        with db.engine.connect() as conn:
            result = conn.execute(query)
            tables = [row[0] for row in result]

        return jsonify({"tables": tables})
    except SQLAlchemyError as e:
        print(f"Error in view_tables: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({"error": str(e)}), 500



# Route to get schema structure
@app.route('/schema')
def get_schema():
    try:
        schema_info = {}
        
        # Get all tables
        if "sqlite" in database_url:
            tables_query = text("SELECT name FROM sqlite_master WHERE type='table'")
        else:
            tables_query = text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
            
        with db.engine.connect() as conn:
            tables_result = conn.execute(tables_query)
            tables = [row[0] for row in tables_result]
            
            # For each table, get column information
            for table in tables:
                if "sqlite" in database_url:
                    # SQLite approach
                    columns_query = text(f"PRAGMA table_info({table})")
                    columns_result = conn.execute(columns_query)
                    columns = [{"name": row[1], "type": row[2], "nullable": not row[3], "primary_key": bool(row[5])} 
                              for row in columns_result]
                else:
                    # PostgreSQL/MySQL approach
                    columns_query = text(f"""
                        SELECT column_name, data_type, is_nullable, 
                               CASE WHEN column_name IN (
                                   SELECT column_name FROM information_schema.key_column_usage
                                   WHERE table_name = '{table}' AND constraint_name LIKE '%pkey%'
                               ) THEN TRUE ELSE FALSE END as is_primary
                        FROM information_schema.columns
                        WHERE table_name = '{table}'
                        ORDER BY ordinal_position
                    """)
                    columns_result = conn.execute(columns_query)
                    columns = [{"name": row[0], "type": row[1], 
                               "nullable": row[2] == "YES", "primary_key": row[3]} 
                              for row in columns_result]
                
                schema_info[table] = columns
                
        return jsonify({"schema": schema_info})
    except SQLAlchemyError as e:
        print(f"Error in get_schema: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({"error": str(e)}), 500


@app.route('/api/dim_date', methods=['GET'])
def get_dim_date():
    start_time = time.time()
    try:
        results = DimDate.query.all()
        record_count = len(results)

        formatted_results = [{"date": row.date, "datetime": row.datetime.isoformat() if row.datetime else None} for row in results]
        
        execution_time = time.time() - start_time
        log_request("/api/dim_date", record_count, execution_time)

        return jsonify({"data": formatted_results, "metadata": {"record_count": record_count, "execution_time_seconds": round(execution_time, 4)}})

    except SQLAlchemyError as e:
        execution_time = time.time() - start_time
        logging.error(f"ERROR: /api/dim_date | Exception: {e} | Execution Time: {execution_time:.4f} seconds")
        return jsonify({"error": str(e), "metadata": {"execution_time_seconds": execution_time}}), 500

# =============================
# 2️⃣ GET DIM EXCHANGE
# =============================
@app.route('/api/dim_exchange', methods=['GET'])
def get_dim_exchange():
    start_time = time.time()
    try:
        results = DimExchange.query.all()
        record_count = len(results)

        formatted_results = [{"exchange_name": row.name, "symbol": row.symbol, "timezone": row.timezone} for row in results]

        execution_time = time.time() - start_time
        log_request("/api/dim_exchange", record_count, execution_time)

        return jsonify({"data": formatted_results, "metadata": {"record_count": record_count, "execution_time_seconds": round(execution_time, 4)}})

    except SQLAlchemyError as e:
        execution_time = time.time() - start_time
        logging.error(f"ERROR: /api/dim_exchange | Exception: {e} | Execution Time: {execution_time:.4f} seconds")
        return jsonify({"error": str(e), "metadata": {"execution_time_seconds": execution_time}}), 500

# =============================
# 3️⃣ GET DIM COMMODITY
# =============================
@app.route('/api/dim_commodity', methods=['GET'])
def get_dim_commodity():
    start_time = time.time()
    try:
        days = request.args.get('days', '60')
        to_date = request.args.get('to', datetime.now().strftime('%Y-%m-%d'))
        from_date = request.args.get('from', None)
        country = request.args.get('country', 'US')
        ticker = request.args.get('ticker', None)

        # Convert date formats
        try:
            to_datetime = datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            to_datetime = datetime.now()

        if from_date is None:
            from_datetime = to_datetime - timedelta(days=int(days)) if days.lower() != 'all' else datetime(1900, 1, 1)
        else:
            from_datetime = datetime.strptime(from_date, '%Y-%m-%d')

        # Query commodities
        query = DimCommodity.query.filter(DimCommodity.exchange == country)
        if ticker:
            query = query.filter(DimCommodity.symbol == ticker)

        results = query.all()
        record_count = len(results)

        formatted_results = [{"symbol": row.symbol, "name": row.name, "currency": row.currency, "exchange": row.exchange} for row in results]

        execution_time = time.time() - start_time
        log_request("/api/dim_commodity", record_count, execution_time)

        return jsonify({"data": formatted_results, "metadata": {"record_count": record_count, "execution_time_seconds": round(execution_time, 4)}})

    except SQLAlchemyError as e:
        execution_time = time.time() - start_time
        logging.error(f"ERROR: /api/dim_commodity | Exception: {e} | Execution Time: {execution_time:.4f} seconds")
        return jsonify({"error": str(e), "metadata": {"execution_time_seconds": execution_time}}), 500

# =============================
# 4️⃣ GET DIM COMPANY
# =============================
@app.route('/api/dim_company', methods=['GET'])
def get_dim_company():
    start_time = time.time()
    try:
        ticker = request.args.get('ticker')

        if not ticker:
            return jsonify({"error": "Ticker symbol is required"}), 400

        results = DimCompany.query.filter(DimCompany.symbol == ticker).all()
        record_count = len(results)

        formatted_results = [{"symbol": row.symbol, "company_name": row.company_name, "sector": row.sector, "industry": row.industry} for row in results]

        execution_time = time.time() - start_time
        log_request("/api/dim_company", record_count, execution_time)

        return jsonify({"data": formatted_results, "metadata": {"record_count": record_count, "execution_time_seconds": round(execution_time, 4)}})

    except SQLAlchemyError as e:
        execution_time = time.time() - start_time
        logging.error(f"ERROR: /api/dim_company | Exception: {e} | Execution Time: {execution_time:.4f} seconds")
        return jsonify({"error": str(e), "metadata": {"execution_time_seconds": execution_time}}), 500


# Route to get market data
@app.route('/api/market')
def get_market_data():
    start_time = time.time()
    try:
        days = request.args.get('days', '60')
        to_date = request.args.get('to', datetime.now().strftime('%Y-%m-%d'))
        from_date = request.args.get('from', None)
        country = request.args.get('country', 'US')

        try:
            to_datetime = datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            to_datetime = datetime.now()

        if from_date is None:
            if days.lower() == 'all':
                from_datetime = datetime(1900, 1, 1)
            else:
                try:
                    from_datetime = to_datetime - timedelta(days=int(days))
                except ValueError:
                    from_datetime = to_datetime - timedelta(days=60)
        else:
            try:
                from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
            except ValueError:
                from_datetime = to_datetime - timedelta(days=60)

        query = db.session.query(
            FactMarketMetrics, DimDate, DimCompany
        ).join(
            DimDate, FactMarketMetrics.fk_date_id == DimDate.sk_date_id
        ).join(
            DimCompany, FactMarketMetrics.fk_company_id == DimCompany.sk_company_id
        ).filter(
            DimCompany.country == country,
            DimDate.datetime.between(from_datetime, to_datetime)
        ).order_by(
            DimCompany.symbol, DimDate.datetime
        )

        results = query.all()

        formatted_results = [
            {
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
            }
            for metric, date, company in results
        ]

        execution_time = time.time() - start_time

        return jsonify({
            'data': formatted_results,
            'metadata': {
                'record_count': len(formatted_results),
                'execution_time_seconds': execution_time
            }
        })
    except SQLAlchemyError as e:
        execution_time = time.time() - start_time
        print(f"Error in get_market_data: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return jsonify({
            "error": str(e),
            'metadata': {'execution_time_seconds': execution_time}
        }), 500

# Route to get stock data 

@app.route('/api/ml-model', methods=['GET'])
def get_ml_model_data():
    start_time = time.time()  # Start execution timer

    try:
        # ✅ Get Query Parameters
        days = request.args.get('days', '60')  # Default: 60 days
        to_date = request.args.get('to', datetime.now().strftime('%Y-%m-%d'))
        from_date = request.args.get('from', None)
        country = request.args.get('country', 'US')
        limit = request.args.get('limit', 100)  # Default: 100 records
        offset = request.args.get('offset', 0)  # Default: start from 0

        # ✅ Convert 'to' Date or Set Default (today)
        try:
            to_datetime = datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            to_datetime = datetime.now()

        # ✅ Determine 'from' Date Based on 'days' or Set Default
        if from_date is None:
            if days.lower() == 'all':
                oldest_record = DimDate.query.order_by(DimDate.datetime.asc()).first()
                from_datetime = oldest_record.datetime if oldest_record else datetime(1900, 1, 1)
            else:
                try:
                    from_datetime = to_datetime - timedelta(days=int(days))
                except ValueError:
                    from_datetime = to_datetime - timedelta(days=60)
        else:
            try:
                from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
            except ValueError:
                from_datetime = to_datetime - timedelta(days=60)

        # ✅ Optimize Query Performance
        query = db.session.query(
            FactMarketMetrics, DimDate, DimCompany
        ).join(
            DimDate, FactMarketMetrics.fk_date_id == DimDate.sk_date_id
        ).join(
            DimCompany, FactMarketMetrics.fk_company_id == DimCompany.sk_company_id
        ).filter(
            DimCompany.country == country,
            DimDate.datetime.between(from_datetime, to_datetime)
        ).order_by(
            DimCompany.symbol, DimDate.datetime
        ).limit(limit).offset(offset)  # ✅ Implement Pagination

        # ✅ Fetch Query Results
        results = query.all()
        record_count = len(results)  # Number of records retrieved

        # ✅ Handle No Data Found
        if record_count == 0:
            execution_time = time.time() - start_time
            logging.warning(f"API: /api/ml-model | Country: {country} | No records found | Execution Time: {execution_time:.4f} seconds")
            return jsonify({
                "message": "No data found for the given parameters",
                "metadata": {"record_count": 0, "execution_time_seconds": round(execution_time, 4)}
            }), 404

        # ✅ Format Response Data
        formatted_results = [
            {
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
            }
            for metric, date, company in results
        ]

        execution_time = time.time() - start_time  # ✅ Calculate Execution Time

        # ✅ Log API request details
        logging.info(f"API: /api/ml-model | Country: {country} | Records: {record_count} | Execution Time: {execution_time:.4f} seconds")

        return jsonify({
            'from': from_datetime.strftime('%Y-%m-%d'),
            'to': to_datetime.strftime('%Y-%m-%d'),
            'country': country,
            'data': formatted_results,
            'metadata': {
                'record_count': record_count,
                'execution_time_seconds': round(execution_time, 4),
                'limit': limit,
                'offset': offset
            }
        })

    except SQLAlchemyError as e:
        execution_time = time.time() - start_time
        logging.error(f"ERROR: /api/ml-model | Country: {country} | Exception: {e} | Execution Time: {execution_time:.4f} seconds")
        print(traceback.format_exc(), file=sys.stderr)

        return jsonify({
            "error": str(e),
            'metadata': {'execution_time_seconds': execution_time}
        }), 500


@app.route('/api/ml-model/stock', methods=['GET'])
def get_single_stock_ml_data():
    start_time = time.time()  # Start tracking execution time

    try:
        # Get query parameters
        ticker = request.args.get('ticker')  # Required
        days = request.args.get('days', '60')  # Default 60 days
        to_date = request.args.get('to', datetime.now().strftime('%Y-%m-%d'))
        from_date = request.args.get('from', None)

        # Ensure ticker is provided
        if not ticker:
            return jsonify({"error": "Ticker symbol is required"}), 400

        # Convert 'to' date or set default (today)
        try:
            to_datetime = datetime.strptime(to_date, '%Y-%m-%d')
        except ValueError:
            to_datetime = datetime.now()

        # Determine 'from' date based on 'days' or set default
        if from_date is None:
            if days.lower() == 'all':
                oldest_record = DimDate.query.order_by(DimDate.datetime.asc()).first()
                from_datetime = oldest_record.datetime if oldest_record else datetime(1900, 1, 1)
            else:
                try:
                    from_datetime = to_datetime - timedelta(days=int(days))
                except ValueError:
                    from_datetime = to_datetime - timedelta(days=60)
        else:
            try:
                from_datetime = datetime.strptime(from_date, '%Y-%m-%d')
            except ValueError:
                from_datetime = to_datetime - timedelta(days=60)

        # Query market data for the specified stock
        query = db.session.query(
            FactMarketMetrics, DimDate, DimCompany
        ).join(
            DimDate, FactMarketMetrics.fk_date_id == DimDate.sk_date_id
        ).join(
            DimCompany, FactMarketMetrics.fk_company_id == DimCompany.sk_company_id
        ).filter(
            DimCompany.symbol == ticker,
            DimDate.datetime.between(from_datetime, to_datetime)
        ).order_by(
            DimDate.datetime
        )

        # Fetch query results
        results = query.all()
        record_count = len(results)  # Get number of records retrieved

        # Format response data
        formatted_results = [
            {
                'symbol': company.symbol,
                'company_name': company.company_name,
                'sector': company.sector,
                'industry': company.industry,
                'country': company.country,
                'date': date.date,
                'datetime': date.datetime.isoformat() if date.datetime else None,
                'current_price': float(metric.current_price) if metric.current_price else None,
                'change': float(metric.change) if metric.change else None,
                'change_percentage': float(metric.change_percentage) if metric.change_percentage else None,
                'volume': metric.volume,
                'day_low': float(metric.day_low) if metric.day_low else None,
                'day_high': float(metric.day_high) if metric.day_high else None,
                'market_cap': float(metric.market_cap) if metric.market_cap else None
            }
            for metric, date, company in results
        ]

        execution_time = time.time() - start_time  # Calculate execution time

        # ✅ Log number of records retrieved and retrieval time
        logging.info(f"Ticker: {ticker} | Records Retrieved: {record_count} | Execution Time: {execution_time:.4f} seconds")

        return jsonify({
            'ticker': ticker,
            'from': from_datetime.strftime('%Y-%m-%d'),
            'to': to_datetime.strftime('%Y-%m-%d'),
            'data': formatted_results,
            'metadata': {
                'record_count': record_count,
                'execution_time_seconds': round(execution_time, 4)
            }
        })

    except SQLAlchemyError as e:
        execution_time = time.time() - start_time
        logging.error(f"Error fetching data for {ticker}: {e} | Execution Time: {execution_time:.4f} seconds")
        print(traceback.format_exc(), file=sys.stderr)

        return jsonify({
            "error": str(e),
            'metadata': {'execution_time_seconds': execution_time}
        }), 500

# Run the app
if _name_ == '_main_':
    print("Running tests before starting server...", file=sys.stderr)
    
    exit_code = pytest.main(["-v", "test_stock.py"]) 
    if exit_code != 0:
        print("❌ Tests failed. Server will not start.", file=sys.stderr)
        exit(exit_code)
    
    print("✅ Tests passed. Starting Flask server...", file=sys.stderr)
    app.run(host='0.0.0.0', port=5000, debug=False)

