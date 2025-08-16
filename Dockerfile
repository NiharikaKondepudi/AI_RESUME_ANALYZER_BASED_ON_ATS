# Start with a clean computer that already has Python 3.9 installed.
FROM python:3.9-slim

# Create a folder inside that computer called /app to work in.
WORKDIR /app

# Install system-level tools. Here, we're installing Tesseract OCR.
RUN apt-get update && apt-get install -y tesseract-ocr

# Copy our list of Python libraries (requirements.txt) into the folder.
COPY requirements.txt .

# Install all the Python libraries from that list.
RUN pip install -r requirements.txt

# Copy all of our project's code (app.py, analyzer.py, etc.) into the folder.
COPY . .

# Set the final command to run when the application starts. This starts our web server.
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]