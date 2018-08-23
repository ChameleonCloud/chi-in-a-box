PLAYBOOKS     := $(basename $(notdir $(shell find playbooks -name '*.yml')))
TEST_TARGETS  := $(PLAYBOOKS:%=%-test)
SHELL_TARGETS := $(PLAYBOOKS:%=%-shell)
WATCH_TARGETS := $(PLAYBOOKS:%=%-watch)

TAGS ?= all

.PHONY: $(TEST_TARGETS)
$(TEST_TARGETS): %-test:
	PLAYBOOK=$* TAGS=$(TAGS) vagrant up --provision

.PHONY: $(SHELL_TARGETS)
$(SHELL_TARGETS): %-shell:
	PLAYBOOK=$* vagrant ssh

.PHONY: $(WATCH_TARGETS)
$(WATCH_TARGETS): %-watch:
	PLAYBOOK=$* vagrant rsync-auto
