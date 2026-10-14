# Ceph RGW Quotas

**Task**: make sure new projects get a default object store (Ceph RGW) quota, and every existing project has a quota, without blocking writes for any project that already uses more than the default.

**Why**: without quotas, one project can fill the RGW data pool. Once its OSDs reach the full ratio, writes stop for every project, not just the one that filled it.

Sizes are in bytes: 1 TiB is `1099511627776`, and `-1` means unlimited. `radosgw-admin --max-size` also accepts `1T` for 1 TiB. `ceph config set` reads `1T` as 10^12 bytes, so give `ceph config set` plain bytes.

### Get a shell

Run the `ceph` and `radosgw-admin` commands on a Ceph admin host, in `cephadm shell` or on any host with the Ceph CLI and the admin keyring. Run the `openstack` commands with admin credentials for the site (for example `admin-openrc.sh`).

### 1. Find out where you are

**Is there a default for new projects?** `-1` means there is none:

```shell
ceph config get client.rgw rgw_user_default_quota_max_size
```

**Which projects already use more than the default you plan?** Top 20 owners, with all their buckets added up (TiB, owner):

```shell
radosgw-admin bucket stats | jq -r '
  group_by(.owner)
  | map({owner: .[0].owner, b: (map(.usage["rgw.main"].size_actual // 0) | add)})
  | sort_by(-.b) | .[:20][]
  | [(.b / pow(2;40) * 100 | round / 100), .owner] | @tsv'
```

`bucket stats` reads every bucket index, so it can take a while. Owners are RGW users. RGW creates one user per Keystone project, the first time the project uses the object store. Its uid is `<project_id>$<project_id>`, or just `<project_id>` for users created before `rgw_keystone_implicit_tenants` was set. Owners without a project id, such as backup accounts, are service users. To get a project's name:

```shell
openstack project show <project_id> -f value -c name
```

**Which projects have no quota?** Write an [rgw-quota-sync](https://github.com/ChameleonCloud/rgw-quota-sync) config with the default you plan (its README covers the file and the RGW user it needs), then run it without `--apply`. This dry run changes nothing. Each `quota would change from disabled` line is a project with no quota today.

### 2. Protect the projects already over the default

For each project from step 1 that uses more than the default, add an override to `project_quotas` in the rgw-quota-sync config, set above its current usage. Its writes keep working. Whether to bring it down later is a separate decision, made with the project.

Keys under `project_quotas` are Keystone project ids, without the `$` part.

### 3. Set the default for new projects

```shell
ceph config set client.rgw rgw_user_default_quota_max_size 1099511627776
```

This applies only to RGW users created after the change, so existing projects still need step 4.

### 4. Give every existing project a quota

1. Run rgw-quota-sync without `--apply` again. Check that no `would change` line sets a quota below a project's usage from step 1.
1. Run it with `--apply`.

It sets quotas only on Keystone project users, never on service users. It overwrites every enabled quota that differs from its config, including ones set by hand, so put any quota you want to keep into `project_quotas` first.

To set one project by hand instead:

```shell
radosgw-admin quota set --quota-scope=user --uid='<project_id>$<project_id>' --max-size=1099511627776
radosgw-admin quota enable --quota-scope=user --uid='<project_id>$<project_id>'
```

### Check

Run rgw-quota-sync without `--apply`. Its last line should be `all Keystone users have their configured quota`. For one project:

```shell
radosgw-admin user info --uid='<project_id>$<project_id>' | jq .user_quota
```

`user_quota` should show `"enabled": true` and the `max_size` you set. Once a project is over its quota, uploads fail with `QuotaExceeded`. RGW caches usage, so a project can write past its quota for a while before uploads start failing.
