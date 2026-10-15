# Ceph RGW Quotas

**Task**: make sure new projects get a default object store (Ceph RGW) quota, every existing project has a quota, and a global quota backs them up, without blocking writes for any project that already uses more than the default.

**Why**: without quotas, one project can fill the RGW data pool. Once its OSDs reach the full ratio, writes stop for every project, not just the one that filled it.

Sizes are in bytes: 1 TiB is `1099511627776`, and `-1` means unlimited. `radosgw-admin --max-size` also accepts `1T` for 1 TiB. `ceph config set` reads `1T` as 10^12 bytes, so give `ceph config set` plain bytes.

Docs:

- [Quota management](https://docs.ceph.com/en/reef/radosgw/admin/#quota-management) in the Ceph Reef admin guide

## Get a shell

Run the `ceph` and `radosgw-admin` commands on a Ceph admin host, in `cephadm shell` or on any host with the Ceph CLI and the admin keyring. Run the `openstack` commands with admin credentials for the site (for example `admin-openrc.sh`).

## 1. Find out the current state

How much space is there, what quotas already exist, and what are the biggest users.

Docs:

- [ceph config](https://docs.ceph.com/en/reef/rados/configuration/ceph-conf/#commands)
- [rgw_user_default_quota_max_size](https://docs.ceph.com/en/reef/radosgw/config-ref/#confval-rgw_user_default_quota_max_size)
- [global quotas](https://docs.ceph.com/en/reef/radosgw/admin/#reading-writing-global-quotas)
- [radosgw-admin](https://docs.ceph.com/en/reef/man/8/radosgw-admin/)
- [Keystone user naming](https://docs.ceph.com/en/reef/radosgw/multitenancy/#swift-with-keystone)

**Is there a default for new projects?** `-1` means there is none:

```shell
ceph config get client.rgw rgw_user_default_quota_max_size
```

**Is there a global quota?** Look at the user quota section (`enabled`, `max_size`):

```shell
radosgw-admin global quota get
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

## 2. Protect the projects already over the default

Docs:

- [rgw-quota-sync config](https://github.com/ChameleonCloud/rgw-quota-sync#config)

For each project from step 1 that uses more than the default, add an override to `project_quotas` in the rgw-quota-sync config, set above its current usage. Its writes keep working. Whether to bring it down later is a separate decision, made with the project.

Keys under `project_quotas` are Keystone project ids, without the `$` part.

Example, with a planned default of 1 TiB. Step 1 shows five projects and one service user over 1 TiB:

```text
170.16  <project_a>$<project_a>
9.95    <project_b>$<project_b>
9.88    <backup_user>
2.26    <project_c>$<project_c>
1.74    <project_d>$<project_d>
1.55    <project_e>$<project_e>
0.98    <project_f>$<project_f>
```

The five projects get overrides above their usage. `<backup_user>` is a service user, which rgw-quota-sync never changes, so it needs none. `<project_f>` is under the default and needs none. The config, with the endpoint and keys left out:

```yaml
max_size: 1099511627776           # default: 1 TiB
max_objects: -1
project_quotas:
  "<project_a>":
    max_size: 197912092999680     # 180 TiB, uses 170.16
  "<project_b>":
    max_size: 16492674416640      # 15 TiB, uses 9.95
  "<project_c>":
    max_size: 3298534883328       # 3 TiB, uses 2.26
  "<project_d>":
    max_size: 2199023255552       # 2 TiB, uses 1.74
  "<project_e>":
    max_size: 2199023255552       # 2 TiB, uses 1.55
```

## 3. Set the default for new projects

Docs:

- [Default quotas](https://docs.ceph.com/en/reef/radosgw/admin/#default-quotas)
- [rgw_user_default_quota_max_size](https://docs.ceph.com/en/reef/radosgw/config-ref/#confval-rgw_user_default_quota_max_size)

Use the same value as `max_size`, the per-project default, in the rgw-quota-sync config. If they differ, rgw-quota-sync changes every new project's quota to its own default the next time it runs.

```shell
ceph config set client.rgw rgw_user_default_quota_max_size 1099511627776
```

This applies only to RGW users created after the change, so existing projects still need step 4.

## 4. Give every existing project a quota

Docs:

- [rgw-quota-sync usage](https://github.com/ChameleonCloud/rgw-quota-sync#usage)
- [Set user quota](https://docs.ceph.com/en/reef/radosgw/admin/#set-user-quota)
- [Enabling and disabling user quota](https://docs.ceph.com/en/reef/radosgw/admin/#enabling-and-disabling-user-quota)

1. Run rgw-quota-sync without `--apply` again. Check that no `would change` line sets a quota below a project's usage from step 1.
1. Run it with `--apply`.

It sets quotas only on Keystone project users, never on service users. It overwrites every enabled quota that differs from its config, including ones set by hand, so put any quota you want to keep into `project_quotas` first.

To set one project by hand instead:

```shell
radosgw-admin quota set --quota-scope=user --uid='<project_id>$<project_id>' --max-size=1099511627776
radosgw-admin quota enable --quota-scope=user --uid='<project_id>$<project_id>'
```

## 5. Set a global quota as a backstop

Docs:

- [Reading / writing global quotas](https://docs.ceph.com/en/reef/radosgw/admin/#reading-writing-global-quotas)
- [RGW service with cephadm](https://docs.ceph.com/en/reef/cephadm/services/rgw/#rgw-service)

The global user quota applies to every RGW user without an enabled quota of its own. After step 4 that means service users, and any project the steps above missed. Set it above the largest service user from step 1, so it blocks none of them today. In the example, `<backup_user>` uses 9.88 TiB, so 15 TiB:

```shell
radosgw-admin global quota set --quota-scope=user --max-size=15T
radosgw-admin global quota enable --quota-scope=user
```

The global quota takes effect only once RGW loads it:

- If `radosgw-admin realm list` shows a realm, run `radosgw-admin period update --commit`.
- If there is no realm, restart every RGW daemon. With cephadm, `ceph orch ls rgw` shows the service, then `ceph orch restart rgw.<service>`.

## Check

Docs:

- [Get quota settings](https://docs.ceph.com/en/reef/radosgw/admin/#get-quota-settings)
- [Quota cache](https://docs.ceph.com/en/reef/radosgw/admin/#quota-cache)

Run rgw-quota-sync without `--apply`. Its last line should be `all Keystone users have their configured quota`. `radosgw-admin global quota get` should show the user quota enabled, with the backstop size. For one project:

```shell
radosgw-admin user info --uid='<project_id>$<project_id>' | jq .user_quota
```

`user_quota` should show `"enabled": true` and the `max_size` you set. Once a project is over its quota, uploads fail with `QuotaExceeded`. RGW caches usage, so a project can write past its quota for a while before uploads start failing.
