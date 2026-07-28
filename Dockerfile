# Use an official, lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Python scripts into the container
COPY smard_api.py .
COPY read_db.py .

# Command to run when the container starts
CMD ["python", "smard_api.py"]