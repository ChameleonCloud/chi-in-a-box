FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    git rsync wget curl iproute2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/chi-in-a-box

# Copy dependency files first (changes rarely, cacheable layer)
# .git and .gitmodules needed for `git submodule update --init` in install_deps
COPY .git .git
COPY .gitmodules cc-ansible requirements.txt requirements.yml ./
COPY src/kolla-ansible src/kolla-ansible

# install_deps: creates venv, installs kolla-ansible, ansible, yq, galaxy roles
RUN ./cc-ansible install_deps

# Copy test requirements and install into the same venv
COPY testing/requirements-test.txt testing/requirements-test.txt
RUN venv/bin/pip install -r testing/requirements-test.txt

# Now copy everything else (changes often, but deps are cached above)
COPY . .

ENV PATH="/opt/chi-in-a-box/venv/bin:$PATH"

WORKDIR /opt/chi-in-a-box/testing

ENTRYPOINT ["pytest"]
CMD ["-v", "-rf", "--tb=short"]
