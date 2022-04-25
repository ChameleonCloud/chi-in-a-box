The sites can use the provided Chameleon image tools to deploy the Chameleon-supported images and set up periodic tasks for automatic image deployment and/or cleanup.

To learn more about images in Chameleon, please read our [user documentation](https://chameleoncloud.readthedocs.io/en/latest/technical/images.html).

## Configuration

The image tools are by default installed onto the `control` node in the site configuration Ansible inventory.
The configuration steps are included in the `post-deploy`. You can also manually configure the image tools by running the `chameleon_image_tools` playbook.

```shell
cc-ansible --playbook playbooks/chameleon_image_tools.yml
```

The configuration steps will pull the latest `chameleon_image_tools` docker image and prepare the configuration file that is required for using the tools.

## Deployer

The image deployer allows the sites to pull the latest Chameleon-supported images and deploy the images to the site.
The deployed Chameleon-supported images are owned by the site admin project and have the `public` visibility.

By default, the automatic deployment task is *disabled*. To enable the task, set `enable_image_deployer: yes` in the site `defaults.yml`.
Then, run the `post-deploy` or run the `chameleon_image_tools` playbook.
The automatic deployment task runs daily to check if there are new (version of) Chameleon-supported images that have been released and deploy all new images to the site.
You can check the installed automatic deployment task via the systemd [timers](https://wiki.archlinux.org/index.php/Systemd/Timers).

```shell
systemctl list-timers 'image_deploy'
```

You can also deploy the images manually by running the following commands:

```shell
# to deploy a specific image
docker run --rm --net=host -v "/etc/chameleon_image_tools/site.yaml:/etc/chameleon_image_tools/site.yaml" \
docker.chameleoncloud.org/chameleon_image_tools:latest deploy \
--site-yaml /etc/chameleon_image_tools/site.yaml \
--image <image_id>

# to deploy by image properties
docker run --rm --net=host -v "/etc/chameleon_image_tools/site.yaml:/etc/chameleon_image_tools/site.yaml" \
docker.chameleoncloud.org/chameleon_image_tools:latest deploy \
--site-yaml /etc/chameleon_image_tools/site.yaml \
--latest <distro>,<release>,<variant>
```

## Cleaner

To avoid accumulation of the older version and deprecated Chameleon-supported images in your site, we implement an image cleaning tool that cleans up images.
The tool will:
- Check and skip the images that are currently used by any instance.
- Hide images that are 12 months or older (i.e. set visibility of the images to `private`). You can also tune this number by overwriting `hide_image_age_in_month` in the site `defaults.yml`.
- Delete images that are 18 months or older. You can also tune this number by overwriting `delete_image_age_in_month` in the site `defaults.yml`.

By default, the automatic cleaning task is *disabled*. To enable the task, set `enable_image_cleaner: yes` in the site `defaults.yml`.
Then, run the `post-deploy` or run the `chameleon_image_tools` playbook.
The automatic cleaning task runs daily to hide or delete the older version and deprecated Chameleon-supported images.
You can check the installed automatic cleaning task via the systemd [timers](https://wiki.archlinux.org/index.php/Systemd/Timers).

```shell
systemctl list-timers 'image_clean'
```

You can also clean the images manually by running the following command:

```shell
docker run --rm --net=host -v "/etc/chameleon_image_tools/site.yaml:/etc/chameleon_image_tools/site.yaml" \
docker.chameleoncloud.org/chameleon_image_tools:latest clean \
--site-yaml /etc/chameleon_image_tools/site.yaml
```

To perform a dry-run, add `--dry-run` flag to the above command to only print without actual hiding and deleting.
