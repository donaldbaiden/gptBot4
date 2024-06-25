# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory in the container
WORKDIR bot.py

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents into the container
COPY . .

# Set environment variables
ENV TELEGRAM_TOKEN=${TELEGRAM_TOKEN}
ENV OPENAI_API_KEY=${OPENAI_API_KEY}
ENV REDIS_HOST=${REDIS_HOST}
ENV REDIS_PORT=${REDIS_PORT}

# Define the command to run the bot
CMD ["python", "bot.py"]