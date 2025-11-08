# ASTRA Publication Guide

Transform your ASTRA discoveries into peer-reviewed astronomical publications.

## Discovery to Publication Workflow

### Phase 1: Initial Discovery (Days 0-2)

**Immediate Actions:**
- **Verify the discovery** using the verification pipeline
- **Check for prior reports** on TNS, ATel, and literature
- **Assess follow-up feasibility** (brightness, coordinates, visibility)
- **File discovery reports** (ATel, TNS) if novel

```bash
# Run comprehensive verification
python scripts/verify_discovery.py AT2025XXXX

# Generate ATel report draft
python scripts/generate_atel_report.py AT2025XXXX
```

### Phase 2: Follow-up Observations (Days 2-14)

**Spectroscopy Priority:**
- **High-priority objects** (Score ≥ 7.0) - Immediate spectroscopy
- **Medium-priority objects** (Score 5.0-6.9) - Spectroscopy within 48 hours
- **Target facilities**: 2-4m class telescopes preferred

**Photometric Monitoring:**
- **Multi-band imaging**: B, V, R, I filters
- **Cadence**: Daily for first week, then every 2-3 days
- **Duration**: Until peak + 50 days past peak

**Coordinate Planning:**
```python
# Use the observation planner
from src.observation_planner import generate_observation_plan

plan = generate_observation_plan(
    object_id='AT2025abao',
    telescope='2m_class',
    location='latitude,longitude'
)
print(plan)
```

### Phase 3: Analysis and Classification (Days 7-30)

**Spectral Analysis:**
- **Line identification**: Hα, Hβ, He I, Ca II, Fe II
- **Velocity measurements**: Expansion velocities
- **Classification comparison**: Template matching
- **Host galaxy redshift**: From narrow host lines

**Light Curve Analysis:**
- **Peak magnitude determination**: Maximum brightness
- **Rise/fall time calculation**: t_rise, t_decline
- **Color evolution**: (B-V), (V-R) over time
- **Absolute magnitude**: Using distance estimates

### Phase 4: Manuscript Preparation (Days 30-60)

## Manuscript Structure

### 1. Abstract (250 words)

**Essential Elements:**
- Discovery method (ASTRA system)
- Object classification and properties
- Key observations and measurements
- Scientific significance

**Example Template:**
```
We report the discovery of AT2025XXXX, a [rare phenomenon]
discovered by the ASTRA autonomous transient detection system
on [date]. Follow-up observations reveal [key characteristics].
The object shows [unusual features] suggesting [scientific interpretation].
```

### 2. Introduction (2-3 pages)

**Content Outline:**
- **Background on phenomenon** (e.g., Luminous Red Novae)
- **Discovery challenges** and importance of automated systems
- **ASTRA system capabilities** and methodology
- **This discovery's significance**
- **Paper organization**

**Key Points to Emphasize:**
- **Novelty**: First ASTRA discovery of this type
- **Methodology**: Automated detection without API access
- **Importance**: Rare phenomena, nearby distance, etc.

### 3. Observations (3-4 pages)

**Photometry Section:**
- **Telescopes and instruments** used
- **Observation log** (Table 1)
- **Data reduction procedures** (calibration, standardization)
- **Photometric uncertainties**

**Spectroscopy Section:**
- **Spectral resolution** and wavelength coverage
- **Observation dates** and phases
- **Data reduction pipeline** (bias, flat, wavelength calibration)
- **Line identifications** and measurements

**Table 1: Observation Log**
```
Date (UT)     MJD      Telescope  Instrument  Filter  Exp(s)  Mag    Err
2025-01-15    58620.1  2.1m       DFOSC      R       300     15.2   0.02
...
```

### 4. Analysis (4-5 pages)

**Light Curve Analysis:**
- **Peak magnitude**: M_max = [value] ± [error] mag
- **Rise time**: t_rise = [value] ± [error] days
- **Decline rate**: Δm_15 = [value] mag in first 15 days
- **Absolute magnitude**: M_abs = [value] ± [error] mag

**Spectral Analysis:**
- **Key spectral features**: Hα emission at [velocity] km/s
- **Line evolution** over time
- **Temperature estimates** from line ratios
- **Comparison with similar objects**

**Host Galaxy Analysis:**
- **Host identification** and morphology
- **Redshift measurement**: z = [value] ± [error]
- **Host properties**: mass, SFR, metallicity if available

### 5. Discussion (2-3 pages)

**Scientific Interpretation:**
- **Classification justification** based on observations
- **Physical interpretation**: explosion mechanism, progenitor
- **Comparison with similar objects** in literature
- **Implications for understanding** of phenomenon class

**ASTRA System Performance:**
- **Detection efficiency** and timeline
- **Advantages of automated systems**
- **Potential for future discoveries**
- **Limitations and improvements**

### 6. Conclusions (1 page)

**Key Findings:**
1. **Discovery**: AT2025XXXX is a [classification]
2. **Properties**: [key measurements and their significance]
3. **Implications**: [broader scientific impact]
4. **Method validation**: ASTRA effectiveness demonstrated

