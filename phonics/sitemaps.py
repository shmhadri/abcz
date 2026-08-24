"""Public, canonical URLs suitable for search-engine discovery."""

from types import SimpleNamespace

from django.contrib.sitemaps import Sitemap
from django.urls import reverse


CANONICAL_DOMAIN = "www.smartlearningksa.com"


class PublicPageSitemap(Sitemap):
    """Sitemap entries for server-rendered pages available to anonymous visitors."""

    changefreq = "weekly"

    _public_view_names = (
        "index",
        "placement_test",
        "levels",
        "pricing",
        "letters",
        "curriculum",
        "about",
        "guide",
        "privacy",
        "terms",
        "seo_phonics",
        "seo_cvc_reading_guide",
        "seo_english_reading",
        "seo_english_vocabulary",
        "seo_english_grammar",
        "seo_english_worksheets",
        "seo_letter_sounds_guide",
        "seo_cvc_words_guide",
        "seo_word_families_guide",
        "seo_reading_learning_guide",
    )

    def items(self):
        return self._public_view_names

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return 1.0 if item == "index" else 0.7

    def get_urls(self, page=1, site=None, protocol=None):
        canonical_site = SimpleNamespace(domain=CANONICAL_DOMAIN, name="Smart Learning")
        return super().get_urls(page=page, site=canonical_site, protocol="https")


sitemaps = {"public": PublicPageSitemap}
