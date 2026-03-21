# pelican-oembed

A [Pelican](https://getpelican.com/) plugin that embeds oEmbed URLs (YouTube, Vimeo, Twitter/X, Spotify, etc.) directly in your Markdown content.

Bare URLs on their own line are replaced with embedded HTML using the [Micawber](https://micawber.readthedocs.io/) oEmbed library, before Pelican post-processing runs.

## Installation

```shell
pip install pelican-oembed
```

Then add to your Pelican `pelicanconf.py`:

```python
PLUGINS = ["pelican.plugins.oembed"]
```

## Usage

Place a bare URL on its own line in your Markdown content:

```markdown
Check out this video:

https://www.youtube.com/watch?v=dQw4w9WgXcQ

More text here.
```

The URL will be replaced with the oEmbed HTML (an `<iframe>` for YouTube, etc.).

## Supported Providers

- YouTube (`youtube.com`, `youtu.be`)
- Vimeo (`vimeo.com`)
- Twitter/X (`twitter.com`, `x.com`)
- Instagram (`instagram.com`)
- SoundCloud (`soundcloud.com`)
- Spotify (`open.spotify.com`)
- TikTok (`tiktok.com`)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT
