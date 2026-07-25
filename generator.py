from playwright.sync_api import sync_playwright
from pom_parser import (
    get_selector, 
    parse_elements,
    get_element_name
)
from utils import (
    parse_url,
    validate_key,
    to_camel_case,
    is_noise
)


def _fetch_html(url):
    """Launch a headless browser, load the URL, and return the full page HTML.
    
    Uses a fresh browser instance per call — no session is preserved.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        html = page.content()
        browser.close()
        return html


def _build_name_from_url(parsed_url, name):
    """Extract a specific part of a parsed URL by name.
    
    Args:
        parsed_url: a ParseResult from urllib.parse.urlparse
        name: one of 'base', 'path', 'class', 'page'
    
    Returns the requested string or raises if name is unrecognised.
    """
    if name == "base":
        # full origin without path e.g. https://github.com
        return f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    if name == "path":
        return parsed_url.path or '/'
    
    if name == "class":
        # turn domain into a valid PascalCase Python class name
        # e.g. the-internet.herokuapp.com → TheInternet
        raw_name = parsed_url.netloc.replace('www.', '').split('.')[0]
        class_name = to_camel_case(raw_name)
        return class_name[0].upper() + class_name[1:]
    
    if name == "page":
        # use path as page name, fall back to 'home' for root
        return parsed_url.path.strip('/').lower() or 'home'

    raise Exception(f"Unknown name type: '{name}'")


def _build_selectors(elements):
    """Convert parsed elements into a clean selector dict.
    
    Skips elements with no usable name, noisy elements, and
    elements with no detectable selector.
    """
    selectors = {}
    for element in elements:
        name = get_element_name(element)
        if not name or is_noise(name):
            continue
        selector = get_selector(element)
        if selector:
            selectors[name] = selector

    return selectors


def generate_from_config(data):
    """Generate a typed Python page object model from a config dict.
    
    Expects data to have 'baseUrl' and 'pages' keys. Each page needs
    'name', 'path', and 'selectors'. Validates all selector keys before
    generating to catch invalid Python identifiers early.
    """
    base_url = data['baseUrl']
    pages = data['pages']
    parsed_url = parse_url(base_url)
    class_name = _build_name_from_url(parsed_url, "class")
    
    lines = []
    
    # boilerplate imports for the generated file
    lines.append("from playwright.sync_api import Locator")
    lines.append("from base import BasePom")
    lines.append("")
    
    lines.append(f"class {class_name}(BasePom):")
    lines.append(f'    _base_url = "{base_url}"')
    lines.append("")
    
    for page in pages:
        name = page['name']
        path = page['path']
        selectors = page['selectors']
        
        lines.append(f"    class {name}:")
        lines.append(f'        _path = "{path}"')

        # type annotations — tells VSCode each attribute is a Playwright Locator
        for key in selectors:
            validate_key(key)
            lines.append(f"        {key}: Locator")
        
        lines.append("")
        
        # runtime selectors — BasePom reads this to bind real Locator objects
        lines.append("        _selectors = {")
        for key, selector in selectors.items():
            lines.append(f'            "{key}": "{selector}",')
        lines.append("        }")
        lines.append("")
    
    return '\n'.join(lines)


def generate_config(raw_url):
    """Fetch a page and build a pom config dict from auto-detected elements.
    
    This is the discovery step — the output config is meant to be reviewed
    and edited by the user before passing to generate_from_config.
    """
    html = _fetch_html(raw_url)
    elements = parse_elements(html)
    selectors = _build_selectors(elements)

    parsed_url = parse_url(raw_url)
    base_url = _build_name_from_url(parsed_url, "base")
    path = _build_name_from_url(parsed_url, "path")
    page_name = path.strip('/') or "home"

    return {
        "baseUrl": base_url,
        "pages": [
            {
                "path": path,
                "name": page_name,
                "selectors": selectors
            }
        ]
    }