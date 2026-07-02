# PARS

PARS is a pipeline for creating subject-specific finite-element brain models from MRI data.

## For users of PARS

For installation and usage instructions, please see the PARS documentation:

https://headlabic.github.io/PARS/

## Third-party software

PARS uses third-party software that is licensed separately from PARS.

In GitHub Codespaces, `.devcontainer/install_fsl.sh` automatically downloads
and runs Oxford's official FSL installer. FSL is not distributed under the
PARS BSD licence, and users are responsible for complying with the applicable
[FSL licence](https://fsl.fmrib.ox.ac.uk/fsl/docs/license.html).


## Repository structure

* `src/` — pipeline source code
* `docs/` — source files for the documentation website
* `notebooks/` — worked examples
* `tests/` — automated tests
* `utils/` — documentation and processing utilities
* `.github/workflows/` — continuous integration and documentation deployment
* `mkdocs.yml` — documentation site configuration

## Contributing

To contribute to PARS, please read [CONTRIBUTING.md](CONTRIBUTING.md) and follow the pull request workflow described there.

## Development and maintenance

See [MAINTAINERS.md](MAINTAINERS.md) for information on repository maintenance, documentation deployment and releases.

## License

This project is licensed under the [BSD-3-Clause license](LICENSE.md).
