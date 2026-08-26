from playwright.sync_api import Locator
from base import BasePom

class Thenkiri(BasePom):
    _base_url = "https://thenkiri.com/"

    class nkiri:
        search: Locator
        posts: Locator
        post_link1: Locator
        post_link2: Locator
        dwld_links: Locator
        dwld_btn: Locator
        dwld_btn_cls: Locator

        _selectors = {
            "search": "#is-search-input-51",
            "posts": ".is-ajax-search-posts",
            "post_link1": ".is-ajax-search-posts div.is-title > a",
            "post_link2": "#primary div.search-entry-content.clr > header > h2 > a",
            "dwld_links": "div.elementor-button-wrapper > a",
            "dwld_btn": "#downloadbtn",
            "dwld_btn_cls": "button.downloadbtn",
        }
