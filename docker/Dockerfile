ARG POETRY_VERSION=2.1.1
ARG POETRY_PLUGIN_EXPORT_VERSION=1.9.0
ARG GECKODRIVER_VERSION=0.36.0

#  Stage 1: builder
FROM python:3.11-slim-bookworm AS builder

ARG POETRY_VERSION
ARG POETRY_PLUGIN_EXPORT_VERSION

WORKDIR /app

# Install Poetry to export dependencies
RUN pip install --no-cache-dir \
    poetry==${POETRY_VERSION} \
    poetry-plugin-export==${POETRY_PLUGIN_EXPORT_VERSION}

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Export production dependencies to requirements.txt
# then install them to /runtime so we can copy to the final stage
RUN poetry export --without-hashes --without dev -f requirements.txt -o requirements.txt \
    && pip install --no-cache-dir --prefix=/runtime -r requirements.txt


#  Stage 2: final image
FROM python:3.11-slim-bookworm

ARG GECKODRIVER_VERSION

WORKDIR /app

# Install only runtime system dependencies
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends \
        curl=7.88.1-10+deb12u14 \
        ca-certificates=20230311+deb12u1 \
        libxml2=2.9.14+dfsg-1.3~deb12u5 \
        libxslt1.1=1.1.35-1+deb12u3 \
        firefox-esr=140.8.0esr-1~deb12u1 \
    && curl -L "https://github.com/mozilla/geckodriver/releases/download/v${GECKODRIVER_VERSION}/geckodriver-v${GECKODRIVER_VERSION}-linux64.tar.gz" \
       | tar xz -C /usr/local/bin \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy installed Python packages from builder
COPY --from=builder /runtime /usr/local

# Copy application source
COPY ./src/ ./src/

# Create logs directory and give appuser ownership
RUN mkdir -p ./src/logs \
    && useradd -m appuser \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

ENTRYPOINT ["python", "-m", "src.job_search"]
