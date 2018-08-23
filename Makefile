PLAYBOOKS     := $(basename $(notdir $(shell find playbooks -name '*.yml')))
TEST_TARGETS  := $(PLAYBOOKS:%=%-test)
SHELL_TARGETS := $(PLAYBOOKS:%=%-shell)

TAGS         ?= all

.PHONY: $(TEST_TARGETS)
$(TEST_TARGETS): %-test:
	PLAYBOOK=$* TAGS=$(TAGS) vagrant up --provision

.PHONY: $(SHELL_TARGETS)
$(SHELL_TARGETS): %-shell:
	PLAYBOOK=$* TAGS=$(TAGS) vagrant ssh
