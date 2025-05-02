FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for React frontend
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY requirements-dev.txt .
COPY ai_models/requirements.txt ai_models-requirements.txt
COPY ui/requirements.txt ui-requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt \
    && pip install --no-cache-dir -r ai_models-requirements.txt \
    && pip install --no-cache-dir -r ui-requirements.txt \
    && pip install --no-cache-dir flask-cors flask-socketio python-multipart

# Copy package.json files
COPY package.json package-lock.json ./

# Install Node.js dependencies
RUN npm install

# Copy the rest of the application
COPY . .

# Build the React frontend
RUN cd ui/react_frontend && npm install && npm run build

# Expose port
EXPOSE 5000

# Set health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/ || exit 1

# Run the application
CMD ["python", "run_ui.py"]
