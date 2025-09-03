# Use Python 3.11 slim image
FROM python:3.11-slim

# Install system dependencies including FFmpeg and PostgreSQL dev headers
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Make start script executable and use it
COPY start.sh .
RUN chmod +x start.sh

# Start the application
CMD ["./start.sh"]