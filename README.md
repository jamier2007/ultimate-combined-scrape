# Unified Vehicle Data API

A high-performance API that combines multiple vehicle data sources for comprehensive vehicle information lookup by VRM (Vehicle Registration Mark).

## 🚀 Features

- **Multi-Source Data**: Combines data from e3technical.haynespro.com and bookmygarage.com
- **Async Processing**: Concurrent scraping from multiple sources for maximum speed
- **Intelligent Caching**: TTL-based caching system with configurable expiration
- **Data Deduplication**: Smart merging algorithm avoids duplicate data
- **CORS Enabled**: Accepts requests from all origins
- **FastAPI**: Modern async API with automatic documentation

## 🏗️ Architecture

The API includes three implementations:

1. **Unified API** (`unified_vehicle_api.py`) - ⭐ **RECOMMENDED** - Port 8000
2. **Flask API** (`app.py`) - Original simple API - Port 7654  
3. **FastAPI Service** (`app/vehicle_service.py`) - BookMyGarage only - Port 5001

## 🛠️ Quick Start

### Prerequisites

- Python 3.7+ installed on your system

### Setup Steps

1. Clone this repository:
   ```bash
   git clone https://github.com/jamier2007/e3-reg-lookup.git
   cd e3-reg-lookup
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the **Unified API** (recommended):
   ```bash
   python3 unified_vehicle_api.py
   ```
   
   The API will be accessible at http://localhost:8000

## 📡 API Usage

### Unified API (Port 8000) - RECOMMENDED

#### Get Vehicle Data by VRM
```
GET http://localhost:8000/{vrm}
```

Example:
```bash
curl "http://localhost:8000/p336pke"
```

#### Optional Parameters
- `username`: Custom username for e3technical.haynespro.com
- `password`: Custom password for e3technical.haynespro.com
- `force_refresh`: Set to 'true' to bypass cache

#### Additional Endpoints
- `GET /` - API information and cache stats
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /cache/stats` - Cache statistics
- `DELETE /cache/clear` - Clear cache

### Legacy APIs

#### Flask API (Port 7654)
```bash
python3 app.py
# Available at http://localhost:7654
```

#### FastAPI Service (Port 5001)
```bash
cd app && uvicorn vehicle_service:app --port 5001
# Available at http://localhost:5001
```

## 📊 Response Format

### Unified API Response
```json
{
  "vrm": "P336PKE",
  "data": {
    "Vehicle Registration Mark (Current)": "P336PKE",
    "Combined VIN": "KZJ950019845",
    "Combined Make": "TOYOTA",
    "Combined Model": "LAND CRUISER IMPORT",
    "Colour": "BLUE",
    "Engine Capacity": "2980",
    "Fuel Type": "DIESEL",
    ...
  },
  "sources": ["e3technical"],
  "cached": false,
  "total_fields": 81
}
```

## 🐳 Docker Deployment

### Using Docker Compose
```bash
docker-compose up
```

### Using Docker directly
```bash
docker build -t vehicle-api:latest .
docker run -p 5001:5001 --name vehicle-api vehicle-api
```

### Using the run script
```bash
./run_local.sh
```

## ⚡ Performance Features

- **Concurrent Scraping**: Multiple sources scraped simultaneously
- **Smart Caching**: 1-hour TTL cache with 5000 entry capacity
- **Data Prioritization**: E3Technical data takes priority over other sources
- **Async Architecture**: Non-blocking I/O for maximum throughput
- **Error Handling**: Graceful fallbacks when sources are unavailable

## 🔧 Configuration

Environment variables for the unified API:

- `CACHE_TTL`: Cache time-to-live in seconds (default: 3600)
- `CACHE_MAXSIZE`: Maximum cache entries (default: 5000)
- `LOG_LEVEL`: Logging level (default: INFO)

## 🌐 Data Sources

1. **E3Technical HaynesPro** (Primary)
   - Comprehensive UK vehicle database
   - 80+ detailed fields including technical specifications
   - Requires authentication

2. **BookMyGarage** (Secondary)
   - Alternative vehicle data source
   - Supplementary information
   - No authentication required

## 📈 API Comparison

| Feature | Unified API | Flask API | FastAPI Service |
|---------|-------------|-----------|-----------------|
| Port | 8000 | 7654 | 5001 |
| Data Sources | 2 (E3Tech + BMG) | 1 (E3Tech) | 1 (BMG) |
| Performance | ⚡ Async | 🔄 Sync | ⚡ Async |
| Caching | ✅ TTL Cache | ✅ Simple Cache | ✅ TTL Cache |
| Documentation | ✅ Auto-generated | ❌ None | ✅ Auto-generated |
| Web Interface | ❌ API Only | ❌ API Only | ✅ Included |
| Docker Ready | ✅ Yes | ✅ Yes | ✅ Yes |

## 🚧 Development

### Running in development mode
```bash
# Unified API with auto-reload
uvicorn unified_vehicle_api:app --reload --port 8000

# Flask API
python3 app.py

# FastAPI Service
cd app && uvicorn vehicle_service:app --reload --port 5001
```

### Testing
```bash
# Test all APIs with the same VRM
curl "http://localhost:8000/p336pke"  # Unified (recommended)
curl "http://localhost:7654/p336pke"  # Flask
curl "http://localhost:5001/p336pke"  # FastAPI Service
```

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.
