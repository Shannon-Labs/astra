#!/usr/bin/env python3
"""
Package Top Discoveries Script
Takes ASTRA report and packages the top discoveries into detailed reports
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def extract_top_discoveries(report_file, max_discoveries=3):
    """Extract top discoveries from report file"""

    discoveries = []

    if not os.path.exists(report_file):
        print(f"❌ Report file not found: {report_file}")
        return discoveries

    with open(report_file, "r") as f:
        content = f.read()

    # Parse the report to extract high-priority discoveries
    lines = content.split("\n")
    in_anomaly_section = False

    for line in lines:
        line = line.strip()

        # Look for anomaly section
        if "HIGH-PRIORITY ANOMALIES" in line:
            in_anomaly_section = True
            continue

        if "IMMEDIATE FOLLOW-UP" in line:
            break

        # Extract discovery lines
        if in_anomaly_section and line and (line[0].isdigit() or "AT2025" in line):
            # Parse discovery information
            if "AT2025" in line and ("Score:" in line or "LRN" in line or "CV" in line):
                discoveries.append(line)

                if len(discoveries) >= max_discoveries:
                    break

    return discoveries


def create_discovery_package(discovery_text, output_dir):
    """Create a detailed package for a single discovery"""

    # Extract object ID from the discovery text
    object_id = None
    for token in discovery_text.split():
        if token.startswith("AT2025"):
            object_id = token
            break

    if not object_id:
        return None

    # Create discovery directory
    discovery_dir = os.path.join(output_dir, object_id)
    os.makedirs(discovery_dir, exist_ok=True)

    # Parse discovery details
    details = parse_discovery_details(discovery_text, object_id)

    # Create reports
    create_atea_report(details, discovery_dir)
    create_observation_plan(details, discovery_dir)
    create_data_package(details, discovery_dir)

    return discovery_dir


def parse_discovery_details(text, object_id):
    """Parse discovery details from text"""

    details = {
        "object_id": object_id,
        "discovery_date": datetime.now().strftime("%Y-%m-%d"),
        "discovery_time": datetime.now().strftime("%H:%M:%S UTC"),
        "raw_text": text,
    }

    # Extract score
    if "Score:" in text:
        score_text = text.split("Score:")[1].split()[0]
        details["score"] = float(score_text.replace("(", "").replace(")", ""))

    # Extract magnitude
    if "m=" in text:
        for part in text.split():
            if part.startswith("m="):
                details["magnitude"] = float(part[2:])
                break

    # Extract type
    if ")" in text and "(" in text:
        type_start = text.find("(") + 1
        type_end = text.find(")")
        if type_start > 0 and type_end > type_start:
            obj_type = text[type_start:type_end]
            details["type"] = obj_type

    # Extract classification reason
    if "-" in text:
        reason_part = text.split("-", 1)[-1].strip()
        details["classification_reason"] = reason_part

    return details


def create_atea_report(details, output_dir):
    """Create ATel-style report"""

    report = f"""ATel #{datetime.now().strftime('%Y')}: {details['object_id']} - High Priority Transient Discovery

{details['object_id']} discovered by ASTRA autonomous discovery system

Authors: ASTRA Collaboration <astra@shannonlabs.io>
Affiliation: Shannon Labs
Date: {details['discovery_date']} {details['discovery_time']}
Subject: {details['object_id']} - {details.get('type', 'Unknown')} discovery

We report the discovery of {details['object_id']}, identified by the ASTRA autonomous
transient discovery system on {details['discovery_date']}.

Object Information:
- Designation: {details['object_id']}
- Type: {details.get('type', 'Unknown')}
- Magnitude: {details.get('magnitude', 'N/A')}
- Discovery Score: {details.get('score', 'N/A')}
- Classification Reason: {details.get('classification_reason', 'N/A')}

The object was automatically flagged for high priority based on its anomalous
characteristics in the ASTRA multi-factor scoring system.

Follow-up observations are strongly encouraged, particularly spectroscopic
classification to confirm the object type.

Coordinates: [Insert from catalog cross-match when available]
Host Galaxy: [Determine from cross-matching]

For more information about this discovery, contact the ASTRA team at
astra@shannonlabs.io.

This discovery was made using the ASTRA (Autonomous System for Transient Research
& Analysis) pipeline, which automatically processes publicly available transient
lists to identify scientifically interesting objects without requiring API access.

---

Classification: Uncertain (Follow-up required)
Follow-up Priority: High
Recommended Facilities: 2m+ class telescopes for spectroscopy
"""

    report_file = os.path.join(output_dir, f"{details['object_id']}_ATel_report.txt")
    with open(report_file, "w") as f:
        f.write(report)


def create_observation_plan(details, output_dir):
    """Create observation planning report"""

    plan = f"""Observation Plan for {details['object_id']}

Generated by ASTRA on {details['discovery_date']}

TARGET INFORMATION:
------------------
Object ID: {details['object_id']}
Type: {details.get('type', 'Unknown')}
Current Magnitude: {details.get('magnitude', 'N/A')}
Discovery Score: {details.get('score', 'N/A')}

IMMEDIATE OBSERVATIONS (Next 48 hours):
---------------------------------------

