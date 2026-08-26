# GitHub Actions Guide

This note explains the checks in `.github/workflows/test.yml` in practical terms.

## What GitHub Actions does

GitHub Actions runs commands on a temporary computer hosted by GitHub. Every workflow run starts from a clean checkout, installs what the project needs, runs the checks, and reports success or failure on the commit or pull request.

## Workflow settings

### `on`

```yaml
on:
  push:
  pull_request:
```

The workflow runs after code is pushed and when a pull request is opened or updated. Testing pull requests helps catch problems before they are merged.

### `permissions`

```yaml
permissions:
  contents: read
```

The workflow only needs to read the repository. Restricting permissions reduces what a workflow could do if one of its commands or dependencies were compromised.

### `concurrency`

```yaml
concurrency:
  group: test-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

`${{ ... }}` is a GitHub Actions expression. This creates a group for runs of the same workflow and branch. If several commits are pushed quickly, GitHub cancels an older run when a newer run replaces it, saving time and runner capacity.

## The test job

```yaml
python-version: "3.12"
```

The test workflow uses one current Python version to keep CI quick and dependable while the project is still developing. More versions can be added later after the project has a formal compatibility policy.

`runs-on: ubuntu-latest` selects a temporary Linux runner. The project can still be developed on Windows; this workflow checks the most common server environment.

## Actions versus shell commands

Steps using `uses` call reusable actions published for GitHub Actions:

- `actions/checkout@v4` downloads the repository onto the temporary runner.
- `actions/setup-python@v5` installs and selects the matrix Python version.

Steps using `run` execute normal shell commands on that runner. For example, `python -m pip` runs pip through the selected Python interpreter, which avoids accidentally using a different Python installation.

## Dependency and browser setup

```yaml
cache: pip
cache-dependency-path: requirements.txt
```

`setup-python` caches downloaded pip packages. The cache is refreshed when `requirements.txt` changes, which makes later workflow runs faster without changing which versions are installed. The current workflow installs the Playwright Python package, but does not download Chromium because its checks do not open a browser. A browser can be added when a real browser test is ready.

## Checks performed

- `python -m compileall` parses project scripts without running them. This catches syntax errors.
- The import check confirms that `test.nkiri` and `test.main` are connected correctly and that their expected public names exist.
- `python pom.py --help` confirms the CLI can start and register its commands.
- `python pom.py generate ...` exercises the real generator using `pom.config.json`.
- Compiling and importing the generated file confirms that the output is valid Python and exposes the expected `Thenkiri` class.

The generated `ci_generated.py` file is temporary CI output. It exists only during the job and is not committed.

## Why `python -m test.main` is not run here

`test/main.py` visits the live NKIRI website and interacts with external download links. Running that automatically on every push would make CI depend on a third-party website, network timing, advertisements, and content that the project does not control. It could also trigger actions that are inappropriate for an automated build.

The workflow therefore tests the code structure and generator deterministically. Run `python -m test.main` manually when you are authorized to access the site and want to perform the live test.

## The Pylint workflow

The separate Pylint workflow runs on Python 3.12 and reports code-quality findings. Its command ends with `|| true`, which means Pylint findings are visible in the log but do not block a push or pull request. This is a deliberate temporary choice for an early project: once the codebase has a Pylint policy, remove `|| true` and fix the reported findings incrementally.

## Reading the result

- A green check means the test and lint jobs completed successfully.
- A red check means at least one step failed. Open the workflow run and select the failed job to see the command output.
- A failure during dependency installation usually points to a package or Python-version compatibility issue.
- Pylint messages are advisory for now; a failed test step is the result that blocks the workflow.