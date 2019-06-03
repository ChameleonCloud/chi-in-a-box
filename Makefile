.PHONY: setup
setup: venv roles/galaxy.ansible.com

venv: requirements.txt
	@ echo "Initializing virtualenv"
	@ virtualenv --system-site-packages $@
	@ echo "Installing base dependencies to virtualenv directory"
	@ $@/bin/pip install -r requirements.txt
	@ touch $@

roles/galaxy.ansible.com: requirements.yml venv
	@ echo "Installing Ansible Galaxy roles"
	@ mkdir -p $@
	@ venv/bin/ansible-galaxy install -p $@ -r $<
	@ touch $@