### 7. Acknowledgments

**Essential Acknowledgments:**
- **Telescope time** allocation committees
- **Observatory staff** and support astronomers
- **ASTRA development team** and contributors
- **Funding sources** (if any)
- **Data resources** (TNS, SIMBAD, Gaia, etc.)

### 8. References

**Citation Requirements:**
- **Previous similar discoveries** (minimum 10-15 references)
- **Methodology papers** for analysis techniques
- **Instrument and telescope manuals**
- **Database documentation** (SIMBAD, NED, Gaia)
- **ASTRA system paper** (this repository)

**Format Example:**
```
[1] Smith, J., et al. 2023, ApJ, 945, 123
[2] ASTRA Collaboration 2025, this repository
[3] Tonry, J. L., et al. 2012, ApJ, 750, 99
```

## Data Requirements

### Photometric Data
**Format:** CSV with columns
```csv
mjd,filter,magnitude,error
58620.1,R,15.2,0.02
58621.2,R,15.0,0.02
```

### Spectroscopic Data
**FITS files** with proper headers:
- **Wavelength calibration** (CRVAL1, CDELT1)
- **Flux calibration** (BZERO, BSCALE)
- **Observation metadata** (DATE-OBS, EXPTIME)

**Repository Submission:**
```bash
# Prepare data for publication
mkdir publication_data/
cp *.fits publication_data/
cp photometry.csv publication_data/
cp observation_log.txt publication_data/
```

## Journal Submission Strategy

### Target Journals (by priority)

**High-Impact (Discovery):**
- **Nature Astronomy**: For truly novel discoveries
- **Science**: Exceptional discoveries with broad impact
- **ApJ Letters**: Rapid publication of important results

**Specialized Astronomy:**
- **The Astrophysical Journal**: Standard for astronomical discoveries
- **Monthly Notices of RAS**: UK-based alternative
- **Astronomy & Astrophysics**: European journal
- **The Astronomical Journal**: North American alternative

**Rapid Communications:**
- **Research Notes of the AAS**: For brief reports
- **ATel**: For initial discovery announcements

### Submission Checklist

**Before Submission:**
- [ ] **Data completeness**: All observations included
- [ ] **Analysis reproducibility**: Code and data available
- [ ] **Figures publication-ready**: High resolution, proper labeling
- [ ] **Tables formatted**: Journal-specific formatting
- [ ] **References complete**: All cited works included
- [ ] **Word count limits**: Follow journal guidelines
- [ ] **Author agreements**: All authors have approved

**Figures Requirements:**
- **Resolution**: 300 DPI minimum
- **Format**: EPS or PDF for vector graphics
- **Color**: Use colorblind-friendly palettes
- **Labels**: Clear, readable fonts (Arial, Helvetica)

## Code and Data Sharing

### GitHub Repository Setup
```bash
# Create publication branch
git checkout -b publication/at2025xxxx

# Add analysis code
mkdir analysis/
cp discovery_analysis.py analysis/
cp light_curve_fitting.py analysis/

# Add data (ensure public domain)
mkdir data/
cp publication_data/* data/

# Create README
echo "# AT2025XXXX Analysis" > data/README.md
echo "Data and code for paper on AT2025XXXX discovery" >> data/README.md
```

### Zenodo Deposit
- **Create DOI** for data and code
- **Version control** with proper tagging
- **License specification** (CC-BY 4.0 recommended)
- **Permanent archive** for peer review

## Ethical Considerations

### Publication Ethics
- **Authorship criteria**: All authors meet ICMJE standards
- **Data integrity**: No manipulation or selective reporting
- **Proper attribution**: Credit previous work appropriately
- **Conflict disclosure**: Declare any competing interests

### Professional Conduct
- **Rapid communication**: Inform community promptly
- **Data sharing**: Make observations publicly available
- **Coordination**: Check for duplicate discoveries
- **Follow-up coordination**: Share with other observers

## Post-Publication Activities

### Community Engagement
- **Press releases**: For exceptional discoveries
- **Social media**: Professional announcement (Twitter, etc.)
- **Conference presentations**: Share results at meetings
- **Database updates**: Update TNS and other catalogs

### Long-term Impact
- **Citation tracking**: Monitor publication impact
- **Follow-up coordination**: Encourage additional observations
- **Educational use**: Share with students and public
- **Method improvements**: Refine ASTRA based on experience

## Success Metrics

### Publication Success Indicators
- **Journal tier**: High-impact vs. specialized journals
- **Citation rate**: Track citation performance
- **Media coverage**: Press mentions and public interest
- **Community uptake**: Other groups using methodology

### ASTRA System Validation
- **Discovery efficiency**: Successful follow-up rate
- **Classification accuracy**: Verification through spectroscopy
- **Timeline advantage**: Faster than traditional methods
- **Cost effectiveness**: Resource utilization compared to alternatives

By following this guide, you'll transform your ASTRA discoveries into high-quality, peer-reviewed astronomical publications that contribute to our understanding of the transient universe.