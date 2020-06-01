# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## 0.2.0 - 2020-06-01

### Changed

- Project was renamed from `sitemaps` to `asgi-sitemaps` - sitemap generation for ASGI apps. (Pull #2)
- Change options of CLI and programmatic API to fit new "ASGI-only" project scope. (Pull #2)
- CLI now reads from stdin (for `--check` mode) and outputs sitemap to stdout. (Pull #2)

### Removed

- Drop support for crawling arbitrary remote servers. (Pull #2)

### Fixed

- Don't include non-200 or non-HTML URLs in sitemap. (Pull #2)

## 0.1.0 - 2020-05-31

### Added

- Initial implementation: CLI and programmatic async API.
