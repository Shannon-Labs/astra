# ASTRA API Documentation

## Overview

ASTRA (Autonomous System for Transient Research & Analysis) provides a Python API for discovering and analyzing astronomical transients without requiring proprietary API access.

## Installation

```bash
pip install astra-discoveries
```

## Quick Start

```python
from src import run_advanced_discovery, run_basic_discovery

# Run advanced discovery pipeline
results = run_advanced_discovery()

# Access results
print(f"Found {len(results['anomalies'])} high-priority anomalies")
for anomaly in results['anomalies']:
    print(f"{anomaly['id']}: Score {anomaly['score']}, Mag {anomaly['mag']}")
```

## Core Modules

### `src` Package

Main package containing all discovery functionality.

#### Functions

##### `run_basic_discovery() -> dict`

Execute the basic ASTRA discovery pipeline.

**Returns:**
- `dict`: Results dictionary containing:
  - `transients` (pd.DataFrame): All discovered transients
  - `anomalies` (list): High-priority objects

**Example:**
```python
from src import run_basic_discovery

results = run_basic_discovery()
print(f"Analyzed {len(results['transients'])} transients")
```

##### `run_advanced_discovery() -> dict`

Execute the advanced ASTRA discovery pipeline with enhanced scoring.

**Returns:**
- `dict`: Results dictionary containing:
  - `transients` (pd.DataFrame): All discovered transients
  - `anomalies` (list): High-priority objects with detailed scoring
  - `report` (str): Formatted text report

**Example:**
```python
from src import run_advanced_discovery

results = run_advanced_discovery()
print(results['report'])

# Save report
with open('discovery_report.txt', 'w') as f:
    f.write(results['report'])
```

##### `system_check() -> bool`

Verify that all required dependencies are available.

**Returns:**
- `bool`: True if all dependencies are available, False otherwise

**Example:**
```python
from src import system_check

if system_check():
    print("Ready to discover!")
else:
    print("Missing dependencies")
```

### TransientScraper

Class for scraping public transient data sources.

#### Constructor

```python
TransientScraper()
```

Creates a new scraper instance with configured data sources.

#### Methods

##### `scrape_rochester_page() -> pd.DataFrame`

Scrape the Rochester Astronomy Supernova page for transients.

**Returns:**
- `pd.DataFrame`: DataFrame with columns:
  - `id` (str): Transient identifier (AT/SN name)
  - `mag` (float): Magnitude
  - `type` (str): Object type
  - `source` (str): Data source identifier

**Example:**
```python
from src import TransientScraper

scraper = TransientScraper()
transients = scraper.scrape_rochester_page()
print(f"Found {len(transients)} transients")
```

##### `get_recent_transients(days: int = 7) -> pd.DataFrame`

Get transients discovered within the last N days.

**Parameters:**
- `days` (int): Number of days to look back (default: 7)

**Returns:**
- `pd.DataFrame`: Filtered transient data

**Example:**
```python
from src import TransientScraper

scraper = TransientScraper()
recent = scraper.get_recent_transients(days=14)
print(f"Found {len(recent)} transients in last 2 weeks")
```

### EnhancedDiscoveryEngineV2

Advanced discovery engine with multi-factor anomaly scoring.

#### Constructor

```python
EnhancedDiscoveryEngineV2()
```

Creates a new enhanced discovery engine instance.

#### Methods

##### `calculate_advanced_score(row: pd.Series) -> tuple[float, list[str]]`

Calculate anomaly score for a transient.

**Parameters:**
- `row` (pd.Series): Transient data with `mag` and `type` fields

**Returns:**
- `tuple`: (score, reasons)
  - `score` (float): Anomaly score (0-10+)
  - `reasons` (list[str]): List of scoring factors

**Scoring Factors:**
- **Brightness:**
  - m < 14.0: +5.0 points (Exceptionally bright)
  - m < 15.0: +4.0 points (Extremely bright)
  - m < 16.0: +3.0 points (Very bright)
  - m < 17.0: +2.0 points (Bright)
  - m > 21.0: +2.0 points (Extremely faint)

- **Type:**
  - LRN (Luminous Red Nova): +5.0 points
  - Ibn (Type Ibn Supernova): +4.0 points
  - IIn (Type IIn Supernova): +3.0 points
  - Unknown: +2.0 points

**Example:**
```python
import pandas as pd
from src import EnhancedDiscoveryEngineV2

engine = EnhancedDiscoveryEngineV2()
row = pd.Series({'id': 'AT2025test', 'mag': 13.5, 'type': 'LRN'})
score, reasons = engine.calculate_advanced_score(row)
print(f"Score: {score}, Reasons: {reasons}")
```

##### `find_advanced_anomalies(transients: pd.DataFrame) -> list[dict]`

Find high-priority anomalies in transient data.

**Parameters:**
- `transients` (pd.DataFrame): Transient data

**Returns:**
- `list[dict]`: List of anomaly dictionaries, sorted by score (highest first)

**Anomaly Dictionary Structure:**
```python
{
    'id': str,           # Transient identifier
    'mag': float,        # Magnitude
    'type': str,         # Object type
    'score': float,      # Anomaly score
    'reasons': [str],    # Scoring reasons
    'source': str,       # Data source
    'ra': str,           # Right ascension (if available)
    'dec': str           # Declination (if available)
}
```

