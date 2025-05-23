# Vehicle VRM Data API

A simple API that retrieves vehicle data from e3technical.haynespro.com based on a Vehicle Registration Mark (VRM).

## Features

- **Simple API**: Direct access to vehicle data using just the VRM in the URL
- **Data Caching**: Implements a caching system to reduce repeated scraping requests
- **CORS Enabled**: Accepts requests from all origins

## Local Setup

### Prerequisites

- Python 3.7+ installed on your system

### Setup Steps

1. Clone or download this repository

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   ```

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the application:
   ```bash
   python3 app.py
   ```

The API will be accessible at http://localhost:7654

## API Usage

### Get Vehicle Data by VRM

```
GET http://localhost:7654/{vrm}
```

Example:
```
http://localhost:7654/EG17LFW
```

### Submit VRM via POST

```
POST http://localhost:7654/
Content-Type: application/x-www-form-urlencoded

vrm=EG17LFW
```

### Optional Parameters

Both endpoints accept these optional parameters:
- `username`: Custom username for e3technical.haynespro.com
- `password`: Custom password for e3technical.haynespro.com
- `force_refresh`: Set to 'true' to bypass cache

## Response Format

```json
{
  "data": {
    "Vehicle Registration Mark (Current)": "EG17LFW",
    "Combined VIN": "WF05XXGCC5HR04327",
    "Combined Make": "FORD",
    "Combined Model": "FOCUS ZETEC EDITION",
    ...
  },
  "cached": false
}
```
