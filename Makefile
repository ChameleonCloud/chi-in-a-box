PLAYBOOKS    := $(basename $(notdir $(shell find playbooks -name '*.yml')))
TEST_TARGETS := $(PLAYBOOKS:%=test-%)
TAGS ?= all

.PHONY: $(TEST_TARGETS)
$(TEST_TARGETS): test-%:
	TAGS=$(TAGS) PLAYBOOK=$*.yml vagrant up --provision
