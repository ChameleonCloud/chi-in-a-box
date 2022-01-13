It is possible to configure CHI-in-a-Box to support bare metal provisioning on both x86- and ARM-based bare metal hardware. There are a few steps, namely configuring support for iPXE, which when combined with UEFI boot can provide different EFI images to the pre-boot environment depending on the target host architecture.

The following assumes your Site Configuration is stored at `$site_config`.

## Configuration changes

**`$site_config/defaults.yml`**:
```yaml
# When set to 'yes', a new ipxe server container is deployed on the 
# Ironic conductor node(s).
enable_ironic_ipxe: yes
```

You must additionally provide a custom ironic.conf file that enables the iPXE plugin:

**`$site_config/node_custom_config/ironic.conf`**:
```ini
[DEFAULT]
enabled_boot_interfaces = ipxe,pxe

[pxe]
ipxe_bootfile_name_by_arch = aarch64:aarch64/snponly.efi
```

## Apply changes

```shell
./cc-ansible --site $site_config upgrade --tags ironic
```

## Post-config

1. Copy the iPXE binary from the [v2021-11.01 CHI-in-a-Box release](https://github.com/ChameleonCloud/chi-in-a-box/releases/tag/v2021-11.01). You must deploy the EFI images to **all** Ironic conductor nodes (usually there is only one.) The Ironic conductor must already be running for this to succeed because it uses a `docker cp`.

```shell
tar xf $ipxe_tarball aarch64/snponly.efi
docker cp aarch64/. ironic_conductor/tftpboot/aarch64/
```

2. Upload the IPA kernel and ramdisk images from the [v2021-11.01 CHI-in-a-Box release](https://github.com/ChameleonCloud/chi-in-a-box/releases/tag/v2021-11.01) to your site:

```shell
openstack image create --file ironic-python-agent-aarch64.initramfs ironic-python-agent-aarch64.initramfs
# Note the UUID of the image, it is used as $ramdisk_uuid later

openstack image create --file ironic-python-agent-aarch64.kernel ironic-python-agent-aarch64.kernel
# Note the UUID of the image, it is used as $kernel_uuid later
```

3. Configure your ARM nodes to deploy with the ARM64-compiled IPA image, and also set the architecture on the node, which will help iPXE understand it is an ARM node at boot time.

> ⚠️ Requires `python-doniclient>=0.4.0`

```shell
openstack hardware set --architecture aarch64 --deploy_kernel $kernel_uuid --deploy_ramdisk $ramdisk_uuid $node
```

## Verification

You should now be able to reserve and provision an ARM node in your environment in addition to any existing x86 nodes, which should remain operational.