#!/bin/sh -e

# Install requirements
echo "Install required apt packages..."
sudo add-apt-repository \
       "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
       $(lsb_release -cs) \
       stable"
sudo apt-get update
sudo apt-get -y install \
    python-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    python-apt \
    python-pip \
    python-setuptools \
    wget \
    curl \
    apt-transport-https \
    ca-certificates

sudo apt-get -y --allow-unauthenticated install \
    docker-ce

echo "Install required pip packages..."
sudo pip install --upgrade \
    pip \
    setuptools \
    virtualenvwrapper \
    pytest

sudo usermod -aG docker $(whoami)

