# CodeSandbox supports debian & ubuntu based images
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# Example; install htop by default
RUN apt update -y && apt install -y htop

# The project will be mounted in /workspace by default

# Every new shell will open inside the built container

# Docker CLI + daemon (dockerd) are provided by the `docker-in-docker`
# devcontainer feature configured in devcontainer.json, so that the
# `docker` / `docker compose` commands used by setup.sh resolve correctly
# inside the devcontainer.
