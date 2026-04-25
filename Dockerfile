FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all Python files
COPY *.py .

# Copy .env.example as reference
COPY .env.example .env.example

# Create directory for session files (use volume mount in Railway)
RUN mkdir -p /app/session

# Create non-root user
RUN useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app

USER botuser

# Set default command
CMD ["python", "main.py"]
