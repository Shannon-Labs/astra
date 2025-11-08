# ASTRA System Architecture

## Overview

ASTRA (Autonomous System for Transient Research & Analysis) is a modular astronomical transient discovery pipeline that operates without requiring API keys or proprietary databases.

## System Components

### 1. Data Collection Layer
- **`transient_scraper.py`** - Scrapes public transient pages
  - Rochester Astronomy Supernova Page
  - Extracts object IDs, magnitudes, types, coordinates
  - Handles HTML parsing and data normalization

- **`bright_transient_scraper.py`** - Focused bright transient detection
  - Filters by magnitude threshold
  - Prioritizes objects suitable for small telescopes

### 2. Analysis Layer
- **`enhanced_discovery_v2.py`** - Multi-factor anomaly scoring
  - Brightness scoring (m < 16.0 gets priority)
  - Type-based scoring (LRN, Ibn, etc.)
  - Unknown object bonus scoring
  - Coordinate-based cross-matching

- **`classification_engine.py`** - Advanced classification system
  - Multi-catalog cross-referencing
  - Machine learning-based anomaly detection
  - Statistical significance analysis

### 3. Cross-Matching Layer
- **`simbad_resolver.py`** - SIMBAD database queries
  - Object identification and classification
  - Historical data retrieval
  - Proper motion analysis

- **`gaia_query.py`** - Gaia DR3 cross-matching
  - Precise astrometry
  - Proper motion and parallax data
  - Stellar parameter matching

### 4. Discovery Management
- **`discovery_framework.py`** - Orchestration and workflow
  - Pipeline coordination
  - Result aggregation
  - Error handling and logging

- **`observation_planner.py`** - Follow-up observation planning
  - Visibility calculations
  - Telescope scheduling recommendations
  - Photometric planning

### 5. User Interface
- **`astra_discovery_engine.py`** - Main entry point
  - Command-line interface
  - Result formatting
  - Report generation

## Data Flow

```
Web Sources → Scraper → Initial Database → Analysis Engine → Scoring → Cross-Matching → Final Scoring → Report Generation
```

### Scoring Algorithm

The v2.0 scoring system uses multiple factors:

1. **Brightness Score**: +3 points for m < 16.0
2. **Type Score**: +5 points for rare types (LRN, CVn, etc.)
3. **Unknown Bonus**: +2 points for unclassified objects
4. **Gaia Match**: +1 point if catalog match exists
5. **Proper Motion**: +3 points for high proper motion objects

**Total Score ≥ 5.0** = High priority for follow-up

## File Structure

```
src/
├── transient_scraper.py          # Data collection
├── enhanced_discovery_v2.py      # Scoring algorithm
├── classification_engine.py      # Advanced classification
├── simbad_resolver.py           # SIMBAD integration
├── gaia_query.py                # Gaia cross-matching
├── discovery_framework.py       # Pipeline orchestration
├── observation_planner.py       # Follow-up planning
└── astra_discovery_engine.py    # Main interface
```

## Dependencies

- **astroquery**: Astronomical database queries
- **astropy**: Coordinate handling and astronomy utilities
- **requests**: HTTP requests for web scraping
- **beautifulsoup4**: HTML parsing
- **pandas**: Data manipulation
- **numpy**: Numerical computations

## Performance Characteristics

- **Runtime**: 5-10 seconds per pipeline execution
- **Memory**: <100 MB typical usage
- **Disk**: ~50 KB per run (CSV outputs)
- **Latency**: 1-2 days vs. TNS (acceptable for bright objects)

## Scalability

The system is designed for:
- **Horizontal scaling**: Multiple parallel scrapers
- **Vertical scaling**: Enhanced ML models
- **Geographic scaling**: Multi-observer coordination

## Error Handling

- Network timeouts with exponential backoff
- Graceful degradation when catalogs are unavailable
- Comprehensive logging for debugging
- Recovery mechanisms for partial failures

## Future Extensions

- **Machine Learning Integration**: Advanced anomaly detection
- **Real-time Alerts**: WebSocket-based notifications
- **Multi-wavelength**: Cross-matching with X-ray, radio surveys
- **Citizen Science**: Public discovery verification interface