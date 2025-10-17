# PyPI Release Setup

## Prerequisites

1. **PyPI Account**: Create account at https://pypi.org
2. **API Token**: Generate at https://pypi.org/manage/account/token/

## GitHub Setup

### 1. Add PyPI Token to GitHub Secrets

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `PYPI_API_TOKEN`
5. Value: Your PyPI API token (starts with `pypi-`)
6. Click **Add secret**

### 2. Verify Workflows

The repository now has two workflows:

**`.github/workflows/release.yml`**
- Triggers on version tags (e.g., `v4.0.0`)
- Builds package
- Publishes to PyPI
- Creates GitHub Release

**`.github/workflows/ci.yml`**
- Triggers on push/PR to main
- Runs tests on Python 3.11, 3.12, 3.13
- Validates imports

## Release Process

### Automatic Release (Recommended)

1. **Update version** in `pyproject.toml`:
   ```toml
   version = "4.0.0"
   ```

2. **Commit and push**:
   ```bash
   git add pyproject.toml
   git commit -m "chore: Bump version to 4.0.0"
   git push origin main
   ```

3. **Create and push tag**:
   ```bash
   git tag -a v4.0.0 -m "Release v4.0.0"
   git push origin v4.0.0
   ```

4. **GitHub Actions automatically**:
   - Builds the package
   - Publishes to PyPI
   - Creates GitHub Release

### Manual Release (Fallback)

If GitHub Actions fails:

```bash
# Build
python -m build

# Upload to PyPI
twine upload dist/*
```

## Verification

After release:

1. **Check PyPI**: https://pypi.org/project/ai-configurator/
2. **Test installation**:
   ```bash
   pip install ai-configurator==4.0.0
   ai-config --version
   ```

## Troubleshooting

### PyPI Token Invalid

- Regenerate token at https://pypi.org/manage/account/token/
- Update GitHub secret

### Build Fails

- Check `pyproject.toml` syntax
- Verify all dependencies are listed
- Test locally: `python -m build`

### Upload Fails

- Ensure version doesn't already exist on PyPI
- Check token has upload permissions
- Verify package name is available

## Version Numbering

Follow Semantic Versioning (semver):

- **Major** (4.0.0): Breaking changes
- **Minor** (4.1.0): New features, backward compatible
- **Patch** (4.0.1): Bug fixes

## Pre-release Versions

For testing:

```bash
# Update version to 4.1.0rc1
git tag -a v4.1.0rc1 -m "Release candidate"
git push origin v4.1.0rc1
```

Install with:
```bash
pip install --pre ai-configurator
```
