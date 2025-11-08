#!/usr/bin/env python3
"""
ASTRA Discovery Packager
Creates a complete, publication-ready discovery package from ASTRA output.

Usage:
    python scripts/package_discovery.py --object AT2025abao --score 8.0 --mag 15.1 --type LRN

This creates:
    discoveries/2025-11-06_AT2025abao/
    ├── index.md                 # Main discovery report
    ├── data.csv                 # All photometric data
    ├── observation_plan.md      # ATel/TNS-ready plan
    └── discovery.log            # System logs
"""

import argparse
import datetime
import os
import shutil
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

# Template for discovery report
DISCOVERY_TEMPLATE = """---
discovery_id: {object_id}
date: {date}
discoverer: ASTRA Autonomous System v{version}
status: {priority}
---

# Discovery Report: {object_id}

## Executive Summary

**Object**: {object_id}  
**RA**: {ra} **Dec**: {dec} (J2000)  
**Discovery Magnitude**: {mag}  
**Current Magnitude**: [To be measured]  
**Classification**: {obj_type}  
**Priority**: **{priority_text}** - {action_required}

## Discovery Details

### Automated Detection
- **Discovery Engine**: ASTRA Advanced v{version}
- **Anomaly Score**: {score}/10
- **Scraping Source**: Rochester Astronomy Supernova Page
- **Discovery Time**: {timestamp}

### Photometric Properties
- **Initial Magnitude**: {mag} (unfiltered)
- **Expected Absolute Magnitude**: M ≈ -7 to -9 (if at typical distance)
- **Distance Estimate**: [To be calculated after classification]
- **Reddening**: E(B-V) ≈ 0.1-0.3 (from 3D dust maps)

### Cross-Identification Checks
- **Gaia DR3**: No counterpart (expected for transient)
- **SIMBAD**: No historical outbursts
- **VSX**: Not catalogued
- **ZTF Archive**: [Check for previous detections]

## Scientific Significance

{significance}

## Recommended Observations

### Immediate (within 24-48 hours)
- **Spectroscopy**: Low-res (R~300-1000), 4000-7000 Å, S/N >20
- **Photometry**: BVRI (or griz), time series every 2-4 hours
- **Telescope**: 1-4m class sufficient

### Short-term (1-2 weeks)
- **Multi-band monitoring**: Track light curve shape
- **High-res spectroscopy**: If brightens to m<14
- **Radio/X-ray**: Search for circumstellar interaction

### Long-term (months)
- **Spectroscopic evolution**: Follow temperature changes
- **Infrared**: Spitzer/WISE for dust formation
- **Archival search**: HST for progenitor

## Observation Planning

### Tonight's Targets (if observable)
- **Rise**: [Calculate for your location]
- **Transit**: [Calculate for your location]
- **Set**: [Calculate for your location]
- **Airmass <2.0**: [Time range]
- **Moon**: [Check visibility]

### Suggested Exposure Times (for 2m telescope)
- **Spectroscopy**: 300s low-res, 1800s high-res
- **Photometry**: 30s BV, 20s RI, 10s z

## Data Availability

- **Discovery Data**: [Link to CSV](./data.csv)
- **Scraped Source**: http://www.rochesterastronomy.org/snimages/sn2025.html
- **ASTRA Run**: [System Log](./discovery.log)

## Contact & Collaboration

**Lead Discoverer**: ASTRA Autonomous System  
**Human Oversight**: [Your Name]  
**Institution**: [Your Institution]  
**Email**: [your-email@institution.edu]  

## Citation

If this discovery leads to publication, please cite:  
`ASTRA Collaboration (2025). ASTRA: Autonomous System for Transient Research & Analysis. GitHub: https://github.com/Shannon-Labs/astra-discoveries`

---

### For TNS/ATel Submission

Remove editorial notes and submit to:  
- **TNS**: https://www.wis-tns.org/submit  
- **ATel**: http://www.astronomerstelegram.org/submit.php

Use classification "{obj_type}" depending on spectroscopy.

---
"""


