# Stage 1: Build stage
FROM ubuntu:latest AS builder

# Install system dependencies (ffmpeg)
RUN apt-get update && apt-get install -y ffmpeg

# Stage 2: Final stage
FROM python:3.10-slim

# Copy ffmpeg from the builder stage
COPY --from=builder /usr/bin/ffmpeg /usr/bin/ffmpeg

# Set the working directory
WORKDIR /workspace

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port the app runs on
EXPOSE 8080

# Run the application
CMD ["python", "auto_upload.py"]