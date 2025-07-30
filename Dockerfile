FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install system dependencies in one layer
RUN apt-get update && apt-get install -y \
    git \
    iputils-ping \
    iproute2 \
    curl \
    wget \
    gnupg2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get update && \
    apt-get install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Expose ports
EXPOSE 8003
EXPOSE 4567

# Use python command instead of direct manage.py for better compatibility
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8003"]