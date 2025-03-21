# Dockerfile (in moringa folder)

# Use an official Python image
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copy dependency file and install packages
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy app files
COPY . .

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_ENV=development

# Ensure Flask is executable
RUN chmod +x app.py

# Expose the Flask port
EXPOSE 5000

# Ensure Flask is executed using python -m
CMD ["python", "-m", "flask", "run"]
