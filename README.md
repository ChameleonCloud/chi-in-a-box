# CHI-in-a-Box

CHI-in-a-Box packages the services behind the [Chameleon](https://www.chameleoncloud.org) testbed: bare metal reservation and provisioning built on OpenStack (Ironic, Blazar, Nova, Neutron, and more), plus Chameleon's own extensions and operator tooling. Use it to add resources to Chameleon as an associate site, or to run an independent testbed.

**Documentation:** <https://chi-in-a-box.readthedocs.io/>

- New here? Start with [What is CHI-in-a-Box?](https://chi-in-a-box.readthedocs.io/en/latest/) and [Before You Begin](https://chi-in-a-box.readthedocs.io/en/latest/before-you-begin/upstream-docs/).
- To try it on a single host, follow the [Evaluation Site](https://chi-in-a-box.readthedocs.io/en/latest/setup-guides/evaluation-site/) guide.
- To deploy on real hardware, follow [Production Baremetal](https://chi-in-a-box.readthedocs.io/en/latest/setup-guides/production-baremetal/), the default configuration for associate sites.
- The docs source lives in [`docs/`](docs/) and builds with [Zensical](https://zensical.org) (`pip install -r requirements-docs.txt && zensical serve`).

## Getting help

- Questions and discussion: [GitHub Discussions](https://github.com/ChameleonCloud/chi-in-a-box/discussions)
- Bugs: [GitHub Issues](https://github.com/ChameleonCloud/chi-in-a-box/issues)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

Apache License 2.0. See [LICENSE](LICENSE).
