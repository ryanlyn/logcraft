.PHONY: dev-env

ONE_SHELL:
env:
	@echo "Making Development Environment"
	if [ -d ".env/" ]; then rm -r ".env/"; fi
	virtualenv --python=python3.7 ".env/" && \
	. ".env/bin/activate" && \
	pip install -U pip && \
	pip install -r "./requirements-dev.txt"