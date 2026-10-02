# Chameleon tools

Chameleon's own services and periodic tasks run as containers on the `control` node. CI in each source repo builds the image. chi-in-a-box pins the tag that sites deploy, in `kolla/defaults.yml`:

| Image | Source repo | Tag variable | Used by | Playbook |
|---|---|---|---|---|
| `ghcr.io/chameleoncloud/hammers` | [hammers](https://github.com/ChameleonCloud/hammers) | `chameleon_hammers_tag` | [hammers](hammers/README.md) (v1) | `playbooks/hammers.yml` |
| `ghcr.io/chameleoncloud/chameleon_site_tools` | [hammers-v2](https://github.com/ChameleonCloud/hammers-v2) | `chameleon_site_tools_tag` | [hammers](hammers/README.md) (v2), [image tools](image-tools.md), [periodic inspector](periodic-inspector.md), [reference repo](reference-repo.md) | `playbooks/hammers.yml`, `playbooks/chameleon_image_tools.yml`, `playbooks/chameleon_periodic_inspector.yml`, `playbooks/chameleon_reference_repo.yml` |
| `ghcr.io/chameleoncloud/chameleon-vendordata-service` | [chameleon-vendordata](https://github.com/ChameleonCloud/chameleon-vendordata) | `chameleon_vendordata_tag` | vendordata service | `playbooks/vendordata.yml` |

Each tag variable sits next to an `_image` variable (the image name) and an `_image_full` variable (image and tag combined). The roles read `_image_full`.

## Updating a tool at a site

1. Release a new version in the source repo, following its README: [hammers](https://github.com/ChameleonCloud/hammers#building-and-deploying), [hammers-v2](https://github.com/ChameleonCloud/hammers-v2#building-and-deploying), [chameleon-vendordata](https://github.com/ChameleonCloud/chameleon-vendordata#building-and-deploying). A release pushes a `vX.Y` image tag.
2. Set the tag variable in `kolla/defaults.yml` to the new version. Open a PR against each release branch that sites deploy from.
3. On the site's deploy host, pull chi-in-a-box. Then run post-deploy, which runs all the playbooks above:
   ```shell
   ./cc-ansible --site /opt/site-config post-deploy
   ```
   Or run only the playbooks for the image that changed:
   ```shell
   ./cc-ansible --site /opt/site-config --playbook playbooks/vendordata.yml
   ```

A site switches to the new version when a playbook rewrites its timers and services to use the new tag. Until then they keep running the old version. Most of these playbooks also pull the new image. `playbooks/hammers.yml` only pulls the v1 hammers image, so after a site tools bump, `docker run` pulls the new image the first time a v2 hammer runs.

Re-pushing an image under a tag a site already uses has no effect until something pulls that tag again. Release under a new tag instead.

To run a different version at a single site, set the tag variable in that site's `defaults.yml`. One example is an unreleased `sha-<short commit>` build on a dev site.
