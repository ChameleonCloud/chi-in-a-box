# Troubleshooting

### Speeding up repeated runs

Rerunning the install can take a long time. You can speed this up by uncommenting lines in the file `kolla-skip-tags`. Each line corresponds to a tag associated with an ansible task. For example, if the script keeps failing at configuring neutron, then uncomment the lines prior to neutron. Ansible will run the common setup tasks, then skip to the first tag that isn't uncommented.

### Finding out what's failing

Many times a failure is caused by a typo or missing line in defaults.yml or your host configuration. Run `./cc-ansible deploy` with multiple `-v` flags to get line-by-line errors.

For example, on centos8, /etc/modules-load.d may not exist, and you'll get an error like `failed: [shermanm-chibox] (item=ip_vs) => {"ansible_loop_var": "item", "changed": false, "item": {"name": "ip_vs"}, "msg": "Destination /etc/modules does not exist !", "rc": 257}`

running it with `-vvv` will show that it first checked for `/etc/modules-load.d` which also didn't exist.
