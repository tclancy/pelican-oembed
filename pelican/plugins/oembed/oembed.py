"""Pelican oEmbed Plugin.

Uses Micawber to convert oEmbed URLs in markdown content to their embedded
HTML representations during the publishing process.

Works as a Markdown preprocessor extension, replacing bare oEmbed URLs in
the markdown source with embedded HTML before typogrify or other
post-processing can mangle the URLs.
"""

from __future__ import annotations

import re
import warnings

import markdown
from bs4 import MarkupResemblesLocatorWarning
from micawber import Provider, ProviderRegistry
from pelican import signals

# Filter BeautifulSoup warnings about URLs
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

# Create a provider registry with popular oEmbed providers
providers = ProviderRegistry()

# Twitter/X
providers.register(
    r"https://twitter.com/\S+/status/\d+",
    Provider("https://publish.twitter.com/oembed"),
)
providers.register(
    r"https://x.com/\S+/status/\d+",
    Provider("https://publish.twitter.com/oembed"),
)

# YouTube
providers.register(
    r"https://www\.youtube\.com/watch\?v=\S+",
    Provider("https://www.youtube.com/oembed"),
)
providers.register(
    r"https://youtu\.be/\S+",
    Provider("https://www.youtube.com/oembed"),
)

# Vimeo
providers.register(
    r"https://vimeo\.com/\d+",
    Provider("https://vimeo.com/api/oembed.json"),
)
providers.register(
    r"https://player\.vimeo\.com/video/\d+",
    Provider("https://vimeo.com/api/oembed.json"),
)

# Instagram
providers.register(
    r"https://www\.instagram\.com/p/\S+",
    Provider("https://api.instagram.com/oembed"),
)
providers.register(
    r"https://instagram\.com/p/\S+",
    Provider("https://api.instagram.com/oembed"),
)

# SoundCloud
providers.register(
    r"https://soundcloud\.com/\S+",
    Provider("https://soundcloud.com/oembed"),
)

# Spotify
providers.register(
    r"https://open\.spotify\.com/\S+",
    Provider("https://embed.spotify.com/oembed"),
)

# TikTok
providers.register(
    r"https://www\.tiktok\.com/\S+/video/\d+",
    Provider("https://www.tiktok.com/oembed"),
)

# Bare URL on its own line (not inside markdown link syntax)
BARE_URL_RE = re.compile(r"^(https?://\S+)$")


class OEmbedPreprocessor(markdown.preprocessors.Preprocessor):
    """Replace bare oEmbed URLs in markdown source with HTML embeds."""

    def run(self, lines: list[str]) -> list[str]:
        """Process lines and embed any bare oEmbed URLs."""
        new_lines = []
        for line in lines:
            match = BARE_URL_RE.match(line.strip())
            if match:
                url = match.group(1)
                try:
                    result = providers.request(url, maxwidth=800, maxheight=600)
                    html = result.get("html", "")
                    if html:
                        new_lines.append(html)
                        continue
                except Exception:  # noqa: BLE001
                    pass
            new_lines.append(line)
        return new_lines


class OEmbedExtension(markdown.Extension):
    """Markdown extension that registers the OEmbed preprocessor."""

    def extendMarkdown(self, md: markdown.Markdown) -> None:  # noqa: N802
        """Add the OEmbed preprocessor to the Markdown pipeline."""
        md.preprocessors.register(OEmbedPreprocessor(md), "oembed", 30)


def pelican_init(pelican_obj) -> None:
    """Inject the OEmbed markdown extension into Pelican's markdown config."""
    md_settings = pelican_obj.settings.setdefault("MARKDOWN", {})
    extensions = md_settings.setdefault("extensions", [])
    extensions.append(OEmbedExtension())


def register() -> None:
    """Register the plugin's signals with Pelican."""
    signals.initialized.connect(pelican_init)
