from config import NOISE_KEYWORDS
import keyword
import re
from urllib.parse import urlparse


def validate_key(key: str):
    """Validate that a string is a valid Python identifier for use as a class attribute.
    
    Raises ValueError with a descriptive message if the key fails any check.
    Called before generating model files to catch bad selector names early.
    """
    if not key:
        raise ValueError("Key cannot be empty")

    if ' ' in key:
        raise ValueError(f"'{key}' cannot contain spaces")

    if key[0].isdigit():
        raise ValueError(f"'{key}' cannot start with a number")
    
    if keyword.iskeyword(key):
        raise ValueError(f"'{key}' is a Python keyword")
    
    if keyword.issoftkeyword(key):
        raise ValueError(f"'{key}' is a Python soft keyword")
    
    # catch any remaining special characters not covered above
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', key):
        raise ValueError(f"'{key}' contains invalid characters")


def to_camel_case(text: str) -> str:
    """Convert a hyphenated or underscored string to camelCase.
    
    Examples:
        login_field     → loginField
        forgot-password → forgotPassword
        submit          → submit
    """
    text = text.replace('-', ' ').replace('_', ' ')
    words = text.split(' ')
    return words[0].lower() + ''.join(word.capitalize() for word in words[1:])


def is_noise(name: str) -> bool:
    """Return True if the element name matches a known noise keyword.
    
    Noise elements are internal UI controls (dismiss buttons, error dialogs)
    that are not useful for automation. See config.py for the full list.
    """
    name_lower = name.lower()
    return any(kw in name_lower for kw in NOISE_KEYWORDS)


def parse_url(raw_url: str):
    """Parse a URL string into a ParseResult for structured access to its parts."""
    return urlparse(raw_url)