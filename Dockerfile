# Use an official lightweight Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Tell Cloud Run to run this command to start the web server
# It will listen on the port provided by the PORT environment variable (e.g., 8080)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "main:app"]