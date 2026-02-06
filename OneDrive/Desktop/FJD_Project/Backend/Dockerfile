# 1. Use Python 3.11 (Better compatibility with TensorFlow 2.x)
FROM python:3.11-slim

# 2. Set environment variables to keep Python clean
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set up the working directory
WORKDIR /app

# 4. Copy requirements first (Docker caching layer)
COPY requirements.txt .

# 5. Install libraries (No Cache to save space)
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of the code (including the .h5 Brain)
COPY . .

# 7. Run the server (Uses the PORT environment variable provided by Render)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]