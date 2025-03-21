# **Stock Market API Documentation**

## **Introduction**
This API provides market data for ML models, including stock, index, bond, commodity, and exchange information. The API supports filtering by country, date range, and ticker symbol. Logging is enabled for monitoring execution time and record counts.

---

## **Base URL**
```
http://localhost:5000
```
If running in Docker, replace `localhost` with the container name, e.g., `flask_app`.

---

## **Endpoints**

### **1. GET `/api/dim_date`**
#### **Description:**
Retrieves all available dates from the `dim_date` table.
#### **Request:**
```sh
curl -X GET "http://localhost:5000/api/dim_date" -H "Content-Type: application/json"
```
#### **Response:**
```json
{
  "data": [{"date": "2025-03-10", "datetime": "2025-03-10T00:00:00"}],
  "metadata": {"record_count": 500, "execution_time_seconds": 0.35}
}
```
---

### **2. GET `/api/dim_exchange`**
#### **Description:**
Retrieves exchange information.
#### **Request:**
```sh
curl -X GET "http://localhost:5000/api/dim_exchange" -H "Content-Type: application/json"
```
#### **Response:**
```json
{
  "data": [{"exchange_name": "NASDAQ", "symbol": "NSDQ", "timezone": "UTC-5"}],
  "metadata": {"record_count": 5, "execution_time_seconds": 0.02}
}
```
---

### **3. GET `/api/dim_commodity`**
#### **Description:**
Fetches commodity data with filters.
#### **Request:**
```sh
curl -X GET "http://localhost:5000/api/dim_commodity?days=60&to=2025-03-14&from=2025-01-13&country=US&ticker=GOLD" -H "Content-Type: application/json"
```
#### **Response:**
```json
{
  "data": [{"symbol": "GOLD", "name": "Gold Futures", "currency": "USD", "exchange": "NYMEX"}],
  "metadata": {"record_count": 10, "execution_time_seconds": 0.12}
}
```
---

### **4. GET `/api/dim_index`**
#### **Request:**
```sh
curl -X GET "http://localhost:5000/api/dim_index?days=60&to=2025-03-14&from=2025-01-13&country=US&ticker=S&P500" -H "Content-Type: application/json"
```
#### **Response:**
```json
{
  "data": [{"symbol": "S&P500", "name": "S&P 500 Index", "currency": "USD", "exchange": "NYSE"}],
  "metadata": {"record_count": 5, "execution_time_seconds": 0.09}
}
```
---

### **5. GET `/api/ml-model`**
#### **Description:**
Retrieves market metrics for ML model training.
#### **Request:**
```sh
curl -X GET "http://localhost:5000/api/ml-model?days=60&to=2025-03-14&from=2025-01-13&country=US" -H "Content-Type: application/json"
```
#### **Response:**
```json
{
  "from": "2025-01-13",
  "to": "2025-03-14",
  "country": "US",
  "data": [{
    "symbol": "AAPL",
    "company_name": "Apple Inc.",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "date": "2025-03-10",
    "datetime": "2025-03-10T00:00:00",
    "current_price": 345.12,
    "change": 2.50,
    "change_percentage": 1.2,
    "volume": 450000,
    "market_cap": 2500000000
  }],
  "metadata": {"record_count": 100, "execution_time_seconds": 0.35}
}
```
---

## **Logging**
All API requests are logged to `api.log`. Logs include:
- API endpoint
- Execution time
- Number of records retrieved
- Errors (if any)

To view logs inside Docker:
```sh
docker exec -it <container_id> cat /app/logs/api.log
```
To view real-time logs:
```sh
docker logs -f <container_id>
```

---

## **Deployment**
### **Running in Docker**
1. **Build and Run the Container**
```sh
docker-compose up --build
```
2. **Access the API** at `http://localhost:5000`.

### **Check Running Containers**
```sh
docker ps
```

### **Stop and Remove Containers**
```sh
docker-compose down
```

---
## **Future Enhancements**
✅ Implement **Redis caching** for faster responses.
✅ Add **authentication** for secure API access.
✅ Support **WebSockets for real-time updates**.

---
## **Contributors**
- **Developer:** Harsh 🚀

For any issues, contact: `support@stockapi.com`

