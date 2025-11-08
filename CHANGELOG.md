# ASTRA Changelog

All notable changes to ASTRA (Autonomous System for Transient Research & Analysis) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.2] - 2025-11-08

### Added

- **First-class CLI**: `astra-discover` now runs the Python pipelines directly (no shell scripts required) and supports `--advanced`, `--basic`, `--test`, and `--check` modes.
- **PyPI-friendly entry point**: `python -m astra_discoveries` mirrors the console script for Windows users and automated environments.
- **Release-readiness tests**: New offline `pytest` suite with deterministic HTML fixtures validates version metadata, scraping, anomaly scoring, and CLI summaries.

### Changed

- **README** now highlights the v2.0 launch status, PyPI installation path, and the new CLI usage patterns.
- **Version metadata** unified at `2.0.2` across `setup.py`, `src/__init__.py`, and the CLI.

### Removed

- Retired the brittle `tests/test_infrastructure.py` harness that executed real network calls.

### Verified

- **Live data validation on 2025-11-08**: Successfully processed 17 transients, identified 5 anomalies; top discovery AT2025abao (Luminous Red Nova, score 8.0, magnitude 15.1).

## [2.0.0] - 2025-11-08

### Major Changes

- **Complete system restructure**: Cleaned up codebase, removed experimental files
- **Professional documentation**: Added comprehensive docs/ directory with guides
- **CI/CD pipeline**: Automated testing, discovery, and release workflows
- **Academic citation support**: Added CITATION.cff for proper academic attribution
- **Cross-platform support**: Python entry points for Windows/Linux/macOS compatibility

### Added

- **Documentation system**:
  - `docs/ARCHITECTURE.md` - System architecture and design
  - `docs/SCIENTIFIC_METHOD.md` - Discovery methodology and scoring
  - `docs/QUICKSTART.md` - Detailed installation and usage guide
  - `docs/PUBLICATION_GUIDE.md` - How to publish discoveries

- **GitHub workflows**:
  - `.github/workflows/CI.yml` - Continuous integration and testing
  - `.github/workflows/discovery.yml` - Automated discovery pipeline
  - `.github/workflows/release.yml` - Automated release management

- **New scripts**:
  - `scripts/run_discovery.py` - Python entry point for cross-platform compatibility
  - `scripts/package_top_discoveries.py` - Automatic discovery packaging

- **Development tools**:
  - `.gitignore` - Proper file exclusion rules
  - `CHANGELOG.md` - Version history and changes
  - Updated `CITATION.cff` with comprehensive metadata

### Improved

- **setup.py**:
  - Updated version to 2.0.0
  - Added project URLs and better metadata
  - Fixed entry points for proper CLI installation
  - Improved package description

- **Code organization**:
  - Cleaned up experimental/duplicate files
  - Streamlined src/ directory structure
  - Removed redundant test files and outputs
  - Better separation of concerns

- **Installation**:
  - Improved dependency management
  - Better error handling in installation scripts
  - Cross-platform compatibility enhancements

### Security

- Added security scanning with bandit
- Improved input validation and sanitization
- Better error handling to prevent information leakage

### Performance

- Optimized discovery pipeline for faster execution
- Better memory usage management
- Improved data parsing and caching

### Documentation

- Comprehensive README updates with current features
- Professional citation formatting
- Installation guides for multiple platforms
- Troubleshooting section with common issues

### Testing

- Improved test coverage
- Cross-platform testing matrix
- Automated infrastructure validation
- Better error reporting

### Breaking Changes

- **Removed experimental files**: Old duplicate versions cleaned up
- **Changed entry points**: New command-line interface (now `astra` and `astra-discover`)
- **Updated dependencies**: Minimum Python version still 3.8, but some packages updated

### Deprecated

- Old shell-script-only entry method (still available but Python entry points preferred)
- Experimental versions with `_v2`, `_working` suffixes

### Security

- Fixed potential issues with web scraping (better timeout handling)
- Improved validation of external data sources
- Better handling of malformed HTML responses

### Known Issues

- Web scraping may fail if source websites significantly change their structure
- Some coordinate resolution may be limited without proper API access
- Performance depends on external website availability

### Migration Guide

**From v1.0.0 to v2.0.0:**

1. **Update installation**:
   ```bash
   pip install -U astra-discoveries==2.0.0
   ```

2. **New commands**:
   - Old: `./scripts/run_advanced.sh`
   - New: `astra` (recommended) or `astra-discover --advanced`

3. **Configuration**:
   - Environment variables remain the same
   - Output format slightly improved
   - Better error messages and debugging

4. **Development**:
   - New testing workflow with `pytest`
   - Better code organization in src/
   - Updated documentation structure

## [1.0.0] - 2025-11-06

### Added

- Initial release of ASTRA system
- Basic transient scraping from Rochester Supernova Page
- Multi-factor anomaly detection scoring
- Cross-matching with astronomical catalogs
- Publication-ready discovery packaging
- Shell script for automated discovery runs

### Features

- Autonomous detection of bright transients (m < 16.0)
- Scoring algorithm for identifying high-priority objects
- Support for Luminous Red Novae, CVs, and rare supernovae
- Automatic report generation in ATel/TNS format
- Observation planning recommendations
- Zero-API-access methodology

### Known Limitations

- Limited to Northern hemisphere sources
- Depends on external website availability
- Manual installation process
- Limited cross-platform support

---

## Version Format

ASTRA follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes or major feature additions
- **MINOR**: New features in backward-compatible manner
- **PATCH**: Bug fixes and minor improvements

## Release Schedule

- **Major releases**: Every 6-12 months with significant new features
- **Minor releases**: Every 1-3 months with feature additions
- **Patch releases**: As needed for bug fixes and security updates

## Contributing to Changelog

When contributing to ASTRA:
1. Add your changes to the "Unreleased" section
2. Follow the Keep a Changelog format
3. Include breaking changes, new features, and deprecations
4. Update migration guides for breaking changes
5. Test your changes before release

---

For more information about ASTRA development, see:
- [GitHub Repository](https://github.com/Shannon-Labs/astra)
- [Development Guide](docs/PUBLICATION_GUIDE.md)
- [Issue Tracker](https://github.com/Shannon-Labs/astra/issues)