1. SPECTROSCOPY (High Priority)
   Facility: 2m+ class telescope
   Resolution: R ~ 1000-3000
   Wavelength range: 4000-9000 Å
   Exposure time: ~1800s (adjust for magnitude)
   Goal: Confirm classification, measure velocities

2. MULTI-BAND PHOTOMETRY
   Filters: B, V, R, I
   Cadence: Every 12 hours
   Goal: Build light curve, measure colors
   Precision: 0.05 mag or better

FOLLOW-UP OBSERVATIONS (Next 2 weeks):
--------------------------------------

1. POLARIMETRY (If available)
   Goal: Check for intrinsic polarization
   Priority: Medium

2. RADIO OBSERVATIONS (If facilities available)
   Frequency: 1-8 GHz
   Goal: Search for radio emission
   Priority: Low

COORDINATES:
------------
[Automatically extract from cross-matching]
RA: [HH:MM:SS]
Dec: [±DD:MM:SS]

VISIBILITY:
-----------
Moon distance: [Calculate]
Airmass constraints: < 2.0
Optimal observing window: [Calculate]

CONTACTS:
---------
For coordination: astra@shannonlabs.io
Observation updates: Please share via GitHub issues

NOTES:
------
{details.get('classification_reason', 'N/A')}

---
This plan was automatically generated by ASTRA v2.0.0
"""

    plan_file = os.path.join(output_dir, f"{details['object_id']}_observation_plan.txt")
    with open(plan_file, "w") as f:
        f.write(plan)


def create_data_package(details, output_dir):
    """Create data package with available information"""

    data = {
        "discovery": details,
        "metadata": {
            "generated_by": "ASTRA v2.0.0",
            "generation_time": datetime.now().isoformat(),
            "pipeline_version": "2.0.0",
            "data_sources": [
                "Rochester Astronomy Supernova Page",
                "Automated classification",
                "Cross-matching with astronomical catalogs",
            ],
        },
        "observation_status": {
            "spectroscopy": "pending",
            "photometry": "pending",
            "polarimetry": "pending",
            "radio": "pending",
        },
    }

    data_file = os.path.join(output_dir, f"{details['object_id']}_data.json")
    with open(data_file, "w") as f:
        json.dump(data, f, indent=2)

    # Create README
    readme = f"""# {details['object_id']} Discovery Package

Generated by ASTRA Autonomous Discovery System on {details['discovery_date']}

## Files in this package:

- `{details['object_id']}_ATel_report.txt` - ATel-style discovery report
- `{details['object_id']}_observation_plan.txt` - Detailed follow-up observations
- `{details['object_id']}_data.json` - Machine-readable discovery data

## Discovery Summary:

**Object ID:** {details['object_id']}
**Type:** {details.get('type', 'Unknown')}
**Magnitude:** {details.get('magnitude', 'N/A')}
**Score:** {details.get('score', 'N/A')}
**Classification Reason:** {details.get('classification_reason', 'N/A')}

## Next Steps:

1. Review the observation plan
2. Coordinate spectroscopic observations
3. Begin photometric monitoring
4. Submit to TNS/ATel if confirmed as new discovery
5. Share results with the astronomical community

## Contact:

For questions or coordination: astra@shannonlabs.io
Report issues or improvements: https://github.com/Shannon-Labs/astra/issues

---
This package was automatically generated by ASTRA v2.0.0
"""

    readme_file = os.path.join(output_dir, "README.md")
    with open(readme_file, "w") as f:
        f.write(readme)


def main():
    """Main packaging function"""

    parser = argparse.ArgumentParser(
        description="Package top ASTRA discoveries for follow-up",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("report_file", help="Path to ASTRA discovery report file")
    parser.add_argument(
        "--output",
        "-o",
        default="packaged_discoveries",
        help="Output directory for packaged discoveries",
    )
    parser.add_argument(
        "--max", "-m", type=int, default=3, help="Maximum number of discoveries to package"
    )

    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output, exist_ok=True)

    print("📦 Packaging Top Discoveries")
    print("==========================")
    print(f"Reading report: {args.report_file}")
    print(f"Output directory: {args.output}")
    print()

    # Extract top discoveries
    discoveries = extract_top_discoveries(args.report_file, args.max)

    if not discoveries:
        print("❌ No high-priority discoveries found in report")
        return 1

    print(f"Found {len(discoveries)} top discoveries:")
    for i, disc in enumerate(discoveries, 1):
        print(f"  {i}. {disc}")
    print()

    # Package each discovery
    packaged = []
    for disc in discoveries:
        print(f"Packaging: {disc.split()[1] if 'AT2025' in disc else 'Unknown'}")

        discovery_dir = create_discovery_package(disc, args.output)
        if discovery_dir:
            packaged.append(discovery_dir)
            print(f"  ✓ Created: {discovery_dir}")
        else:
            print(f"  ❌ Failed to package")

    print()
    print(f"🎉 Successfully packaged {len(packaged)} discoveries!")
    print(f"Location: {args.output}/")

    # Create summary
    summary = {
        "packaging_date": datetime.now().isoformat(),
        "total_discoveries": len(packaged),
        "source_report": args.report_file,
        "packages": [os.path.basename(p) for p in packaged],
    }

    summary_file = os.path.join(args.output, "packaging_summary.json")
    with open(summary_file, "w") as f:
        json.dump(summary, f, indent=2)

    return 0


if __name__ == "__main__":
    sys.exit(main())
