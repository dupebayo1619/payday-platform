# Use Python again, just like the API
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the worker logic
COPY . .

# Start the worker
CMD ["python", "worker.py"]
