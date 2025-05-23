#!/usr/bin/env python3
"""
Unified Vehicle Data API - FastAPI implementation
Combines data from multiple sources for comprehensive vehicle information.
Optimized for speed with async processing and intelligent caching.
"""

import asyncio
import logging
import os
import time
from typing import Dict, Any, Optional, List
from collections import defaultdict
import json

import httpx
import mechanicalsoup
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from cachetools import TTLCache
from pydantic import BaseModel
import re

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

# ==================== FastAPI Setup ====================
app = FastAPI(
    title="Unified Vehicle Data API",
    version="3.0.0",
    description="High-performance API combining multiple vehicle data sources"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTP client for async requests
http_client: Optional[httpx.AsyncClient] = None

@app.on_event("startup")
async def startup():
    global http_client
    http_client = httpx.AsyncClient(
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        timeout=15.0,
        follow_redirects=True
    )
    logger.info("Unified Vehicle API started")

@app.on_event("shutdown")
async def shutdown():
    if http_client:
        await http_client.aclose()

# ==================== Data Models ====================
class VehicleResponse(BaseModel):
    vrm: str
    data: Dict[str, Any]
    sources: List[str]
    cached: bool
    cache_time: Optional[str] = None
    total_fields: int

# ==================== Helper Functions ====================
def clean_vrm(vrm: str) -> str:
    """Clean and normalize VRM"""
    return vrm.upper().strip().replace(" ", "")

def merge_vehicle_data(data_sources: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Intelligently merge data from multiple sources, avoiding duplicates"""
    merged = {}
    source_priority = ["e3technical", "bookmygarage"]  # e3technical has priority
    
    # Collect all unique keys
    all_keys = set()
    for source_data in data_sources.values():
        all_keys.update(source_data.keys())
    
    # Merge with priority
    for key in sorted(all_keys):
        for source in source_priority:
            if source in data_sources and key in data_sources[source]:
                value = data_sources[source][key]
                if value and str(value).strip():  # Only use non-empty values
                    merged[key] = value
                    break
    
    return merged

# ==================== E3Technical Scraper ====================
class AsyncE3TechnicalScraper:
    """Async version of E3Technical scraper for better performance"""
    
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.url = "https://e3technical.haynespro.com/"
        self.session_data = None
    
    async def get_vehicle_data(self, vrm: str) -> Dict[str, Any]:
        """Get vehicle data from E3Technical (synchronous fallback for now)"""
        try:
            # Using thread pool for blocking operations
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._sync_scrape, vrm)
            return result
        except Exception as e:
            logger.error(f"E3Technical scraping failed: {e}")
            return {}
    
    def _sync_scrape(self, vrm: str) -> Dict[str, Any]:
        """Synchronous scraping method"""
        try:
            browser = mechanicalsoup.StatefulBrowser(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                soup_config={'features': 'lxml'}
            )
            
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
    """Scrape vehicle data from BookMyGarage"""
    if not http_client:
        return {}
    
    try:
        url = f"https://bookmygarage.com/garage-detail/sussexautocareltd/rh12lw/book/?ref=sussexautocare.co.uk&vrm={vrm}&referrer=widget"
        
        response = await http_client.get(url)
        response.raise_for_status()
        
        # Extract JSON data from HTML
        html = response.text
        
        # Look for VrmDetails object
        idx = html.find('"VrmDetails"')
        if idx == -1:
            idx = html.find('\\"VrmDetails\\"')
        if idx == -1:
            return {}
        
        start = html.find('{', idx)
        if start == -1:
            return {}
        
        brace_level = 0
        in_string = False
        escaped = False
        
        for pos in range(start, len(html)):
            ch = html[pos]
            
            if ch == '"' and not escaped:
                in_string = not in_string
            if not in_string:
                if ch == '{':
                    brace_level += 1
                elif ch == '}':
                    brace_level -= 1
                    if brace_level == 0:
                        json_str = html[start:pos + 1]
                        try:
                            data = json.loads(json_str)
                            return data
                        except json.JSONDecodeError:
                            return {}
            
            escaped = (ch == '\\' and not escaped)
        
        return {}
        
    except Exception as e:
        logger.error(f"BookMyGarage scraping failed: {e}")
        return {}

# ==================== Main Scraping Function ====================
async def get_comprehensive_vehicle_data(vrm: str, username: str = None, password: str = None) -> Dict[str, Any]:
    """Get vehicle data from all sources and merge intelligently"""
    
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
    
    # Run scrapers concurrently
    tasks = [
        e3_scraper.get_vehicle_data(vrm),
        scrape_bookmygarage(vrm)
    ]
    
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        e3_data = results[0] if not isinstance(results[0], Exception) else {}
        bmg_data = results[1] if not isinstance(results[1], Exception) else {}
        
        # Prepare data sources
        data_sources = {}
        sources_used = []
        
        if e3_data:
            data_sources["e3technical"] = e3_data
            sources_used.append("e3technical")
        
        if bmg_data:
            data_sources["bookmygarage"] = bmg_data
            sources_used.append("bookmygarage")
        
        if not data_sources:
            raise HTTPException(status_code=404, detail=f"No data found for VRM: {vrm}")
        
        # Merge data intelligently
        merged_data = merge_vehicle_data(data_sources)
        
        # Prepare response
        response_data = {
            "vrm": vrm,
            "data": merged_data,
            "sources": sources_used,
            "cached": False,
            "total_fields": len(merged_data),
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
    return {
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

@app.get("/{vrm}")
async def get_vehicle_data(
    vrm: str = Path(..., regex=r"^[A-Za-z0-9]{1,8}$", description="Vehicle Registration Mark"),
    username: Optional[str] = Query(None, description="E3Technical username"),
    password: Optional[str] = Query(None, description="E3Technical password"),
    force_refresh: bool = Query(False, description="Force refresh cache")
):
    """Get comprehensive vehicle data from all sources"""
    
    vrm = clean_vrm(vrm)
    
    # Force refresh by clearing cache
    if force_refresh:
        cache_key = f"unified_{vrm}"
        cache.pop(cache_key, None)
    
    try:
        result = await get_comprehensive_vehicle_data(vrm, username, password)
        
        # Remove timestamp from response (keep for internal use)
        response_result = {k: v for k, v in result.items() if k != 'timestamp'}
        
        return JSONResponse(content=response_result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API error for VRM {vrm}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    return {
        "current_size": len(cache),
        "max_size": CACHE_MAXSIZE,
        "ttl_seconds": CACHE_TTL,
        "hit_info": "Cache hit info not available with TTLCache"
    }

@app.delete("/cache/clear")
async def clear_cache():
    """Clear the entire cache"""
    cache.clear()
    return {"message": "Cache cleared successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 