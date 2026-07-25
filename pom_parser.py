from bs4 import BeautifulSoup
from utils import to_camel_case
import keyword


def get_selector(element):
    """Build the best Playwright selector for an element.
    
    Priority: id → name → aria-label → submit type.
    Returns None if no usable selector is found.
    """
    if element['id']:
        return f"#{element['id']}"
    elif element['name']:
        return f"[name='{element['name']}']"
    elif element['aria-label']:
        return f"[aria-label='{element['aria-label']}']"
    elif element['type'] == 'submit':
        # last resort — not unique if multiple submit buttons exist
        return "button[type='submit']"


def get_element_name(element):
    """Derive a valid camelCase Python identifier from an element's attributes.
    
    Priority: id → name → aria-label → tag_type fallback.
    Returns None if no usable name can be derived or name is too long.
    """
    raw = element['id'] or element['name'] or element['aria-label']
    
    # fallback to tag + type when no identifying attribute exists
    if not raw and element.get('type'):
        raw = f"{element['tag']}_{element['type']}"
    
    if not raw:
        return None
        
    name = to_camel_case(raw)
    
    # skip names that are too long — likely auto-generated ids
    if not name or len(name) > 30:
        return None
    
    # prefix with tag name if starts with digit — invalid Python identifier
    if name[0].isdigit():
        name = element['tag'] + name.capitalize()
    
    # prefix with tag name if name is a reserved Python keyword
    if keyword.iskeyword(name) or keyword.issoftkeyword(name):
        name = element['tag'] + name.capitalize()
    
    # strip any remaining characters that are invalid in Python identifiers
    name = ''.join(c for c in name if c.isalnum() or c == '_')
    
    return name or None


def parse_elements(html):
    """Parse raw HTML and extract interactive elements as attribute dicts.
    
    Targets input, button, anchor, select, and textarea tags.
    Skips hidden inputs and deduplicates by id/name/aria-label.
    Only keeps elements with at least one identifiable attribute.
    """
    soup = BeautifulSoup(html, 'html.parser')
    elements = []
    seen = set()
    
    tags = soup.find_all(['input', 'button', 'a', 'select', 'textarea'])

    for tag in tags:
        # hidden inputs are security/internal fields — never useful for automation
        if tag.get('type') == 'hidden':
            continue

        # deduplicate by identifier — same element can appear multiple times in HTML
        identifier = tag.get('id') or tag.get('name') or tag.get('aria-label')
        if identifier is not None and identifier in seen:
            continue
        if identifier is not None:
            seen.add(identifier)

        raw_class = tag.get('class') or []
        element = {
            "tag": tag.name,
            "id": tag.get('id'),
            "class": ' '.join(raw_class),
            "name": tag.get('name'),
            "aria-label": tag.get('aria-label'),
            "type": tag.get('type')
        }
        
        # only keep elements with at least one attribute we can use as a selector
        if any([element['id'], element['name'], element['aria-label'], element['type'] == 'submit']):
            elements.append(element)
    
    return elements