FROM python:3.13-slim-bookworm

WORKDIR /app

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends --fix-missing \
        gcc curl ca-certificates libxml2-dev libxslt1-dev  firefox-esr \
    && curl -L https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz | tar xz -C /usr/local/bin \
    && apt-get clean cache \
    && rm -rf /var/lib/apt/lists/* 


COPY ./src/ ./src/
COPY requirements.txt ./src/requirements.txt

# Install  environment
RUN pip install -r ./src/requirements.txt

ENTRYPOINT ["python", "./src/job_search.py"]
