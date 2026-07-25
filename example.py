from playwright.sync_api import Locator
from base import BasePom

class Example(BasePom):
    _base_url = "https://example.com"

    class register:
        _path = "/register"
        username: Locator
        password: Locator
        submit: Locator

        _selectors = {
            "username": "#username",
            "password": "#password",
            "submit": "button[type='submit']",
        }

    class login:
        _path = "/login"
        username: Locator
        password: Locator
        submit: Locator

        _selectors = {
            "username": "#username",
            "password": "#password",
            "submit": "button[type='submit']",
        }
