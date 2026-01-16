# Dockerfile – Build Streamlit GEO Tool image

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose Streamlit default port
EXPOSE 8501

# Environment variables (optional)
ENV PYTHONUNBUFFERED=1

# Run Streamlit app
CMD ["streamlit", "run", "scripts/app.py", "--server.port", "8501", "--server.enableCORS", "false"]
