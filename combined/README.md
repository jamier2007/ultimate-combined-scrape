# Combined Vehicle Data API

🚀 **High-performance FastAPI combining multiple vehicle data sources**

A modern async API that intelligently merges vehicle data from multiple sources, providing comprehensive vehicle information with smart caching and data deduplication.

## ✨ Key Features

- 🔥 **Multi-Source Data**: Combines E3Technical HaynesPro + BookMyGarage
- ⚡ **Async Processing**: Concurrent scraping for maximum speed
- 🧠 **Smart Merging**: Intelligent data deduplication with source prioritization
- 💾 **TTL Caching**: 1-hour cache with 5000 entry capacity
- 🌐 **CORS Enabled**: Works from any origin
- 📚 **Auto Documentation**: Built-in Swagger UI

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the API
```bash
python unified_vehicle_api.py
```

**🎯 API Available at: http://localhost:8000**

## 📡 API Usage

### Get Vehicle Data
```bash
# Basic lookup
curl "http://localhost:8000/p336pke"

# With custom credentials
curl "http://localhost:8000/p336pke?username=YOUR_USER&password=YOUR_PASS"

# Force refresh cache
curl "http://localhost:8000/p336pke?force_refresh=true"
```

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📊 Example Response

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
    "Body Style": "ESTATE",
    "Year Of Manufacture": "1996"
  },
  "sources": ["e3technical"],
  "cached": false,
  "total_fields": 81
}
```

## 🔧 Additional Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info and cache stats |
| `/{vrm}` | GET | Get vehicle data by VRM |
| `/docs` | GET | Interactive API documentation |
| `/cache/stats` | GET | Cache statistics |
| `/cache/clear` | DELETE | Clear entire cache |

## ⚙️ Configuration

### Environment Variables
```bash
export CACHE_TTL=3600        # Cache TTL in seconds (default: 1 hour)
export CACHE_MAXSIZE=5000    # Max cache entries (default: 5000)
export LOG_LEVEL=INFO        # Logging level
```

### E3Technical Credentials
- **Default Username**: `NT445A`
- **Default Password**: `7g2ba29mz4`
- Can be overridden via query parameters

## 🌐 Data Sources

### 1. E3Technical HaynesPro (Primary)
- ✅ **80+ fields** of comprehensive vehicle data
- ✅ Technical specifications, history, ownership
- ✅ High data quality and accuracy
- ⚠️ Requires authentication

### 2. BookMyGarage (Secondary)
- ✅ Alternative vehicle information
- ✅ Supplementary data points
- ✅ No authentication required
- ℹ️ Used to fill gaps in E3Technical data

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────────┐
│   Client API    │───▶│   FastAPI Router     │
│   Request       │    │   (unified_vehicle   │
└─────────────────┘    │    _api.py)          │
                       └──────────┬───────────┘
                                  │
                       ┌──────────▼───────────┐
                       │   Cache Check        │
                       │   (TTLCache)         │
                       └──────────┬───────────┘
                                  │
                       ┌──────────▼───────────┐
                       │   Concurrent         │
                       │   Scraping           │
                       └──────┬─────────┬─────┘
                              │         │
                    ┌─────────▼─┐   ┌───▼──────┐
                    │E3Technical│   │BookMy    │
                    │Scraper    │   │Garage    │
                    │(Auth)     │   │Scraper   │
                    └─────────┬─┘   └───┬──────┘
                              │         │
                       ┌──────▼─────────▼─────┐
                       │   Data Merger        │
                       │   (Smart Dedup)      │
                       └──────────┬───────────┘
                                  │
                       ┌──────────▼───────────┐
                       │   JSON Response      │
                       │   + Cache Store      │
                       └──────────────────────┘
```

## 🚀 Performance

- **Speed**: Async concurrent scraping
- **Efficiency**: Smart caching prevents redundant requests
- **Reliability**: Graceful fallbacks when sources fail
- **Scalability**: Non-blocking I/O architecture

## 🔒 Error Handling

- **404**: VRM not found in any source
- **422**: Invalid VRM format
- **500**: Scraping or server errors
- **Timeouts**: 15-second timeout per source

## 🛠️ Development

### Run with auto-reload
```bash
uvicorn unified_vehicle_api:app --reload --port 8000
```

### Debug mode
```bash
python unified_vehicle_api.py
```

## 📈 Monitoring

### Cache Statistics
```bash
curl "http://localhost:8000/cache/stats"
```

### Clear Cache
```bash
curl -X DELETE "http://localhost:8000/cache/clear"
```

## 🐳 Docker Support

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY unified_vehicle_api.py .
EXPOSE 8000
CMD ["python", "unified_vehicle_api.py"]
```

Build and run:
```bash
docker build -t combined-vehicle-api .
docker run -p 8000:8000 combined-vehicle-api
```

## 📄 License

MIT License - Feel free to use and modify.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**🎯 Ready to use! Just run `python unified_vehicle_api.py` and start querying vehicle data at http://localhost:8000** 