"""Tests for pelican.plugins.oembed."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import markdown

from pelican.plugins.oembed.oembed import (
    BARE_URL_RE,
    OEmbedExtension,
    OEmbedPreprocessor,
    pelican_init,
    register,
)


class TestBareUrlRegex:
    def test_matches_http_url(self):
        assert BARE_URL_RE.match("https://www.youtube.com/watch?v=abc123")

    def test_matches_http_only_url(self):
        assert BARE_URL_RE.match("http://example.com/video")

    def test_does_not_match_text_with_url(self):
        assert not BARE_URL_RE.match("Check out https://youtube.com/watch?v=abc")

    def test_does_not_match_markdown_link(self):
        assert not BARE_URL_RE.match("[Watch this](https://youtube.com/watch?v=abc)")

    def test_does_not_match_plain_text(self):
        assert not BARE_URL_RE.match("just some text")


class TestOEmbedPreprocessor:
    def _make_preprocessor(self):
        md = markdown.Markdown()
        return OEmbedPreprocessor(md)

    def test_passes_through_non_url_lines(self):
        preprocessor = self._make_preprocessor()
        lines = ["# Heading", "Some text here.", "Another line."]
        result = preprocessor.run(lines)
        assert result == lines

    def test_passes_through_url_when_oembed_fails(self):
        preprocessor = self._make_preprocessor()
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        with patch(
            "pelican.plugins.oembed.oembed.providers.request",
            side_effect=Exception("Network error"),
        ):
            result = preprocessor.run([url])
        assert result == [url]

    def test_replaces_url_with_html_on_success(self):
        preprocessor = self._make_preprocessor()
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        mock_html = '<iframe src="https://www.youtube.com/embed/dQw4w9WgXcQ"></iframe>'
        with patch(
            "pelican.plugins.oembed.oembed.providers.request",
            return_value={"html": mock_html},
        ):
            result = preprocessor.run([url])
        assert result == [mock_html]

    def test_passes_through_when_no_html_in_response(self):
        preprocessor = self._make_preprocessor()
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        with patch(
            "pelican.plugins.oembed.oembed.providers.request",
            return_value={"type": "photo", "url": "https://example.com/photo.jpg"},
        ):
            result = preprocessor.run([url])
        assert result == [url]

    def test_mixed_lines(self):
        preprocessor = self._make_preprocessor()
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        mock_html = "<iframe>...</iframe>"
        lines = ["Before the embed.", url, "After the embed."]
        with patch(
            "pelican.plugins.oembed.oembed.providers.request",
            return_value={"html": mock_html},
        ):
            result = preprocessor.run(lines)
        assert result == ["Before the embed.", mock_html, "After the embed."]


class TestOEmbedExtension:
    def test_registers_preprocessor(self):
        md = markdown.Markdown()
        ext = OEmbedExtension()
        ext.extendMarkdown(md)
        assert "oembed" in md.preprocessors


class TestPelicanInit:
    def test_adds_extension_to_pelican_settings(self):
        mock_pelican = MagicMock()
        mock_pelican.settings = {}
        pelican_init(mock_pelican)
        extensions = mock_pelican.settings["MARKDOWN"]["extensions"]
        assert len(extensions) == 1
        assert isinstance(extensions[0], OEmbedExtension)

    def test_appends_to_existing_extensions(self):
        mock_pelican = MagicMock()
        mock_pelican.settings = {"MARKDOWN": {"extensions": ["codehilite"]}}
        pelican_init(mock_pelican)
        extensions = mock_pelican.settings["MARKDOWN"]["extensions"]
        assert len(extensions) == 2
        assert isinstance(extensions[-1], OEmbedExtension)


class TestRegister:
    def test_register_connects_signal(self):
        from pelican import signals

        with patch.object(signals.initialized, "connect") as mock_connect:
            register()
            mock_connect.assert_called_once_with(pelican_init)
