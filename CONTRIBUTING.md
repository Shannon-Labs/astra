# Contributing to ASTRA

Thank you for your interest in contributing to ASTRA! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive
- Focus on constructive criticism
- Help create a welcoming environment for all

## How to Contribute

### Reporting Issues

If you find a bug or have a feature request:
1. Check existing [issues](https://github.com/Shannon-Labs/astra/issues) first
2. Create a new issue with clear title and description
3. Include steps to reproduce (for bugs)
4. Add relevant labels (bug, enhancement, question)

### Contributing Code

1. **Fork the repository** on GitHub
2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/astra.git
   cd astra
   ```
3. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Set up development environment**:
   ```bash
   python3 -m venv astra_env
   source astra_env/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If you add dev dependencies
   ```
5. **Make your changes**:
   - Follow PEP 8 style guidelines
   - Add docstrings to new functions
   - Include type hints where possible
   - Write tests for new features
6. **Run tests**:
   ```bash
   python tests/test_infrastructure.py
   ```
7. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: your descriptive commit message"
   ```
   We follow conventional commits:
   - `feat:` New features
   - `fix:` Bug fixes
   - `docs:` Documentation changes
   - `test:` Test additions/modifications
   - `refactor:` Code refactoring
8. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
9. **Create a Pull Request** on GitHub

### Adding New Data Sources

To add a new transient source:
1. Create a new scraper module in `src/`
2. Implement the scraping logic
3. Add tests in `tests/`
4. Update documentation
5. Submit PR with example output

Example structure:
```python
# src/new_scraper.py
def scrape_new_source():
    """Scrape transients from new source."""
    # Your implementation here
    return pandas.DataFrame(...)
```

### Improving Anomaly Detection

The scoring algorithm in `src/enhanced_discovery_v2.py` can be enhanced:
- Add new scoring factors
- Adjust weights based on feedback
- Implement machine learning classification
- Add new transient type handlers

### Documentation Improvements

We welcome documentation improvements:
- Fix typos and clarify explanations
- Add examples and use cases
- Improve API documentation
- Translate to other languages

## Development Guidelines

### Code Style
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use meaningful variable names
- Add docstrings to all functions
- Keep functions focused and small

### Testing
- Write tests for all new features
- Ensure all tests pass before submitting PR
- Add edge case tests
- Test with real data when possible

### Performance
- Profile code before optimizing
- Consider memory usage for large datasets
- Use efficient pandas operations
- Cache repeated computations

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Included in CITATION.cff for major contributions
- Recognized in release notes
- Invited to join ASTRA Collaboration

## Questions?

- **Technical issues**: Open a GitHub issue
- **Scientific questions**: Email astra@shannonlabs.io
- **General discussion**: Use GitHub Discussions

Thank you for helping make ASTRA better!

---

**ASTRA Collaboration**  
*Democratizing transient discovery, one contribution at a time.*