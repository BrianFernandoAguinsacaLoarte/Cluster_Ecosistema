# Master Node - Ecosystem Simulation API
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY api/ ./api/
COPY templates/ ./templates/
COPY static/ ./static/

# Expose port
EXPOSE 5000

# Run Flask app
CMD ["python", "app.py"]
