# Ceph RGW Quotas

**Summary**: how to measure object store (Ceph RGW) usage, find the largest projects and buckets, and set per-project quotas with `radosgw-admin` and `ceph config`. Written for Ceph Reef.

**Consequences**: without quotas, a single project can fill the RGW data pool. Once its OSDs reach the full ratio, writes stop for every project, not just the one that filled it.

Sizes are in bytes. The example used below, 5 TiB, is `5497558138880`. `radosgw-admin --max-size` also accepts suffixes (`5T` or `5Ti` both mean 5 TiB). `ceph config set` reads `5T` as 5x10^12 bytes, so give `ceph config set` plain bytes. `-1` means unlimited.

#### Get a shell

chi-in-a-box configures the Keystone side of the RGW integration: the object store endpoints, HAProxy (`ceph_rgw_port`, 7480) and the `ceph` Keystone service user (`swift_keystone_user`, `ceph_rgw_keystone_password`), in `kolla/defaults.yml` and `passwords.yml`. The Ceph cluster itself is managed outside chi-in-a-box, so run everything below on a Ceph admin host:

```
cephadm shell             # on a cephadm-managed mon or _admin host
ceph -s                   # must show the cluster
radosgw-admin realm list  # must answer; also tells you if a realm exists (step 3)
```

Without cephadm, use any host that has the Ceph CLI, `/etc/ceph/ceph.conf` and the admin keyring (`/etc/ceph/ceph.client.admin.keyring`). If `jq` is missing inside `cephadm shell`, run commands from the host instead: `cephadm shell -- radosgw-admin ... | jq ...`.

The `openstack` commands run from wherever you normally use admin credentials (`admin-openrc.sh`).

#### 1. Measure total RGW usage

```
ceph df detail
ceph osd dump | grep full_ratio
```

In `ceph df detail`, find the RGW data pool (usually `<zone>.rgw.buckets.data`, e.g. `default.rgw.buckets.data`; list pools with `ceph osd pool ls | grep rgw`). Check `STORED`, `%USED` and `MAX AVAIL`. `MAX AVAIL` estimates how much more the pool can take. It depends on replication or EC, the fullest OSDs and the full ratio. `ceph health detail` shows `OSD_NEARFULL` once an OSD passes `nearfull_ratio`.

#### 2. Find the largest buckets and projects

Top 20 buckets (TiB, owner, bucket):

```
radosgw-admin bucket stats | jq -r '
  map({bucket, owner, b: (.usage["rgw.main"].size_actual // 0)})
  | sort_by(-.b) | .[:20][]
  | [(.b / pow(2;40) * 100 | round / 100), .owner, .bucket] | @tsv'
```

Top 20 owners (projects), with all their buckets added up:

```
radosgw-admin bucket stats | jq -r '
  group_by(.owner)
  | map({owner: .[0].owner, b: (map(.usage["rgw.main"].size_actual // 0) | add)})
  | sort_by(-.b) | .[:20][]
  | [(.b / pow(2;40) * 100 | round / 100), .owner] | @tsv'
```

`bucket stats` reads every bucket index, so it can be slow on a large site. For one owner:

```
radosgw-admin user stats --uid='<project_id>$<project_id>' --sync-stats
```

**From an RGW uid to a project**: RGW creates one user per Keystone project on the project's first object store request. Its uid is `<project_id>$<project_id>` (`<tenant>$<user>`, from `rgw_keystone_implicit_tenants`). Users created before that option was set are just `<project_id>`. Always single-quote a uid that has a `$` in it. To get the project name:

```
openstack project show <project_id> -f value -c name
openstack project show <project_name> -f value -c id   # the other way
```

#### 3. Show or set the global user quota

```
radosgw-admin global quota get
radosgw-admin global quota set --quota-scope=user --max-size=5497558138880
radosgw-admin global quota enable --quota-scope=user
```

The global quota is stored in the period config, so it does not take effect by itself:

- If `radosgw-admin realm list` shows a realm, run `radosgw-admin period update --commit`.
- If there is no realm, restart every RGW daemon: `ceph orch ls rgw` to find the service, then `ceph orch restart rgw.<service>`. Without cephadm, restart the radosgw service on each RGW host.

The global quota applies to every user without an enabled user quota, including service users (image store, backups). An enabled per-user quota replaces the global one. To exempt a user, give it its own unlimited quota (step 5 with `--max-size=-1`).

#### 4. Show or set the default quota for new projects

```
ceph config get client.rgw rgw_user_default_quota_max_size
ceph config set client.rgw rgw_user_default_quota_max_size 5497558138880
ceph config set client.rgw rgw_user_default_quota_max_objects -1
```

These settings only apply to RGW users created after the change, which means projects whose first object store request comes later. Each such user gets an enabled user quota with these values. Existing users are not changed (see step 5).

No restart is needed. RGW reads these settings each time it creates a user, and they can be changed at runtime. `client.rgw` covers every daemon named `client.rgw.*`. To check the value a running daemon is using:

```
ceph orch ps --daemon_type rgw    # daemon names, e.g. rgw.<service>.<host>.<id>
ceph config show client.rgw.<service>.<host>.<id> rgw_user_default_quota_max_size
```

If the `SOURCE` column says `file`, the value comes from `ceph.conf` on the RGW host, which overrides `ceph config set`. Change it there and restart that RGW.

#### 5. Set quotas for existing projects (backfill)

One project:

```
UID='<project_id>$<project_id>'   # or '<project_id>' for old users
radosgw-admin quota set --quota-scope=user --uid="$UID" --max-size=5497558138880
radosgw-admin quota enable --quota-scope=user --uid="$UID"
radosgw-admin user info --uid="$UID" | jq '{type, user_quota}'
```

`user_quota` should show `"enabled": true` and the `max_size` you set. `type` is `keystone` for project users. To exempt a project, set `--max-size=-1` and enable it.

**Bulk backfill**: use [rgw-quota-sync](https://github.com/ChameleonCloud/rgw-quota-sync). Its README covers the config file (a default plus per-project overrides) and the RGW user it needs. Run it without `--apply` first. That dry run lists every `would change` and changes nothing. Then run it with `--apply`. Every enabled quota that differs from the config is overwritten, including ones set by hand above. Before applying, put any quota you want to keep into `project_quotas`. To exempt a project, give it `max_size: -1` (and `max_objects: -1`).

#### 6. Verify

When a user goes over quota, uploads fail with `QuotaExceeded`: HTTP 403 on S3 and HTTP 413 on Swift.

Enforcement can lag, because each RGW caches quota stats: bucket stats for `rgw_bucket_quota_ttl` (default 10 min), and user stats until `rgw_user_quota_bucket_sync_interval` (3 min) and `rgw_user_quota_sync_interval` (1 day) come around. So a project can go somewhat past its quota before writes stop. To force a stats sync:

```
radosgw-admin user stats --uid="$UID" --sync-stats
```

#### 7. Monitoring

Usage per project and bucket is exported by [radosgw_usage_exporter](https://github.com/ChameleonCloud/radosgw_usage_exporter). There is no central (Mimir) alert on RGW usage or missing quotas yet.
