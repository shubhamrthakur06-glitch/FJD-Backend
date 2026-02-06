# 1. Use a Python Image as the base
FROM python:3.9-slim

# 2. Install Tesseract (The Linux way)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Set up the working directory
WORKDIR /app

# 4. Copy the files and install Python libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the code
COPY . .

# 6. Run the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]