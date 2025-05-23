#!/usr/bin/env python3
"""
Flask implementation for E3 Technical HaynesPro Web Scraper
This provides an efficient API for retrieving vehicle data by VRM.
"""

import os
import time
from flask import Flask, request, jsonify
from flask_caching import Cache
from flask_cors import CORS
from scraper import E3TechnicalScraper

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all origins
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure caching
cache_config = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",  # Simple in-memory cache
    "CACHE_DEFAULT_TIMEOUT": 3600  # Cache timeout in seconds (1 hour)
}
app.config.from_mapping(cache_config)
cache = Cache(app)

# Default credentials
DEFAULT_USERNAME = "NT445A"
DEFAULT_PASSWORD = "7g2ba29mz4"

# Helper functions
def clean_vrm(vrm):
    """Clean and normalize VRM"""
    return vrm.upper().strip().replace(" ", "")

# Routes
@app.route('/')
def root():
    """Root endpoint with API information"""
    return jsonify({
        "name": "Full Vehicle Data API",
        "version": "1.0.0"
    })

@app.route('/<vrm>')
def get_vehicle_data(vrm):
    """
    Get vehicle data by VRM.
    
    Args:
        vrm: Vehicle Registration Mark
        
    Query Parameters:
        username: Username for e3technical.haynespro.com (optional)
        password: Password for e3technical.haynespro.com (optional)
        force_refresh: Force refresh cache (optional)
        
    Returns:
        Vehicle data
    """
    vrm = clean_vrm(vrm)
    username = request.args.get('username', DEFAULT_USERNAME)
    password = request.args.get('password', DEFAULT_PASSWORD)
    force_refresh = request.args.get('force_refresh', 'false').lower() == 'true'
    
    # Check cache first if not forcing refresh
    if not force_refresh:
        cached_data = cache.get(vrm)
        if cached_data:
            cached_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(cached_data.get('timestamp', 0)))
            return jsonify({
                "data": cached_data.get('data', {}),
                "cached": True,
                "cache_time": cached_time
            })
    
    # Create scraper and get vehicle data
    try:
        scraper = E3TechnicalScraper(username, password)
        data = scraper.get_vehicle_data(vrm)
        
        if "error" in data:
            if "VRM search failed" in data["error"]:
                return jsonify({"error": f"No data found for VRM: {vrm}"}), 404
            else:
                return jsonify({"error": data["error"]}), 500
        
        # Cache the data with timestamp
        cache_data = {
            'data': data,
            'timestamp': time.time()
        }
        cache.set(vrm, cache_data)
        
        return jsonify({
            "data": data,
            "cached": False
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['POST'])
def post_vehicle_data():
    """
    Get vehicle data by VRM (form submission).
    
    Form Parameters:
        vrm: Vehicle Registration Mark
        username: Username for e3technical.haynespro.com (optional)
        password: Password for e3technical.haynespro.com (optional)
        force_refresh: Force refresh cache (optional)
        
    Returns:
        Vehicle data
    """
    vrm = request.form.get('vrm')
    if not vrm:
        return jsonify({"error": "VRM is required"}), 400
        
    username = request.form.get('username', DEFAULT_USERNAME)
    password = request.form.get('password', DEFAULT_PASSWORD)
    force_refresh = request.form.get('force_refresh', 'false').lower() == 'true'
    
    # Redirect to GET endpoint
    return get_vehicle_data(vrm)

if __name__ == "__main__":
    # Use port 7654, which is likely not in use based on your image
    port = int(os.environ.get("PORT", 7654))
    app.run(host="0.0.0.0", port=port, debug=True)
