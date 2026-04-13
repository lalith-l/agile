# 1. Start with a base image (we pull this from Docker Hub)
FROM python:3.10-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy your requirements file into the image
COPY requirements.txt .

# 4. Install your Python dependencies
RUN pip install -r requirements.txt

# 5. Copy the rest of your application code into the image
COPY . .

# 6. Tell Docker what command to run when the container starts
CMD ["python", "engine.py"]