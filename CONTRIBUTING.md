# Contributing to CHI-in-a-box

Thank you! Read on.

## Code of Conduct

This project and everyone participating in it is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).

## I don't want to read this whole thing I just have a question!!!

> Please don't file an issue just to ask a question. You'll get faster results with one of the folowing:

We have an official message board where the community can chime in.
* [Github Discussions for CHI-in-a-box Operators](https://github.com/ChameleonCloud/chi-in-a-box/discussions)
* [Chameleon Helpdesk](https://chameleoncloud.org/user/help/ticket/new/)
* [Chameleon user facing documentation](https://chameleoncloud.readthedocs.io/en/latest/contents.html)
* [Upstream Kolla-Ansible documentation](https://docs.openstack.org/kolla-ansible/train/)


## What should I know in order to get started?

CHI-in-a-box is a packaging of Openstack, using heavy customization and templating via Ansible.
At a minimum, you should be familiar with the Linux commandline, and some basics of system administration. Knowledge of the general architecture of OpenStack will make your life much easier.

While our goal is ease of use and "Operator Ergonomics", this is fundamentally a complex system with many features, so be prepared to do a lot of learning if you're new to the concepts.

## How can I Contibute?

In rough order from least to most involved:

### Join the [discussions](https://github.com/ChameleonCloud/chi-in-a-box/discussions)!
Even if you don't contribute code, participating in the community, asking questions, and responding to others is enormously helpful. This helps us gauge interest in new features, and makes it possible to discover common issues that others have encountered.

### Reporting Bugs

If you encounter issues, please ask on the discussion forum first. We may ask you to file a bug in order to track the details better. That said, if anything is unclear, or you don't know where to go next, we consider this a bug in the documentation, and worthy of fixing.

When you do file an issue, please include:
- What you're trying to accomplish (overall goal)
- Any specific error messages
- What OS you're deploying on

### Suggesting Enhancements

Openstack has many features, and it's impossible for us to robustly support everything. Please post on the discussion forum about what you'd like to accomplish, and what features are missing that would make it possible / easier.

### Local Development

Local development depends on having a running Chi-in-a-box site. You can follow the Quickstart guide to bring one up on your own hardware, or, if you have a Chameleon account already, use our [Trovi Artifact](https://chameleoncloud.org/experiment/share/35) to run a development node on top of another Chameleon site.

### Pull Requests

Submitting a pull request will trigger our CI, including some basic linting, as well as sanity checks around deployment use-cases.
Please be clear about the intended deployment scenario, as we'll need to ensure it doesn't break anything for existing deployments.

