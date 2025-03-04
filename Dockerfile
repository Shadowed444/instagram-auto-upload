# Use the jrottenberg/ffmpeg image with Python 3.10
FROM jrottenberg/ffmpeg:5.1.2-python3.10

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