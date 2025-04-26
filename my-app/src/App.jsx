import React, { useState, useEffect } from "react";
import "./App.css";

const App = () => {
  const [query, setQuery] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [selectedApi, setSelectedApi] = useState(null);
  const [loading, setLoading] = useState(false);
  const [baseUrl, setBaseUrl] = useState("http://localhost:5001");

  const apiEndpoints = [
    {
      name: "Retrieve Stock Market Data",
      url: "/api/market",
      description: "This API returns comprehensive stock and index data for a selected country. You can specify date ranges and duration (e.g., last 60 days or all). The data helps in trend analysis and machine learning predictions. Retrieval metrics like number of records and time taken are logged."
    },
    {
      name: "Retrieve Single Stock Data",
      url: "/api/ml-model/stock?ticker=AAPL",
      description: "Use this endpoint to fetch historical market data for a specific stock ticker. Parameters include the ticker symbol, date range, and duration. It enables targeted stock analysis and supports ML model training. Record count and response time are logged."
    },
    {
      name: "Retrieve Date Dimension Data",
      url: "/api/dim_date",
      description: "Returns structured date-related metadata to support time-based analysis in data warehousing. Ideal for calendar-based aggregations and filtering. Includes details like fiscal periods and holidays. Logs include record count and retrieval time."
    },
    {
      name: "Retrieve Exchange Dimension Data",
      url: "/api/dim_exchange",
      description: "Fetches data about global stock exchanges. Useful for categorizing and filtering stocks based on their trading platforms. This data supports enriched stock analytics and segmentation. Metrics on records and performance are logged."
    },
    {
      name: "Retrieve Commodity Data",
      url: "/api/dim_commodity",
      description: "Returns commodity market data based on parameters like date range, country, and ticker. Supports comparative analysis of commodity trends over time. Useful for commodity-based research and modeling. Logs include record count and retrieval speed."
    },
    {
      name: "Retrieve Index Data",
      url: "/api/ml-model?country=US&days=60",
      description: "This endpoint provides stock market index data for selected countries and date ranges. Parameters include index ticker, start and end dates. Supports index-based market trend analysis. All queries are logged for audit and optimization."
    },
    {
      name: "Retrieve Stock Dimension Data",
      url: "/api/dim_stock",
      description: "Returns metadata for individual stocks, enabling performance comparisons across exchanges. Includes ticker-based filtering, dates, and country parameters. Useful for organizing stock datasets. Record counts and time are logged."
    },
    {
      name: "Retrieve Company Data",
      url: "/api/dim_company?ticker=AAPL",
      description: "Fetch detailed company information linked to specific stock tickers. Ideal for understanding company fundamentals and integrating with financial datasets. Helps provide context for stock performance. Retrieval logs ensure traceability."
    },
    {
      name: "Retrieve Bond Data",
      url: "/api/dim_bond",
      description: "This endpoint provides access to bond market data. Supports bond trend analysis and fixed-income research. Complements other financial instruments in portfolio analytics. Logs track records fetched and response duration."
    },
  
    {
      name: "Database Tables",
      url: "/api/tables",
      description: "Lists all tables in the database. This endpoint is useful for quickly checking what data is available in the system."
    },
 
  ];

  useEffect(() => {
    // Set a default selected API when component mounts
    if (apiEndpoints.length > 0 && !selectedApi) {
      setSelectedApi(apiEndpoints[0]);
      setQuery(baseUrl + apiEndpoints[0].url);
    }
  }, []);

  const handleBaseUrlChange = (e) => {
    const newBaseUrl = e.target.value;
    setBaseUrl(newBaseUrl);
    if (selectedApi) {
      setQuery(newBaseUrl + selectedApi.url);
    }
  };

  const handleSearch = async () => {
    setError(null);
    setData(null);
    setLoading(true);

    try {
      const response = await fetch(query);
      if (!response.ok) throw new Error(`API Error: ${response.status} ${response.statusText}`);
      const result = await response.json();
      setData(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatData = (data) => {
    if (!data) return null;
    
    // Format the data based on the API endpoint structure
    if (data.data && Array.isArray(data.data) && data.data.length > 0) {
      // Get all possible columns from the data
      const firstItem = data.data[0];
      const columns = Object.keys(firstItem);
      
      return (
        <>
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-4 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">
                #
              </th>
              {columns.map(column => (
                <th key={column} className="px-6 py-4 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">
                  {column.replace(/_/g, ' ')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.data.slice(0, 15).map((item, index) => (
              <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="px-6 py-4 whitespace-nowrap text-base text-gray-900 font-medium">
                  {index + 1}
                </td>
                {columns.map(column => (
                  <td key={column} className="px-6 py-4 whitespace-nowrap text-base text-gray-500">
                    {typeof item[column] === 'object' 
                      ? <pre className="data-content">{JSON.stringify(item[column], null, 2)}</pre>
                      : item[column] === null ? 'null' : String(item[column])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </>
      );
    } else if (data.tables && Array.isArray(data.tables)) {
      return (
        <>
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-4 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">
                #
              </th>
              <th className="px-6 py-4 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">
                Table Name
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.tables.map((item, index) => (
              <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="px-6 py-4 whitespace-nowrap text-base text-gray-900 font-medium">
                  {index + 1}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-base text-gray-500">
                  {item}
                </td>
              </tr>
            ))}
          </tbody>
        </>
      );
    } else if (data.schema && typeof data.schema === 'object') {
      return (
        <>
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-4 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">
                Table Name
              </th>
              <th className="px-6 py-4 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">
                Columns
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {Object.entries(data.schema).map(([tableName, columns], index) => (
              <tr key={index} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                <td className="px-6 py-4 whitespace-nowrap text-base text-gray-900 font-medium">
                  {tableName}
                </td>
                <td className="px-6 py-4">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="px-4 py-3 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">Name</th>
                        <th className="px-4 py-3 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">Type</th>
                        <th className="px-4 py-3 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">Nullable</th>
                        <th className="px-4 py-3 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">Primary Key</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {columns.map((column, colIdx) => (
                        <tr key={colIdx}>
                          <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{column.name}</td>
                          <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{column.type}</td>
                          <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{column.nullable ? 'Yes' : 'No'}</td>
                          <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{column.primary_key ? 'Yes' : 'No'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </td>
              </tr>
            ))}
          </tbody>
        </>
      );
    } else if (data.endpoints && typeof data.endpoints === 'object') {
      // Handle the root endpoint response
      return (
        <>
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-4 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">
                Message
              </th>
              <th className="px-6 py-4 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">
                Value
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            <tr>
              <td className="px-6 py-4 whitespace-nowrap text-base text-gray-900 font-medium">
                Welcome Message
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-base text-gray-500">
                {data.message}
              </td>
            </tr>
            <tr className="bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-base text-gray-900 font-medium">
                Database Status
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-base text-gray-500">
                {data.database_status}
              </td>
            </tr>
            <tr>
              <td className="px-6 py-4 whitespace-nowrap text-base text-gray-900 font-medium">
                Available Endpoints
              </td>
              <td className="px-6 py-4">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-4 py-3 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">Endpoint</th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">Path</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {Object.entries(data.endpoints).map(([name, path], idx) => (
                      <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{name}</td>
                        <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">{path}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </td>
            </tr>
          </tbody>
        </>
      );
    } else {
      // Fallback for any other data format
      return (
        <>
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-4 text-left text-sm font-medium text-gray-500 uppercase tracking-wider">
                Data
              </th>
            </tr>
          </thead>
          <tbody className="bg-white">
            <tr>
              <td className="px-6 py-4">
                <pre className="data-content">{JSON.stringify(data, null, 2)}</pre>
              </td>
            </tr>
          </tbody>
        </>
      );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-100 to-purple-100 font-sans p-6">
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-blue-800 mb-3">Market Data Explorer</h1>
        <p className="text-lg text-gray-600">Access and visualize stock market data from various endpoints</p>
      </header>

      {/* Top Search Bar */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <div className="flex flex-col md:flex-row gap-6 items-start md:items-center">
          <div className="w-full md:w-1/4">
            <label className="block text-base font-medium text-gray-700 mb-2">Base URL</label>
            <input
              type="text"
              value={baseUrl}
              onChange={handleBaseUrlChange}
              className="w-full p-3 text-base border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="http://localhost:5001"
            />
          </div>
          <div className="w-full md:w-2/4">
            <label className="block text-base font-medium text-gray-700 mb-2">API Endpoint</label>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full p-3 text-base border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter API URL..."
            />
          </div>
          <div className="w-full md:w-1/4 self-end">
            <button 
              onClick={handleSearch}
              className="w-full p-3 text-base bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 mt-7 md:mt-0"
              disabled={loading}
            >
              {loading ? 'Loading...' : 'Fetch Data'}
            </button>
          </div>
        </div>
      </div>

      <div className="flex flex-col md:flex-row gap-8">
        {/* Sidebar (API Endpoints) */}
        <div className="w-full md:w-1/4 bg-white rounded-lg shadow-lg p-5">
          <h2 className="text-2xl font-semibold text-gray-800 mb-5">API Endpoints</h2>
          <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
            {apiEndpoints.map((api) => (
              <button
                key={api.url}
                onClick={() => {
                  setQuery(baseUrl + api.url);
                  setSelectedApi(api);
                }}
                className={`w-full p-3 rounded-md text-left text-base ${
                  selectedApi && selectedApi.url === api.url
                    ? "bg-blue-100 text-blue-700 border-l-4 border-blue-600"
                    : "hover:bg-gray-100 text-gray-700"
                }`}
              >
                {api.name}
              </button>
            ))}
          </div>
        </div>

        <div className="w-full md:w-3/4 flex flex-col gap-8">
          {/* Description Box */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-3">API Description</h2>
            <p className="text-base text-gray-600 leading-relaxed">
              {selectedApi ? selectedApi.description : "Select an API to see details"}
            </p>
          </div>

          {/* Data Table */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-5">Results</h2>
            
            {error && (
              <div className="bg-red-100 text-red-700 p-4 rounded-md mb-5 text-base">
                {error}
              </div>
            )}
            
            {loading && (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-3 border-b-3 border-blue-600"></div>
                <p className="mt-4 text-lg text-gray-600">Loading data...</p>
              </div>
            )}
            
            {data && !loading && (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 text-base">
                  {formatData(data)}
                </table>
                
                {data.metadata && (
                  <div className="mt-6 p-4 bg-gray-50 rounded-md">
                    <h3 className="text-lg font-medium text-gray-700 mb-2">Metadata</h3>
                    <div className="flex flex-wrap gap-6 mt-2">
                      {Object.entries(data.metadata).map(([key, value]) => (
                        <div key={key} className="flex items-center">
                          <span className="text-base font-medium text-gray-700 mr-2">{key.replace(/_/g, ' ')}:</span>
                          <span className="text-base text-gray-600">{
                            typeof value === 'number' && !Number.isInteger(value) 
                              ? value.toFixed(4) 
                              : String(value)
                          }</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {!data && !loading && !error && (
              <div className="text-center py-16 text-gray-500 text-lg">
                Select an API endpoint and click "Fetch Data" to see results
              </div>
            )}
          </div>
        </div>
      </div>
      
      <footer className="mt-8 text-center text-gray-500 py-4">
        <p>Market Data Explorer © 2025 - Connecting to {baseUrl}</p>
      </footer>
    </div>
  );
};

export default App;