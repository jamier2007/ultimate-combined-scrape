#!/usr/bin/env python3
"""
Unified Vehicle Data API - FastAPI implementation
Combines data from multiple sources for comprehensive vehicle information.
Optimized for speed with async processing and intelligent caching.
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
import json

import httpx
import mechanicalsoup
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, PlainTextResponse, HTMLResponse
from cachetools import TTLCache

# ==================== Configuration ====================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("unified-vehicle-api")

# Cache configuration
CACHE_TTL = 3600  # 1 hour
CACHE_MAXSIZE = 5000
cache = TTLCache(maxsize=CACHE_MAXSIZE, ttl=CACHE_TTL)

# E3Technical credentials
DEFAULT_USERNAME = "NT445A"
DEFAULT_PASSWORD = "7g2ba29mz4"

# HTTP client for async requests
http_client: Optional[httpx.AsyncClient] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global http_client
    http_client = httpx.AsyncClient(
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        timeout=10.0,  # Reduced for speed
        follow_redirects=True,
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)  # Connection pooling
    )
    yield
    # Shutdown
    if http_client:
        await http_client.aclose()

# ==================== FastAPI Setup ====================
app = FastAPI(
    title="Unified Vehicle Data API",
    version="3.0.0",
    description="High-performance API combining multiple vehicle data sources",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Helper Functions ====================
def clean_vrm(vrm: str) -> str:
    """Clean and normalize VRM"""
    return vrm.upper().strip().replace(" ", "")

def clean_field_name(field_name: str) -> str:
    """Remove 'Combined' prefix from field names"""
    if field_name.startswith("Combined "):
        return field_name[9:]
    elif field_name.startswith("Combined"):
        return field_name[8:]
    return field_name

def process_all_vehicle_data(data_sources: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Process and return all data from both sources without merging duplicates"""
    processed_data = {}
    
    for source_name, source_data in data_sources.items():
        if source_data:
            # Clean field names for each source
            cleaned_data = {}
            for key, value in source_data.items():
                if value and str(value).strip():
                    cleaned_key = clean_field_name(key)
                    cleaned_data[cleaned_key] = value
            
            if cleaned_data:
                processed_data[source_name] = cleaned_data
    
    return processed_data

