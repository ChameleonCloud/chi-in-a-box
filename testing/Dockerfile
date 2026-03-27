FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    git rsync wget curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/chi-in-a-box

# Copy the repo (expects docker build context = chi-in-a-box root)
COPY . .

# Install chi-in-a-box deps (creates venv with kolla-ansible, ansible, yq, etc.)
RUN ./cc-ansible install_deps

# Add test deps to the same venv
RUN venv/bin/pip install pytest pyyaml

WORKDIR /opt/chi-in-a-box/testing
ENTRYPOINT ["/opt/chi-in-a-box/venv/bin/pytest"]
CMD ["-v"]
