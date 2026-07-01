# PARS maintenance guide

This guide explains how to update and maintain the PARS repository and documentation site.

## Repository structure

* `README.md` — overview shown on the GitHub repository homepage
* `MAINTAINERS.md` — maintenance guidance
* `CITATION.cff` — citation metadata
* `mkdocs.yml` — documentation configuration, navigation and theme
* `docs/` — editable documentation pages
* `notebooks/` — workflow notebooks
* `src/` — source code supporting notebooks
* `.github/workflows/` — GitHub Actions workflows
* `gh-pages` branch — auto-generated documentation website

Do not edit the `gh-pages` branch directly.

## Making changes

For substantial changes:

1. Pull the latest version of `main`.
2. Create a new branch.
3. Make and test the changes.
4. Push the branch and write the commit message link to relevant issue.
5. Open a pull request.
6. Link the pull request to the relevant issue or milestone.

## Documentation

Editable documentation files are stored in:

```
docs/
```

The documentation homepage must be:

```
docs/index.md
```

Site navigation is defined under `nav:` in:

```
mkdocs.yml
```

When adding, renaming or removing a documentation page, update both the files under `docs/` and the `nav:` section in `mkdocs.yml`.

The documentation site is still under development, so new pages can be added gradually as content becomes available.

## Running the documentation locally

Create and activate a virtual environment:

```
python3 -m venv .venv
source .venv/bin/activate
```

Install the project and documentation dependencies:

```
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

Preview the site:

```
mkdocs serve
```

Test that it builds successfully:

```
mkdocs build --strict
```

Do not commit the generated `site/` directory.

## Publishing the documentation

A push to `main` triggers the documentation workflow in:

```
.github/workflows/docs.yml
```

The workflow builds the site and publishes it to the `gh-pages` branch.

The public documentation site is:

```
https://headlabic.github.io/PARS/
```

If deployment fails, check the relevant GitHub Actions run and identify the first failed step.

## Branding and content

The PARS documentation is intended for scientists and researchers.

When updating the site:

* use HEAD Lab and [Imperial College branding](https://brand.imperial.ac.uk/);
* keep installation and usage instructions practical and easy to follow;
* explain expected inputs, outputs and software dependencies clearly;
* acknowledge ReCoDE where its template or support has been reused.

## Licensing and third-party software

Do not change the repository licence without agreement from the project leads.

PARS may depend on third-party software with separate licence conditions. Make sure the documentation distinguishes between:

* the PARS software licence;
* third-party software licences;
* any commercial-use restrictions;
* files that cannot be redistributed.

## Sensitive information

Do not commit:

* passwords or personal access tokens;
* private keys;
* patient-identifiable data;
* confidential institutional information;
* restricted third-party software;
* unpublished data without permission.

If a credential is committed accidentally, revoke it immediately. Removing it in a later commit is not sufficient because it may remain in the Git history.
