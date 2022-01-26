# Chameleon Identity Federation

### **What is Chameleon Identity Federation?**

Federated identity allows a user to link existing identities and attributes across multiple distinct systems. In practice, this allows an operator to configure a system to allow access to users from other systems. Chameleon Identity Federation allows existing Chameleon users access to the configured associate site. This allows the site operator to leverage all of the infrastructure that the Chameleon project has built for handling user, project, and allocation management through the [Chameleon Portal](https://chameleoncloud.org).

### Requirements

* IDP Client Credential for federation with Chameleon Keycloak (Request from Chameleon Core team)

### **Enabling Chameleon Identity Federation**

Before an associate site can enable federation, that site must obtain a client identifier from Chameleon administrators.

* Open a ticket in the [help desk](https://www.chameleoncloud.org/user/help/) explaining some details of the site institution and hardware. Chameleon staff will issue a Client ID for the site, which will need to be entered into the site configuration.
* The Client ID is configured in `defaults.yml` as `keystone_idp_client_id`. To satisfy requirements of the deployment tool, the encrypted passwords file should set `keystone_idp_client_secret` should to "public".
* Use `cc-ansible reconfigure` to apply the changes and generate a new keystone domain called "chameleon". At this point, federated login should now be available on the site.
* Add the "admin" role and operator user.
  *   Find and take note of the desired user and group UUIDs. Be sure to query the user and project entities in the "chameleon" domain.

      ```
      openstack user show --domain chameleon <username>
      openstack project show --domain chameleon openstack
      ```
  *   Make the role assignment

      ```
      openstack role add --user <user_uuid> --project <project_uudi> admin
      ```

###
