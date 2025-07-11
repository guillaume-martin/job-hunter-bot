FROM python:3.13-slim-bookworm

WORKDIR /app

# Install system dependencies and Geckodriver
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        gcc \
        curl \
        ca-certificates \
        libxml2-dev \
        libxslt1-dev \
        firefox-esr \
    && curl -L https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz | tar xz -C /usr/local/bin \
    && apt-get clean cache \
    && rm -rf /var/lib/apt/lists/* 

# Create a non-root user and switch to it
RUN useradd -m appuser 
USER appuser

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt ./src/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r ./src/requirements.txt

# Copy the rest of the application code
COPY ./src/ ./src/


ENTRYPOINT ["python", "./src/job_search.py"]
