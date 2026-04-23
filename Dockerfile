FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    curl \
    git \
    iproute2 \
    python3 \
    python3-pip \
    python3-venv \
    rsync \
    wget \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/chi-in-a-box

COPY .git .git
COPY src src
COPY roles roles
COPY playbooks playbooks
COPY requirements.txt requirements.yml cc-ansible .

# install_deps: creates venv, installs kolla-ansible, ansible, yq, galaxy roles
RUN ./cc-ansible install_deps -vv

COPY testing/requirements-test.txt testing/requirements-test.txt
# Copy test requirements and install into the same venv
RUN venv/bin/pip install -r testing/requirements-test.txt

COPY . .

ENV VIRTUAL_ENV="/opt/chi-in-a-box/venv/"
ENV PATH="/opt/chi-in-a-box/venv/bin:$PATH"
