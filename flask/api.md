
# **Stock Market API Documentation**

## **Introduction**
This API provides market data for ML models, including stock, index, bond, commodity, and exchange information. The API supports filtering by country, date range, and ticker symbol. Logging is enabled for monitoring execution time and record counts.

---

## **Base URL**
```
http://localhost:5001
```
If running in Docker, replace `localhost` with the container name, e.g., `flask_app`.

---

## **Endpoints**

### **1. GET `/api/dim_date`**
Retrieves all available dates from the `dim_date` table.
```
curl -X GET "http://localhost:5001/api/dim_date" -H "Content-Type: application/json"
```

### **2. GET `/api/dim_exchange`**
Retrieves exchange information.
```
curl -X GET "http://localhost:5001/api/dim_exchange" -H "Content-Type: application/json"
```

### **3. GET `/api/dim_commodity`**
Fetches commodity data.
```
curl -X GET "http://localhost:5001/api/dim_commodity" -H "Content-Type: application/json"
```

### **4. GET `/api/dim_index`**
Fetches index data by filters.
```
curl -X GET "http://localhost:5001/api/dim_index?ticker=S&P500&country=US" -H "Content-Type: application/json"
```

### **5. GET `/api/ml-model`**
Retrieves market metrics for ML model training.
```
curl -X GET "http://localhost:5001/api/ml-model?days=60&country=US" -H "Content-Type: application/json"
```

### **6. GET `/api/dim_company`**
Fetches company data filtered by ticker.
```
curl -X GET "http://localhost:5001/api/dim_company?ticker=AAPL" -H "Content-Type: application/json"
```

### **7. GET `/api/dim_bond`**
Retrieves available bonds.
```
curl -X GET "http://localhost:5001/api/dim_bond" -H "Content-Type: application/json"
```

### **8. GET `/api/dim_stock`**
Fetches stock and metrics info.
```
curl -X GET "http://localhost:5001/api/dim_stock?symbol=AAPL" -H "Content-Type: application/json"
```

### **9. GET `/api/ml-model/stock`**
Retrieves market metrics for a specific stock.
```
curl -X GET "http://localhost:5001/api/ml-model/stock?ticker=AAPL" -H "Content-Type: application/json"
```

### **10. GET `/api/index_data`**
Fetches index data with filters.
```
curl -X GET "http://localhost:5001/api/index_data?ticker=S&P500&country=US" -H "Content-Type: application/json"
```

### **11. GET `/api/market`**
Returns full market data for all companies.
```
curl -X GET "http://localhost:5001/api/market?country=US" -H "Content-Type: application/json"
```

---

## **Logging**
Logs include:
- API endpoint
- Execution time
- Record count
- Errors (if any)

To view logs inside Docker:
```
docker exec -it <container_id> cat /app/logs/api.log
```
To view real-time logs:
```
docker logs -f <container_id>
```

---

## **Deployment**
Run with Docker:
```
docker-compose up --build
```
Stop containers:
```
docker-compose down
```

---

## **Future Enhancements**
- ✅ Redis caching
- ✅ Authentication
- ✅ WebSocket support

---

## **Contributors**
Alfiya, Anshika, Rajdeep, Gursheen, Kritika

Contact: `support@stockapi.com`
