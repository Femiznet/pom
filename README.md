# POM

Page Object Model generator for Playwright. Point it at a URL, get a typed Python class back.

## What it does

```bash
# discover elements on a page
python pom.py get https://example.com/login

# review and edit pom.config.json, then generate
python pom.py generate -o example.py
```

```python
# use it
from example import Example

# set headless = True for a background run
with Example(headless=False) as site:
    site.login.username.fill("chidi@gmail.com") # auto navigates to /login of the base url
    site.login.password.fill("1234")
    site.login.submit.click()
```

## Install

```bash
git clone https://github.com/Femiznet/pom
cd pom
python -m venv venv
venv\Scripts\activate # for windows or source venv/bin/activate for mac/linux 
pip install -r requirements.txt
playwright install chromium
```

## Commands

| Command | What it does |
|---|---|
| `pom get <url>` | Fetch a page and auto-detect elements into `pom.config.json` |
| `pom generate` | Generate a typed Python model from `pom.config.json` |

### Options

```bash
python pom.py get <url> -o custom.config.json   # save config to custom file
python pom.py generate --config custom.config.json -o model.py  # use custom config
```

## Config format

```json
{
  "baseUrl": "https://example.com",
  "pages": [
    {
      "name": "register",
      "selectors": {
        "username": "#username",
        "password": "#password",
        "submit": "button[type='submit']"
      }
    },

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

## How it works

pom get → opens a headless browser, fetches page → parses interactive elements → writes config
pom generate → reads config → generates typed Python class → ready to use

## Notes

- `pom get` is for discovery — review and clean the config before generating
- Add `pom.config.json` to `.gitignore` if it contains sensitive URLs
- Access full Playwright API via `site.page` when needed