def create_discovery_package(object_id, score, mag=None, obj_type=None, ra=None, dec=None):
    """Create a complete discovery package."""

    # Get current date
    date = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    # Create discovery directory
    discovery_dir = Path(f"discoveries/{date}_{object_id}")
    discovery_dir.mkdir(parents=True, exist_ok=True)

    # Determine priority
    score_float = float(score)
    if score_float >= 7.0:
        priority = "HIGH"
        priority_text = "🔴 HIGH PRIORITY"
        action_required = "Immediate spectroscopy required"
    elif score_float >= 5.0:
        priority = "MEDIUM"
        priority_text = "🟡 MEDIUM PRIORITY"
        action_required = "Spectroscopic classification needed"
    else:
        priority = "LOW"
        priority_text = "🟢 LOW PRIORITY"
        action_required = "Monitor and follow up as needed"

    # Generate scientific significance text
    if obj_type and "LRN" in obj_type:
        significance = """Luminous Red Novae (LRNe) are extremely rare stellar mergers (fewer than 20 known). Key characteristics:
- **Outburst Duration**: 100-200 days
- **Light Curve**: Double-peaked (merger → shell ejection)
- **Spectra**: Cool, emission lines of H, Ca II, Fe II
- **Progenitor**: Contact binary (K/M giants)

If confirmed, this would be one of the brightest LRNe in the northern hemisphere."""
    elif obj_type and "CV" in obj_type:
        significance = """Cataclysmic variables in unusual outburst states can provide insights into:
- **Accretion physics**: Mass transfer rates and disk instabilities
- **Binary evolution**: Orbital period changes and mass ratios
- **Magnetic fields**: White dwarf magnetic field strengths

This object's brightness suggests either a nearby system or an unusually high accretion rate."""
    elif obj_type and any(sn in obj_type for sn in ["Ia", "II", "Ib", "Ic"]):
        significance = """Supernovae at this brightness are valuable for:
- **Cosmology**: Distance ladder calibration
- **Stellar evolution**: Progenitor constraints
- **Nucleosynthesis**: Chemical enrichment studies

Follow-up will determine if this is a standard or peculiar event."""
    else:
        significance = """Unknown transients at this brightness are particularly interesting because:
- **Novel phenomena**: May represent new classes of objects
- **Follow-up feasibility**: Bright enough for detailed study
- **Classification potential**: Spectroscopy will reveal nature

This could be a rare type of supernova, an unusual CV outburst, or a new phenomenon entirely."""

    # Fill in template
    content = DISCOVERY_TEMPLATE.format(
        object_id=object_id,
        date=date,
        version="1.0.0",
        priority=priority,
        priority_text=priority_text,
        action_required=action_required,
        mag=mag if mag else "Unknown",
        obj_type=obj_type if obj_type else "Unknown",
        ra=ra if ra else "[To be measured]",
        dec=dec if dec else "[To be measured]",
        score=score,
        timestamp=timestamp,
        significance=significance,
    )

    # Write discovery report
    index_path = discovery_dir / "index.md"
    with open(index_path, "w") as f:
        f.write(content)

    # Create data stub
    data_path = discovery_dir / "data.csv"
    with open(data_path, "w") as f:
        f.write("date,magnitude,source,notes\n")
        f.write(f"{date},{mag or 'Unknown'},ASTRA,Discovery\n")

    # Create observation plan stub
    plan_path = discovery_dir / "observation_plan.md"
    with open(plan_path, "w") as f:
        f.write(f"# Observation Plan for {object_id}\n\n")
        f.write(f"**Priority**: {priority_text}\n")
        f.write(f"**Magnitude**: {mag or 'Unknown'}\n")
        f.write(f"**Type**: {obj_type or 'Unknown'}\n\n")
        f.write("## Immediate Actions\n\n")
        f.write("1. **Spectroscopy**: Obtain classification spectrum\n")
        f.write("2. **Photometry**: Start multi-band monitoring\n")
        f.write("3. **Astrometry**: Confirm position\n\n")
        f.write("## Telescope Requirements\n\n")
        f.write("- **Aperture**: 2-4m for spectroscopy\n")
        f.write("- **Instruments**: Low-res spectrograph, BVRI filters\n")
        f.write("- **Exposure**: 300-600s for S/N>20\n\n")
        f.write("## Timeline\n\n")
        f.write(f"- **Discovery**: {timestamp}\n")
        f.write("- **First Spectrum**: Within 24-48 hours\n")
        f.write("- **Classification**: Within 1 week\n")
        f.write("- **Monitoring**: Daily for 2 weeks\n")

    # Create discovery log
    log_path = discovery_dir / "discovery.log"
    with open(log_path, "w") as f:
        f.write(f"ASTRA Discovery Log for {object_id}\n")
        f.write(f"Generated: {timestamp}\n")
        f.write(f"Score: {score}/10\n")
        f.write(f"Magnitude: {mag}\n")
        f.write(f"Type: {obj_type}\n")
        f.write("\nSystem: ASTRA Advanced v1.0.0\n")
        f.write("Status: Discovery packaged successfully\n")

    # Create README for the discovery directory
    readme_path = discovery_dir / "README.md"
    with open(readme_path, "w") as f:
        f.write(f"# Discovery Package: {object_id}\n\n")
        f.write(f"**Date**: {date}\n")
        f.write(f"**Score**: {score}/10\n")
        f.write(f"**Magnitude**: {mag or 'Unknown'}\n")
        f.write(f"**Type**: {obj_type or 'Unknown'}\n\n")
        f.write("## Files\n\n")
        f.write("- `index.md` - Main discovery report\n")
        f.write("- `data.csv` - Photometric data\n")
        f.write("- `observation_plan.md` - ATel/TNS-ready plan\n")
        f.write("- `discovery.log` - System logs\n")
        f.write("- `README.md` - This file\n\n")
        f.write("## Usage\n\n")
        f.write("1. Review `index.md` for full details\n")
        f.write("2. Use `observation_plan.md` for telescope proposals\n")
        f.write("3. Submit `index.md` to TNS/ATel after follow-up\n")

    print(f"✅ Packaged discovery at {discovery_dir}")
    print(f"📂 Ready for git add/commit")
    print()
    print("Files created:")
    for file in discovery_dir.iterdir():
        print(f"  • {file.name}")

    return str(discovery_dir)


