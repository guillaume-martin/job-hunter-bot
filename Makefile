
# Variables
IMAGE_NAME = job-hunter-bot
TAG = latest
DOCKERFILE_PATH = ./docker/Dockerfile

# Build target
build:
	docker build -t $(IMAGE_NAME):$(TAG) -f $(DOCKERFILE_PATH) .

run:
	docker run -i --rm -v ~/.aws:/home/appuser/.aws $(IMAGE_NAME):$(TAG)

.PHONY: build run

# Tests
test:          ## Run unit tests
	poetry run pytest tests/unit/ -v

test-all:      ## Run all tests including integration
	poetry run pytest -v
