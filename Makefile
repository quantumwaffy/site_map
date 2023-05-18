#!make

.PHONY: check_image check_container

# --- Docker
image_name := site_map_parser
container_name := site_map


check_image:
    ifeq ($(shell docker images -q $(image_name)),)
		@$(MAKE) build
    endif

check_container:
    ifneq ($(shell docker ps -aq -f name=$(container_name)),)
		@$(MAKE) rm
    endif


help:
	@echo "Please use 'make <target>' where <target> is one of:"
	@echo "    shelp                     Parser help message"
	@echo "    parse ARGS=\"_args_\"       Run parsing from a Docker container with ARGS provided to the script"
	@echo "    rmf                       Remove the used image and container"

build:
	@docker build -t $(image_name) .

parse: check_image check_container
	@docker run --name $(container_name) $(image_name) $(ARGS)

rm:
	@docker rm $(container_name)

rmf: check_container
	@docker rmi $(image_name) -f

shelp: check_image check_container
	@docker run --name $(container_name) $(image_name) -h
