# Release Guide

This project publishes with `uv` (PEP 517 via `pyproject.toml`).

## Steps

1. Bump `__version__` in `toolshed/__init__.py`.
2. (Optional) Clean old artifacts:
   ```bash
   rm -rf dist build *.egg-info
   ```
3. Build source + wheel distributions:
   ```bash
   uv build
   ```
4. Validate package metadata:
   ```bash
   uvx twine check dist/*
   ```
5. Upload to TestPyPI (recommended first):
   ```bash
   uv publish \
     --publish-url https://test.pypi.org/legacy/ \
     --check-url https://test.pypi.org/simple \
     dist/*
   ```
6. Upload to PyPI:
   ```bash
   uv publish dist/*
   ```

## Auth

Use API tokens with `uv`, for example:

```bash
export UV_PUBLISH_TOKEN=pypi-...
```

Alternatively:

```bash
export UV_PUBLISH_USERNAME=__token__
export UV_PUBLISH_PASSWORD=pypi-...
```
