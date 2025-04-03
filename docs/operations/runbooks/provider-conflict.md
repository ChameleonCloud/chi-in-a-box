Symptom: Nova shows a 409 conflict for an instance UUID.

Resolution:
1. Run `openstack resource provider list --name <uuid>` to get the resource provider UUID
2. run `openstack resource provider delete <uuid>` to remove that provider. It should be auto-recreated if needed.