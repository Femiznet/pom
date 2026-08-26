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

## Jobs and the Python matrix

```yaml
strategy:
  fail-fast: false
  matrix:
    python-version: ["3.9", "3.10", "3.11", "3.12"]
```

The matrix runs the same job once for each Python version. `fail-fast: false` lets all versions finish so a failure on one version does not hide failures on the others.

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

`setup-python` caches downloaded pip packages. The cache is refreshed when `requirements.txt` changes, which makes later workflow runs faster without changing which versions are installed.

Playwright has two parts: the Python package and browser binaries. `pip install -r requirements.txt` installs the package, while:

```bash
python -m playwright install --with-deps chromium
```

installs Chromium and the Linux libraries it needs. The workflow does this even though the deterministic checks do not visit a website, so future browser-based tests have the required environment.

## Checks performed

- `python -m pip check` detects incompatible installed package requirements.
- `python -m py_compile ...` parses every project script without running it. This catches syntax errors.
- The import check confirms that `test.nkiri` and `test.main` are connected correctly and that their expected public names exist.
- `python pom.py --help` confirms the CLI can start and register its commands.
- `python pom.py generate ...` exercises the real generator using `pom.config.json`.
- Compiling and importing the generated file confirms that the output is valid Python and exposes the expected `Thenkiri` class.

The generated `ci_generated.py` file is temporary CI output. It exists only during the job and is not committed.

## Why `python -m test.main` is not run here

`test/main.py` visits the live NKIRI website and interacts with external download links. Running that automatically on every push would make CI depend on a third-party website, network timing, advertisements, and content that the project does not control. It could also trigger actions that are inappropriate for an automated build.

The workflow therefore tests the code structure and generator deterministically. Run `python -m test.main` manually when you are authorized to access the site and want to perform the live test.

## Reading the result

- A green check means every matrix job completed successfully.
- A red check means at least one step failed. Open the workflow run and select the failed Python version to see the command output.
- A failure on only one Python version usually indicates a compatibility issue specific to that version.
- A failure during browser installation usually indicates a Playwright or runner-environment issue, rather than a problem with the page-object code.