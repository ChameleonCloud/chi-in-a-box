PLAYBOOKS    := $(basename $(notdir $(shell find playbooks -name '*.yml')))
TEST_TARGETS := $(PLAYBOOKS:%=test-%)

.PHONY: $(TEST_TARGETS)
$(TEST_TARGETS): test-%:
	PLAYBOOK=$*.yml vagrant up --provision