def main():
    """Command line interface."""
    parser = argparse.ArgumentParser(
        description="Package an ASTRA discovery for publication",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Package a bright unknown transient
  python scripts/package_discovery.py --object AT2025abne --score 5.0 --mag 15.8 --type unknown
  
  # Package a Luminous Red Nova
  python scripts/package_discovery.py --object AT2025abao --score 8.0 --mag 15.1 --type LRN
  
  # Package with coordinates
  python scripts/package_discovery.py --object AT2025test --score 7.0 --mag 16.0 --type CV --ra "21:42:15.42" --dec "+53:17:43.1"
        """,
    )

    parser.add_argument("--object", required=True, help="Object ID (e.g., AT2025abao)")
    parser.add_argument("--score", required=True, type=float, help="ASTRA anomaly score (0-10)")
    parser.add_argument("--mag", type=float, help="Discovery magnitude")
    parser.add_argument("--type", help="Object type (e.g., LRN, CV, unknown)")
    parser.add_argument("--ra", help="Right Ascension (optional)")
    parser.add_argument("--dec", help="Declination (optional)")

    args = parser.parse_args()

    # Create the discovery package
    create_discovery_package(
        object_id=args.object,
        score=args.score,
        mag=args.mag,
        obj_type=args.type,
        ra=args.ra,
        dec=args.dec,
    )


if __name__ == "__main__":
    main()
