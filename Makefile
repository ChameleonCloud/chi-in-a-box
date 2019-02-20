PLAYBOOKS     := $(basename $(notdir $(shell find playbooks -name '*.yml')))
TEST_TARGETS  := $(PLAYBOOKS:%=%-test)
SHELL_TARGETS := $(PLAYBOOKS:%=%-shell)
WATCH_TARGETS := $(PLAYBOOKS:%=%-watch)
CLEAN_TARGETS := $(PLAYBOOKS:%=%-clean)

TAGS ?= all

.PHONY: setup
setup: kolla/etc venv vault_password
	@ echo "Current inventory (.ansible-inventory): $$(cat .ansible-inventory 2>/dev/null || echo 'none')"

kolla/etc:
	@ echo "Creating custom node configuration directory for Kolla"
	@ mkdir -p "$@"

venv: requirements.txt
	@ echo "Initializing virtualenv"
	@ virtualenv --system-site-packages $@
	@ echo "Installing base dependencies to virtualenv directory"
	@ $@/bin/pip install -r requirements.txt
	@ touch $@

vault_password:
	@ echo "Creating new Ansible Vault password"
	@ openssl rand -base64 2048 > $@

#
# Development targets
#

.PHONY: $(TEST_TARGETS)
$(TEST_TARGETS): %-test:
	PLAYBOOK=$* TAGS=$(TAGS) vagrant up --provision

.PHONY: $(SHELL_TARGETS)
$(SHELL_TARGETS): %-shell:
	PLAYBOOK=$* vagrant ssh

.PHONY: $(WATCH_TARGETS)
$(WATCH_TARGETS): %-watch:
	PLAYBOOK=$* vagrant rsync-auto

.PHONY: $(CLEAN_TARGETS)
$(CLEAN_TARGETS): %-clean:
	PLAYBOOK=$* vagrant destroy
