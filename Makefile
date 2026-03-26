
# Variables
IMAGE_NAME = job-hunter-bot
TAG = latest
DOCKERFILE_PATH = ./docker/Dockerfile

# Build targets
build:
	docker build -t $(IMAGE_NAME):$(TAG) -f $(DOCKERFILE_PATH) .

build-clean:
	docker build --no-cache -t $(IMAGE_NAME):$(TAG) -f $(DOCKERFILE_PATH) .

run:
	mkdir -p output
	docker run -i --rm \
        -v ~/.aws:/home/appuser/.aws \
        -v $$PWD/output:/app/output \
        $$([ -f src/search_config.yaml ] && echo "-v $$PWD/src/search_config.yaml:/app/src/search_config.yaml:ro") \
        --env-file src/.env \
        $(IMAGE_NAME):$(TAG)

.PHONY: build build-clean run

# Tests
test:          ## Run unit tests
	poetry run pytest tests/unit/ -v

test-all:      ## Run all tests including integration
	poetry run pytest -v
