# Use a lightweight Python image that supports both ARM64 and x86 architectures
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# TextBlob requires downloading a specific NLP language model
RUN python -m textblob.download_corpora

# Copy all your project files into the container
COPY . .

# Expose the ports for FastAPI (8000) and Streamlit (8501)
EXPOSE 8000 8501