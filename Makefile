
# Variables
IMAGE_NAME = remote-bot
TAG = test
DOCKERFILE_PATH = ./docker/Dockerfile

# Build target
build:
	docker build -t $(IMAGE_NAME):$(TAG) -f $(DOCKERFILE_PATH) .


.PHONY: build
