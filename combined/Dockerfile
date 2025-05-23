# Combined Vehicle Data API - Docker Image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for web scraping
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the API application
COPY unified_vehicle_api.py .

# Expose the port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the application
CMD ["python", "unified_vehicle_api.py"] 