# ==================== E3Technical Scraper ====================
class AsyncE3TechnicalScraper:
    """Async version of E3Technical scraper for better performance"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.url = "https://e3technical.haynespro.com/"
        self.session_data = None
    
    async def get_vehicle_data(self, vrm: str) -> Dict[str, Any]:
        """Get vehicle data from E3Technical - optimized"""
        try:
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, self._sync_scrape, vrm)
            if data:
                print(f"[E3] Successfully scraped {len(data)} fields for {vrm}")
            else:
                print(f"[E3] No data found for {vrm}")
            return data
        except Exception as e:
            print(f"[E3] Scraping failed for {vrm}: {e}")
            return {}
    
    def _sync_scrape(self, vrm: str) -> Dict[str, Any]:
        """Synchronous scraping method"""
        try:
            browser = mechanicalsoup.StatefulBrowser(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                soup_config={'features': 'lxml'}
            )
            browser.session.timeout = 8  # Fast timeout for E3Technical
            
            # Login
            browser.open(self.url)
            try:
                browser.select_form('form[action="./Login.aspx"]')
            except:
                forms = browser.get_current_page().find_all('form')
                if forms:
                    browser.select_form(forms[0])
                else:
                    return {}
            
            browser["ctl00$MainContentPlaceHolder$Username"] = self.username
            browser["ctl00$MainContentPlaceHolder$Password"] = self.password
            
            response = browser.submit_selected()
            if "Welcome to e3 technical" not in response.text:
                return {}
            
            # Search VRM
            browser.select_form('form#aspnetForm')
            browser["ctl00$SearchContentPlaceHolder$Search$SearchKey"] = vrm
            browser.form["__EVENTTARGET"] = "ctl00$SearchContentPlaceHolder$Search$SearchVehicle"
            browser.form["__EVENTARGUMENT"] = ""
            
            response = browser.submit_selected()
            if "Vehicle Registration Mark (Current)" not in response.text:
                return {}
            
            # Extract data
            page = browser.get_current_page()
            container = page.find(id="ctl00_MainContentPlaceHolder_VehicleDataContainer")
            
            if not container:
                return {}
            
            data = {}
            rows = container.find_all("tr")
            for row in rows:
                cells = row.find_all("td")
                if len(cells) >= 2:
                    key = cells[0].get_text(separator=" ", strip=True)
                    value = cells[1].get_text(separator=" ", strip=True)
                    if key and value:
                        data[key] = value
            
            return data
            
        except Exception as e:
            logger.error(f"E3Technical sync scrape failed: {e}")
            return {}

# ==================== BookMyGarage Scraper ====================
async def scrape_bookmygarage(vrm: str) -> Dict[str, Any]:
    """Scrape vehicle data from BookMyGarage - optimized for speed"""
    if not http_client:
        return {}
    
    try:
        url = f"https://bookmygarage.com/garage-detail/sussexautocareltd/rh12lw/book/?ref=sussexautocare.co.uk&vrm={vrm}&referrer=widget"
        
        response = await http_client.get(url)
        response.raise_for_status()
        html = response.text
        
        # Fast string search for VrmDetails with different patterns
        patterns = ['"VrmDetails":', '\\"VrmDetails\\":', '"VrmDetails":{']
        vrm_pos = -1
        
        for pattern in patterns:
            vrm_pos = html.find(pattern)
            if vrm_pos != -1:
                break
        
        if vrm_pos == -1:
            print(f"[BMG] VrmDetails not found for {vrm}")
            return {}
        
        # Find the opening brace after VrmDetails
        start = html.find('{', vrm_pos)
        if start == -1:
            print(f"[BMG] Opening brace not found for {vrm}")
            return {}
        
        # Fast brace matching
        brace_count = 0
        in_string = False
        escape_next = False
        
        for i in range(start, len(html)):
            char = html[i]
            
            if escape_next:
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                continue
                
            if char == '"':
                in_string = not in_string
                continue
                
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        json_str = html[start:i + 1]
                        try:
                            # Handle escaped JSON by replacing escaped quotes
                            cleaned_json = json_str.replace('\\"', '"').replace('\\\\', '\\')
                            data = json.loads(cleaned_json)
                            print(f"[BMG] Extracted {len(data)} fields for {vrm}")
                            return data
                        except json.JSONDecodeError as e:
                            print(f"[BMG] JSON error for {vrm}: {e}")
                            # Try original string if cleaning didn't work
                            try:
                                data = json.loads(json_str)
                                print(f"[BMG] Extracted {len(data)} fields for {vrm} (original)")
                                return data
                            except:
                                return {}
        
        print(f"[BMG] Incomplete JSON for {vrm}")
        return {}
        
    except Exception as e:
        print(f"[BMG] Scraping failed for {vrm}: {e}")
        return {}

# ==================== Main Scraping Function ====================
async def get_comprehensive_vehicle_data(vrm: str, username: str = None, password: str = None) -> Dict[str, Any]:
    """Get vehicle data from all sources - optimized for speed, showing all data"""
    
    # Check cache first
    cache_key = f"unified_{vrm}"
    if cache_key in cache:
        cached_data = cache[cache_key]
        return {
            **cached_data,
            "cached": True,
            "cache_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cached_data.get('timestamp', 0)))
        }
    
    # Scrape from all sources concurrently
    username = username or DEFAULT_USERNAME
    password = password or DEFAULT_PASSWORD
    
    e3_scraper = AsyncE3TechnicalScraper(username, password)
    
    # Run scrapers concurrently for maximum speed
    start_time = time.time()
    tasks = [
        e3_scraper.get_vehicle_data(vrm),
        scrape_bookmygarage(vrm)
    ]
    
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        scrape_time = round((time.time() - start_time) * 1000, 2)  # milliseconds
        
        e3_data = results[0] if not isinstance(results[0], Exception) else {}
        bmg_data = results[1] if not isinstance(results[1], Exception) else {}
        
        # Prepare data sources
        data_sources = {}
        sources_used = []
        
        if e3_data:
            data_sources["e3technical"] = e3_data
            sources_used.append("e3technical")
            print(f"[E3] Got {len(e3_data)} fields for {vrm}")
        
        if bmg_data:
            data_sources["bookmygarage"] = bmg_data
            sources_used.append("bookmygarage")
            print(f"[BMG] Got {len(bmg_data)} fields for {vrm}")
        
        if not data_sources:
            raise HTTPException(status_code=404, detail=f"No data found for VRM: {vrm}")
        
        # Process all data without merging duplicates
        all_data = process_all_vehicle_data(data_sources)
        
        # Calculate total fields across all sources
        total_fields = sum(len(source_data) for source_data in all_data.values())
        
        # Prepare response
        response_data = {
            "vrm": vrm,
            "data": all_data,
            "sources": sources_used,
            "cached": False,
            "total_fields": total_fields,
            "scrape_time_ms": scrape_time,
            "timestamp": time.time()
        }
        
        # Cache the result
        cache[cache_key] = response_data
        
        return response_data
        
    except Exception as e:
        logger.error(f"Comprehensive scraping failed: {e}")
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

# ==================== API Routes ====================
@app.get("/")
async def root():
    """API information"""
    response_data = {
        "name": "Unified Vehicle Data API",
        "version": "3.0.0",
        "description": "High-performance API combining multiple vehicle data sources",
        "sources": ["e3technical.haynespro.com", "bookmygarage.com"],
        "features": ["async processing", "intelligent caching", "data deduplication"],
        "cache_info": {
            "current_size": len(cache),
            "max_size": CACHE_MAXSIZE,
            "ttl_seconds": CACHE_TTL
        }
    }
    formatted_json = json.dumps(response_data, indent=2, ensure_ascii=False)
    return PlainTextResponse(
        content=formatted_json,
        media_type="text/plain",
        headers={"Content-Type": "text/plain; charset=utf-8"}
    )





@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    response_data = {
        "current_size": len(cache),
        "max_size": CACHE_MAXSIZE,
        "ttl_seconds": CACHE_TTL,
        "hit_info": "Cache hit info not available with TTLCache"
    }
    formatted_json = json.dumps(response_data, indent=2, ensure_ascii=False)
    return PlainTextResponse(
        content=formatted_json,
        media_type="text/plain",
        headers={"Content-Type": "text/plain; charset=utf-8"}
    )

@app.delete("/cache/clear")
async def clear_cache():
    """Clear the entire cache"""
    cache.clear()
    return {"message": "Cache cleared successfully"}







@app.get("/{vrm}")
async def get_vehicle_data(
    vrm: str = Path(..., pattern=r"^[A-Za-z0-9]{1,8}$", description="Vehicle Registration Mark"),
    username: Optional[str] = Query(None, description="E3Technical username"),
    password: Optional[str] = Query(None, description="E3Technical password"),
    force_refresh: bool = Query(False, description="Force refresh cache")
):
    """Get comprehensive vehicle data from all sources"""
    
    vrm = clean_vrm(vrm)
    
    if force_refresh:
        cache.pop(f"unified_{vrm}", None)
    
    try:
        result = await get_comprehensive_vehicle_data(vrm, username, password)
        response_data = {k: v for k, v in result.items() if k != 'timestamp'}
        formatted_json = json.dumps(response_data, indent=2, ensure_ascii=False)
        return PlainTextResponse(
            content=formatted_json,
            media_type="text/plain",
            headers={"Content-Type": "text/plain; charset=utf-8"}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API error for VRM {vrm}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 