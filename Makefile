
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
