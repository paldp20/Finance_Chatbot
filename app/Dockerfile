# FROM python:3
# WORKDIR /app
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY . .
# CMD ["streamlit", "run", "app.py"]

# # Start from a base Python image
# FROM python:3.9-slim

# # Set the working directory
# WORKDIR /app

# # Copy requirements for the app service
# COPY ./requirements.txt /app/
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the source code for the app
# COPY ./app.py /app/

# # Set entrypoint for the app
# CMD ["python", "app.py"]
#_________________________________________________________________________________
# # Use specific Python version instead of generic 'python:3'
# FROM python:3.9-slim

# # Set working directory
# WORKDIR /app

# # Install system dependencies first (some Python packages need them)
# RUN apt-get update && apt-get install -y \
#     gcc \
#     python3-dev \
#     && rm -rf /var/lib/apt/lists/*

# # Copy requirements first to leverage Docker cache
# COPY ./requirements.txt /app/
# RUN pip install --no-cache-dir -r requirements.txt

# # Copy application code
# COPY . .

# # Proper Streamlit configuration
# EXPOSE 8501
# HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
# CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

# app/Dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from app directory
COPY ./app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app/ .

# Copy utils from ticker_fetcher directory
COPY ./ticker_fetcher/utils.py .

# Proper Streamlit configuration
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]