FROM python:3.8-slim-buster

# Install dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    libglib2.0-0 \
    libnss3 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    pandoc \
    fonts-noto-cjk \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV CHROME_BIN=/usr/bin/chromium-browser
ENV CHROME_PATH=/usr/lib/chromium/

ARG CONTAINER_VERSION
ENV CONTAINER_VERSION ${CONTAINER_VERSION}

WORKDIR /app

# Copy requirements and install them
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

# Copy the application code
COPY . .

# Expose port 5000
EXPOSE 5000

# Run the application
CMD ["python3", "app.py"]
