FROM python:3.12.4

# Set the working directory in the container
WORKDIR /app


RUN apt-get update && apt-get install -y \
    gcc \
    ffmpeg \
    curl \
    libffi-dev \
    libssl-dev \
    build-essential \
    redis-server \
    && rm -rf /var/lib/apt/lists/*


RUN curl https://sh.rustup.rs -sSf | sh -s -- -y


ENV PATH="/root/.cargo/bin:${PATH}"

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose port for Redis (if needed)
EXPOSE 6379

# Define the command to run the bot
CMD ["python", "bot.py"]