**Example:**
```python
import pandas as pd
from src import EnhancedDiscoveryEngineV2

engine = EnhancedDiscoveryEngineV2()
transients = pd.DataFrame([
    {'id': 'AT2025test1', 'mag': 13.5, 'type': 'LRN', 'source': 'Rochester'},
    {'id': 'AT2025test2', 'mag': 15.0, 'type': 'unknown', 'source': 'Rochester'}
])

anomalies = engine.find_advanced_anomalies(transients)
for anomaly in anomalies:
    print(f"{anomaly['id']}: Score {anomaly['score']:.1f}")
```

##### `generate_advanced_report(anomalies: list[dict]) -> str`

Generate a formatted text report for anomalies.

**Parameters:**
- `anomalies` (list[dict]): List of anomaly dictionaries

**Returns:**
- `str`: Formatted report text

**Example:**
```python
from src import EnhancedDiscoveryEngineV2

engine = EnhancedDiscoveryEngineV2()
results = engine.run_advanced_pipeline()

if results:
    with open('report.txt', 'w') as f:
        f.write(results['report'])
```

##### `run_advanced_pipeline() -> dict | None`

Execute the complete advanced discovery pipeline.

**Returns:**
- `dict | None`: Results dictionary or None if no data found

**Example:**
```python
from src import EnhancedDiscoveryEngineV2

engine = EnhancedDiscoveryEngineV2()
results = engine.run_advanced_pipeline()

if results:
    print(f"Found {len(results['anomalies'])} high-priority anomalies")
    results['transients'].to_csv('transients.csv', index=False)
```

## Command Line Interface

### `astra-discover`

Main CLI command for running discovery pipelines.

#### Usage

```bash
astra-discover [OPTIONS]
```

#### Options

- `--advanced`: Run the enhanced discovery pipeline (default)
- `--basic`: Run the legacy basic discovery pipeline
- `--test`: Run lightweight self-test without network calls
- `--check`: Run dependency and environment checks only
- `--output DIR`, `-o DIR`: Directory for run artifacts (default: auto-generated)
- `--verbose`, `-v`: Show extra logging
- `--help`: Show help message

#### Examples

```bash
# Run advanced discovery
astra-discover --advanced

# Run basic discovery
astra-discover --basic

# Self-test
astra-discover --test

# Dependency check
astra-discover --check

# Custom output directory
astra-discover --advanced --output ./my_results
```

#### Output Files

When running discovery pipelines, ASTRA creates:

```
discoveries/
└── advanced_run_20251108_120000/
    ├── summary.txt                    # Quick summary
    ├── astra_advanced_report.txt      # Full report
    └── advanced_transients_catalog.csv # Data catalog
```

A `latest_discovery` symlink is created pointing to the most recent run.

## Data Structures

### Transient DataFrame

```python
pd.DataFrame({
    'id': str,        # Transient identifier (AT2025*, SN2025*)
    'mag': float,     # Magnitude (can be NaN)
    'type': str,      # Object type (Ia, II, LRN, unknown, etc.)
    'source': str,    # Data source identifier
    'date': str,      # Discovery date (optional)
    'ra': str,        # Right ascension (optional)
    'dec': str        # Declination (optional)
})
```

### Anomaly Dictionary

```python
{
    'id': str,           # Transient identifier
    'mag': float,        # Magnitude
    'type': str,         # Object type
    'score': float,      # Anomaly score (0-10+)
    'reasons': [str],    # List of scoring factors
    'source': str,       # Data source
    'ra': str,           # Right ascension (optional)
    'dec': str           # Declination (optional)
}
```

## Error Handling

ASTRA uses standard Python exceptions:

```python
try:
    results = run_advanced_discovery()
except KeyboardInterrupt:
    print("Discovery interrupted")
except Exception as e:
    print(f"Discovery failed: {e}")
```

## Best Practices

### 1. Check System Before Running

```python
from src import system_check, run_advanced_discovery

if system_check():
    results = run_advanced_discovery()
else:
    print("Install missing dependencies first")
```

### 2. Handle Empty Results

```python
from src import run_advanced_discovery

results = run_advanced_discovery()

if results and results['anomalies']:
    print(f"Found {len(results['anomalies'])} anomalies")
else:
    print("No high-priority anomalies found")
```

### 3. Save Results

```python
from src import run_advanced_discovery
from datetime import datetime

results = run_advanced_discovery()

if results:
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save report
    with open(f'report_{timestamp}.txt', 'w') as f:
        f.write(results['report'])

    # Save data
    results['transients'].to_csv(f'transients_{timestamp}.csv', index=False)
```

### 4. Filter and Process Results

```python
from src import run_advanced_discovery

results = run_advanced_discovery()

if results:
    # Filter bright objects
    bright = [a for a in results['anomalies'] if a['mag'] < 16.0]

    # Filter by type
    lrn_candidates = [a for a in results['anomalies'] if 'LRN' in a['type']]

    # Sort by magnitude
    by_mag = sorted(results['anomalies'], key=lambda x: x['mag'])
```

## Version Information

```python
import src
print(src.__version__)  # '2.0.2'
```

## Support

- **GitHub Issues**: https://github.com/Shannon-Labs/astra/issues
- **Documentation**: https://github.com/Shannon-Labs/astra/docs
- **PyPI**: https://pypi.org/project/astra-discoveries/
