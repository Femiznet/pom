# POM

A small Page Object Model generator for Playwright. Point it at a page, review the discovered selectors, and generate a typed Python page-object class.

## Requirements

- Python 3.9 or newer
- Chromium, installed through Playwright

## Installation

```bash
git clone https://github.com/Femiznet/pom
cd pom
python -m venv venv
```

Activate the virtual environment:

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

Install dependencies and the browser used for discovery:

```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

### 1. Discover page elements

```bash
python pom.py get https://example.com/login
```

This opens the URL in a headless Chromium browser and writes detected interactive elements to `pom.config.json`. The command checks for an existing file before overwriting it.

Use a different config path when needed:

```bash
python pom.py get https://example.com/login -o login.config.json
```

### 2. Review the config

Discovery is intentionally only a starting point. Remove unwanted selectors, rename page sections, or replace selectors that are not unique.

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

Each selector key must be a valid Python identifier because it becomes a typed locator attribute.

### 3. Generate the page object

```bash
python pom.py generate -o test/nkiri.py
```

For a custom config:

```bash
python pom.py generate --config login.config.json -o login_page.py
```

Without `-o`, generated Python is printed to standard output.

### 4. Use the generated class

The generated class starts Playwright, opens `baseUrl`, and binds each configured selector to a Playwright locator. Set `headless=True` for non-visual runs.

```python
from test.nkiri import Thenkiri

with Thenkiri(headless=True) as site:
  site.nkiri.search.fill("vincenzo")
  site.nkiri.search.press("Enter")

  site.nkiri.post_link2.first.click()
  site.nkiri.dwld_btn.click()

    # Use the underlying Playwright Page for advanced operations.
    print(site.page.url)
```

  ## TEST A FREE MOVIE DOWNLOADER SCRIPT WITH NKIRI

  The repository includes a test script that uses the generated `Thenkiri` page object to search for a movie and inspect its available download links. Run it from the project root:

  ```bash
  python -m test.main
  ```

  The script uses the search term `vincenzo`, visits matching results, checks each available link, and cancels captured download streams instead of saving files. Only use it with content and websites you are authorized to access.

## Commands

| Command | Description |
|---|---|
| `python pom.py get <url>` | Discover interactive elements and write a JSON config |
| `python pom.py generate` | Generate a Python page-object model from a JSON config |

Run `python pom.py --help` or `python pom.py <command> --help` for all options.

## How discovery works

`get` loads the page and inspects inputs, buttons, links, selects, and textareas. It prefers `id`, `name`, and `aria-label` attributes when building selectors, skips hidden inputs, and filters obvious noise. Review the generated config before using `generate`.

## Notes

- Generated page sections group locators by name; they do not automatically navigate to a section-specific URL.
- Add `pom.config.json` to `.gitignore` if it contains private URLs or selectors.
- The generated file imports `BasePom`, so run `python -m test.main` from the project root or otherwise keep the project root on the Python import path.
