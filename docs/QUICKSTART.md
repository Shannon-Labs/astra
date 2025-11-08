# ASTRA Quick Start Guide

Get ASTRA running in 5 minutes and discover your first astronomical transients!

## Prerequisites

- **Python 3.8+** (tested on 3.8-3.11)
- **Internet connection** (for data scraping)
- **~500 MB disk space** (for virtual environment)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Shannon-Labs/astra.git
cd astra
```

### 2. Create Virtual Environment

```bash
# Create environment
python3 -m venv astra_env

# Activate environment
# macOS/Linux:
source astra_env/bin/activate
# Windows:
astra_env\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
python tests/test_infrastructure.py
```

**Expected output:**
```
🎉 ASTRA IS READY FOR DISCOVERY OPS
```

## Your First Discovery

### Option 1: Quick Test (30 seconds)

```bash
# Run basic discovery test
python src/transient_scraper.py
```

This will show you current bright transients without the advanced scoring.

### Option 2: Full Discovery Pipeline (2 minutes)

```bash
# Run the complete discovery system
./scripts/run_advanced.sh
```

**Expected output:**
```
🚀 ASTRA Advanced Discovery System
=====================================
✓ Environment activated
📁 Output directory: discovery_run_20251108_143022
✓ Found 35 bright transients
✓ Found 4 high-priority anomalies

🎯 TOP DISCOVERY: AT2025abao (Score: 8.0)
   Type: LRN (Luminous Red Nova)
   Magnitude: 15.1
   Action: Immediate spectroscopy
```

## Understanding the Results

### Check the Report

```bash
# View the main discovery report
cat advanced_report
```

### Detailed Analysis

```bash
# Check the latest results directory
ls -la latest_discovery/

# View detailed summary
cat latest_discovery/summary.txt

# See all discovered objects
cat latest_discovery/advanced_transients_catalog.csv
```

## Customization

### Adjust Discovery Parameters

Edit `src/enhanced_discovery_v2.py` to modify:

```python
# Change magnitude threshold
BRIGHTNESS_THRESHOLD = 16.0  # Default: 16.0

# Adjust scoring weights
BRIGHTNESS_SCORE = 3  # Points for bright objects
UNKNOWN_TYPE_BONUS = 2  # Points for unclassified
```

### Focus on Specific Object Types

```python
# Prioritize only Luminous Red Novae
PRIORITY_TYPES = ['LRN']

# Exclude common types
EXCLUDE_TYPES = ['AGN', 'CV']
```

## Common Tasks

### Run Discovery Daily

```bash
# Add to crontab for automated runs
crontab -e

# Run every day at 2 AM
0 2 * * * cd /path/to/astra && ./scripts/run_advanced.sh
```

### Manual Research

```python
# Start Python interpreter
python
>>> from src.enhanced_discovery_v2 import run_discovery_pipeline
>>> results = run_discovery_pipeline()
>>> print(results[results['score'] >= 5.0])  # High priority only
```

### Export Data

```bash
# Convert results to JSON for web display
python -c "
import pandas as pd
df = pd.read_csv('latest_discovery/advanced_transients_catalog.csv')
print(df.to_json(indent=2))
" > latest_discovery/results.json
```

## Troubleshooting

### Installation Issues

**Problem:** `astroquery` installation fails
```bash
# Try installing conda-forge version
conda install -c conda-forge astroquery
```

**Problem:** Virtual environment activation fails
```bash
# Ensure Python 3.8+
python3 --version

# Create new environment
rm -rf astra_env
python3 -m venv astra_env
source astra_env/bin/activate
```

### Runtime Issues

**Problem:** "No transients found"
- Check internet connection
- Verify Rochester page is accessible
- Try running at different times (pages update periodically)

**Problem:** Module import errors
```bash
# Ensure you're in project directory
pwd  # Should show .../astra

# Check Python path
python -c "import sys; print(sys.path)"
```

**Problem:** Permission errors
```bash
# Make script executable
chmod +x scripts/run_advanced.sh
```

### Performance Issues

**Slow execution:**
- Network latency is normal (first run ~10s)
- Subsequent runs are faster (~5s)
- Consider running during off-peak hours

**High memory usage:**
- Normal: <100 MB
- If >500 MB, restart virtual environment
- Check for memory leaks with repeated runs

## Advanced Usage

### Custom Data Sources

Add new scrapers by extending `transient_scraper.py`:

```python
def scrape_custom_source():
    """Add your own data source here"""
    # Your scraping logic
    return transients
```

### Machine Learning Integration

```bash
# Install ML dependencies
pip install scikit-learn

# Enable ML-based anomaly detection
export ASTRA_ML_ENABLED=true
python src/enhanced_discovery_v2.py
```

### Multi-Observer Coordination

```bash
# Share results with collaborators
rsync -av latest_discovery/ collaborator@server:/shared/astra/

# Combine multiple observations
python scripts/combine_observations.py observer1.csv observer2.csv
```

## Getting Help

### Documentation
- [Full Architecture Guide](ARCHITECTURE.md)
- [Scientific Methodology](SCIENTIFIC_METHOD.md)
- [Publication Guide](PUBLICATION_GUIDE.md)

### Community
- [GitHub Issues](https://github.com/Shannon-Labs/astra/issues) - Bug reports and feature requests
- [Discussions](https://github.com/Shannon-Labs/astra/discussions) - Questions and general discussion

### Performance Monitoring
```bash
# Run with detailed timing
time ./scripts/run_advanced.sh

# Monitor system resources
htop  # or Activity Monitor on macOS
```

## Next Steps

1. **Schedule regular runs** using cron or systemd
2. **Set up notifications** for high-priority discoveries
3. **Coordinate with local observatory** for follow-up observations
4. **Share your discoveries** with the astronomical community
5. **Contribute improvements** to the ASTRA project

## Success Stories

If you make discoveries using ASTRA, please:
1. **File a GitHub issue** to share your results
2. **Cite the project** in any publications (see CITATION.cff)
3. **Contribute back** improvements to help others

Happy hunting! 🌟