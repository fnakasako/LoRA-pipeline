# Dockerfile

# Start from an official PyTorch image with CUDA support
FROM pytorch/pytorch:2.3.1-cuda12.1-cudnn8-runtime

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies required by our Python libraries
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libmagic1 \
    rsync \
    && rm -rf /var/lib/apt/lists/*

# Copy ONLY the requirements file first to leverage Docker's caching
COPY requirements.txt .

RUN apt-get update && apt-get install -y build-essential

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of our project code into the working directory
COPY . .