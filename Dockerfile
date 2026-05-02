# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Expose the port the app runs on
# Render provides the PORT environment variable
EXPOSE 8000

# Run the application
# We use 0.0.0.0 to bind to all interfaces
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
