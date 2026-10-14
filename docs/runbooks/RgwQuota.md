# Ceph RGW Quotas

**Summary**: make sure no single project can fill the object store (Ceph RGW). Check how full the pool is, find the largest projects, set a default quota for new projects, and give every existing project a quota.

**Consequences**: without quotas, one project can fill the RGW data pool. Once its OSDs reach the full ratio, writes stop for every project, not just the one that filled it.

Sizes are in bytes: 1 TiB is `1099511627776`, and `-1` means unlimited. `radosgw-admin --max-size` also accepts `1T` for 1 TiB. `ceph config set` reads `1T` as 10^12 bytes, so give `ceph config set` plain bytes.

### Get a shell

Run the `ceph` and `radosgw-admin` commands on a Ceph admin host, in `cephadm shell` or on any host with the Ceph CLI and the admin keyring. Run the `openstack` commands with admin credentials for the site (for example `admin-openrc.sh`).

### 1. How full is the pool

```shell
ceph df detail
```

Find the `default.rgw.buckets.data` pool and read `%USED` and `MAX AVAIL`.

### 2. Find the largest projects and buckets

Top 20 owners, with all their buckets added up (TiB, owner):

```shell
radosgw-admin bucket stats | jq -r '
  group_by(.owner)
  | map({owner: .[0].owner, b: (map(.usage["rgw.main"].size_actual // 0) | add)})
  | sort_by(-.b) | .[:20][]
  | [(.b / pow(2;40) * 100 | round / 100), .owner] | @tsv'
```

Top 20 buckets (TiB, owner, bucket):

```shell
radosgw-admin bucket stats | jq -r '
  map({bucket, owner, b: (.usage["rgw.main"].size_actual // 0)})
  | sort_by(-.b) | .[:20][]
  | [(.b / pow(2;40) * 100 | round / 100), .owner, .bucket] | @tsv'
```

`bucket stats` reads every bucket index, so it can take a while.

**Owners are RGW users.** RGW creates one user per Keystone project, the first time the project uses the object store. Its uid is `<project_id>$<project_id>`, or just `<project_id>` for users created before `rgw_keystone_implicit_tenants` was set. Always single-quote a uid with a `$` in it. Owners without a project id, such as backup accounts, are service users. To get a project's name:

```shell
openstack project show <project_id> -f value -c name
```

### 3. Set the default quota for new projects

```shell
ceph config get client.rgw rgw_user_default_quota_max_size
ceph config set client.rgw rgw_user_default_quota_max_size 1099511627776
```

This applies only to RGW users created after the change. Existing users keep their quota, or lack of one, so also do step 4.

### 4. Give every existing project a quota

**All projects**: use [rgw-quota-sync](https://github.com/ChameleonCloud/rgw-quota-sync). Its README covers the config file (a default plus per-project overrides) and the RGW user it needs.

1. Put every project from step 2 that is already over the default into `project_quotas`, with the quota you mean to give it. Otherwise the default applies to it and blocks its writes.
1. Run it without `--apply`. This dry run changes nothing and logs a `would change` line for each user it would set.
1. Run it with `--apply`.

It sets quotas only on Keystone project users, never on service users. It overwrites every enabled quota that differs from its config, including ones set by hand.

**One project**:

```shell
radosgw-admin quota set --quota-scope=user --uid='<project_id>$<project_id>' --max-size=1099511627776
radosgw-admin quota enable --quota-scope=user --uid='<project_id>$<project_id>'
```

### Check

```shell
radosgw-admin user info --uid='<project_id>$<project_id>' | jq .user_quota
```

`user_quota` should show `"enabled": true` and the `max_size` you set. Once a project is over its quota, uploads fail with `QuotaExceeded`. RGW caches usage, so a project can write past its quota for a while before uploads start failing.
