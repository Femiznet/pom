# POM

POM is a small Python tool that turns a real web page into a Playwright Page Object Model.

> **Project status:** POM is still under active development. Errors and incomplete behavior are expected, so review generated output and report problems when you find them.

## What problem does it solve?

When you automate a website, you usually have to find selectors by hand and keep those selectors organized in Python. POM gives you a quicker starting point:

1. It opens a URL in Chromium and finds useful interactive elements.
2. It saves the findings in an editable JSON file.
3. It generates a typed Python class whose attributes are Playwright locators.

It does not magically understand a website or guarantee perfect selectors. The important middle step is reviewing the generated config before using it.

## Install

You need Python 3.9 or newer. From the project folder:

```bash
python -m venv venv
```

Activate the environment:

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

Install the Python packages and Chromium:

```bash
python -m pip install -r requirements.txt
playwright install chromium
```

## Your first Page Object

### 1. Discover a page

```bash
python pom.py get https://example.com/login
```

This creates `pom.config.json`. If that file already exists, POM asks before replacing it. Choose another output file when you want to keep the existing config:

```bash
python pom.py get https://example.com/login -o login.config.json
```

The browser runs headlessly, so no browser window is expected during discovery.

### 2. Review the JSON

Remove selectors you do not need, rename sections, and fix selectors that are not unique. A small config might look like this:

```json
{
  "baseUrl": "https://example.com",
  "pages": [
    {
      "name": "login",
      "selectors": {
        "username": "#username",
        "password": "#password",
        "submit": "button[type='submit']"
      }
    }
  ]
}
```

Every selector name becomes a Python attribute, so it must be a valid Python identifier such as `submit_button`, not `submit-button`.

### 3. Generate Python

```bash
python pom.py generate --config login.config.json -o login_page.py
```

For the default `pom.config.json`:

```bash
python pom.py generate -o page.py
```

Omit `-o` to print the generated code instead of writing a file.

### 4. Use the generated class

The generated class starts Playwright, opens `baseUrl`, and exposes each selector as a locator. `headless=False` (the default) shows the browser; use `headless=True` for an invisible run.

```python
from login_page import Example

with Example(headless=True) as site:
    site.login.username.fill("person@example.com")
    site.login.password.fill("a-password")
    site.login.submit.click()

    # The raw Playwright Page is available for anything else.
    print(site.page.url)
```

Run commands from the project root so imports such as `from base import BasePom` resolve correctly.

## Included NKIRI downloader test

The repository also contains `test/main.py`, a separate live-site script that demonstrates the generated NKIRI page object. It searches NKIRI for `vincenzo`, opens the matching result, visits its download links, and listens for download events.

Run it from the project root:

```bash
python -m test.main
```

Important details:

- This script visits a third-party website and needs a working internet connection.
- It uses the checked-in class in `test/nkiri.py`, which was generated from `pom.config.json`.
- It catches download events and calls `download.cancel()`. It is a stream-checking demonstration, not a script that saves movie files to disk.
- The site and its content can change, so the script may stop working when selectors or links change.
- Only access content and websites you are legally allowed to access. Follow the site’s terms and applicable laws.

To change the movie being searched, edit `search_term` in `test/main.py`, then run the command again.

## Undo and cleanup

The NKIRI script makes no permanent change to your computer: leaving the `with Thenkiri()` block closes the browser, and captured downloads are canceled. Stop a run with `Ctrl+C`; close any remaining browser window if your environment leaves one open.

To remove generated files created by your own experiments, delete them normally:

```bash
del login_page.py pom.config.json        # Windows
rm login_page.py pom.config.json        # macOS/Linux
```

Do not delete `pom.config.json` if you want to keep its selectors. To undo a regenerated tracked file and return it to the repository version, use your version-control tool, for example:

```bash
git restore test/nkiri.py pom.config.json
```

Only run that command when you are sure you do not need your local edits; it discards changes to those files.

## Command reference

| Command | Purpose |
|---|---|
| `python pom.py get <url>` | Discover interactive elements into a JSON config |
| `python pom.py get <url> -o <file>` | Discover into a named config file |
| `python pom.py generate` | Generate Python from `pom.config.json` |
| `python pom.py generate --config <file> -o <file>` | Generate Python from a chosen config |
| `python pom.py --help` | Show CLI help |

Discovery checks inputs, buttons, links, selects, and textareas. It prefers `id`, `name`, and `aria-label`, skips hidden inputs, and filters some obvious noise. Generated sections group locators; they do not automatically navigate to section-specific URLs.
