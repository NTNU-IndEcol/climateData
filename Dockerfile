# Use official Python runtime as base image
FROM python:3.9-slim

# Use official Python runtime as base image
FROM python:3.9-slim

# Set working directory in container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies including geospatial libraries
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libexpat1 \
    libgdal-dev \
    libspatialindex-dev \
    libgeos-dev \
    proj-bin \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create necessary directories
# RUN mkdir -p  download

# Expose port
EXPOSE 5000

# Set the command to run the application using your existing app.py
CMD ["python", "app/app.py"]
