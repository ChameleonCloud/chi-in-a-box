## What is this?

CHI-in-a-box is a packaging of the implementation of the core services that together constitute the [Chameleon](https://www.chameleoncloud.org/) testbed for experimental Computer Science research. These services allow Chameleon users to discover information about Chameleon resources, allocate those resources for present and future use, configure them in various ways, and monitor various types of metrics.

While a large part of CHI (**CH**\ ameleon **I**\ nfrastructure) is based on an open source project (OpenStack), and all the extensions we made are likewise open source, without proper packaging there was no clear recipe on how to combine them and configure a testbed of this type. CHI-in-a-box is composed of the following three components:

  1. open source dependencies supported by external projects (e.g., OpenStack and Grid’5000)
  2. open source extensions made by the Chameleon team, both ones that are scheduled to be integrated into the original project (but have not been yet) and ones that are specific to the testbed
  3. new code written by the team released under the Apache License 2.0.

## Who is it for?

We have identified demand for three types of scenarios in which users would like to use a packaging of Chameleon infrastructure:

  - **Chameleon Associate**: In this scenario a provider wants to add resources to the Chameleon testbed such that they are discoverable and available to all Chameleon users while retaining their own project identity (via branding, usage reports, some of the policies, etc.). This type of provider will provide system administration of their resources (hardware configuration and operation as well as CHI administration with the support of the Chameleon team) and use the Chameleon user services (user/project management, etc.), user portal, resource discovery, and appliance catalog. All user support will be provided by the Chameleon team.

  - **Chameleon Part-time Associate**: This scenario is similar to the Chameleon Associate but while the resources are available to the testbed users most of the time, the provider anticipates that they may want to take them offline for extended periods of time for other uses. In this scenario Chameleon support extends only to the time resources are available to the testbed.

  - **Independent Testbed**: In this scenario a provider wants to create a testbed that is in every way separate from Chameleon. This type of provider will use CHI for the core testbed services only and operate their user services (i.e., manage their own user accounts and/or projects, help desk, mailing lists and other communication channels, etc.), user portal, resource discovery, and appliance catalog (some of those services can in principle be left out at the cost of providing a less friendly interface to users). This scenario will be supported on a best effort basis only.

## How do I get started?

Please [submit a Help Desk ticket](https://www.chameleoncloud.org/user/help/ticket/new/) if you are interested in running a Chameleon testbed, whether it be as an independent site or as an associate site.

If you want to learn more about how the process works, please read our [Installation guide](./Installation-guide).