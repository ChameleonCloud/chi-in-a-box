**Summary**: the Chameleon user portal is unreachable or experiencing errors.

**Consequences**: When the user portal is down, users will be unable log in anywhere due to portal hosting the Single-Sign On (SSO) implementation. Additionally, users will be unable to reach the user portal (chameleoncloud.org), view their allocations, request renewals, and view things like the appliance catalog.

### Possible causes

**Networking interruption**: the host institution network for the portal (TACC) might be down or unreachable from the outside. If this is the case, TACC should be notified and there's not much to be done. However, login to other sites can be restored by disabling SSO:

1. Edit the site configuration `globals.yml` to have `enable_horizon_chameleon_websso: no`
2. Reconfigure Horizon: `./cc-ansible reconfigure --tags horizon`