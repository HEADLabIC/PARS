# Contributing to PARS

Thank you for contributing to PARS.

All changes to the repository must be made through a pull request. The default branch, `main`, is protected and changes should not be pushed or merged directly without review.

## Recommended workflow

1. Pull the latest version of `main`.
2. Create a new branch for the change.
3. Make and test the change locally.
4. Commit the change with a clear commit message.
5. Push the branch to GitHub.
6. Open a pull request into `main`.
7. Link the pull request to the relevant issue or milestone.
8. Wait for review and approval before merging.

Example:

```
git checkout main
git pull
git checkout -b update-installation-guide
```

Use short and descriptive branch names, for example:

```
fix-installation-error
improve-usage-docs
add-output-example
update-mesh-processing
```

## Pull request requirements

Each pull request should:

* explain what was changed and why;
* remain focused on one issue or task where possible;
* link to the relevant GitHub issue or milestone;
* include any testing or validation performed;
* update documentation when behaviour or usage changes;
* avoid unrelated formatting or file changes;
* pass any required automated checks;
* be reviewed before it is merged into `main`.

Do not merge your own pull request unless this has been agreed with the repository maintainers.

## Reviewing pull requests

Reviewers should check that:

* the change addresses the stated issue;
* the code or documentation is clear and maintainable;
* commands, file paths and links are correct;
* no generated, confidential or restricted files are included;
* documentation builds successfully where relevant;
* the change does not unintentionally alter unrelated parts of the pipeline;
* any required approvals and automated checks have completed.

Requested changes should be resolved before approval.

## Documentation changes

Editable documentation is stored in:

```
docs/
```

Site configuration and navigation are defined in:

```
mkdocs.yml
```

The documentation homepage is:

```
docs/index.md
```

Preview documentation changes locally with:

```
mkdocs serve
```

Test the documentation build with:

```
mkdocs build --strict
```

Do not edit the `gh-pages` branch directly. It contains generated files and is updated automatically by GitHub Actions after approved changes are merged into `main`.

## Good practice

When contributing:

* start from the latest `main`;
* keep branches short-lived;
* make small, focused commits;
* use meaningful commit messages;
* avoid committing generated files;
* do not commit passwords, tokens, private keys or sensitive data;
* document new dependencies or setup requirements;
* preserve attribution and licensing information;
* discuss major structural, licensing or branding changes in an issue before implementation.

## After merging

After a pull request is merged:

* confirm that the GitHub Actions checks complete successfully;
* confirm that the documentation deployment succeeds if documentation was changed;
* check the public documentation site where relevant;
* delete the merged branch if it is no longer needed.
