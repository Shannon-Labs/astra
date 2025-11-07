#!/usr/bin/env python3
"""
ASTRA: Enhanced Discovery Pipeline
Integrates coordinate extraction, Gaia cross-matching, and advanced scoring
"""

import pandas as pd
import numpy as np
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
from astropy.coordinates import SkyCoord
import astropy.units as u

try:
    from astroquery.gaia import Gaia
    GAIA_AVAILABLE = True
except:
    GAIA_AVAILABLE = False
    print("⚠️  Gaia not available")

class EnhancedDiscoveryEngine:
    """Enhanced discovery with coordinate extraction and Gaia matching"""
    
    def __init__(self):
        self.transients = pd.DataFrame()
        self.anomalies = []
        
    def scrape_with_coordinates(self):
        """Scrape transients and extract coordinates from text"""
        print("🌐 Scraping Rochester page for transients with coordinates...")
        
        url = "http://www.rochesterastronomy.org/supernova.html"
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        text = soup.get_text()
        
        # Pattern for transient entries with coordinates
        pattern = r'(AT\d{4}[\w]+).*?discovered\s+(\d{4}/\d{2}/\d{2}).*?R\.A\.\s*=\s*([\dhms\.]+).*?Decl\.\s*=\s*([\+\-\d\s\.\']+).*?Mag\s+([\d\.]+).*?Type\s+([\w\?]+)'
        
        matches = re.findall(pattern, text)
        
        transients = []
        for match in matches[:100]:  # Limit to avoid duplicates
            transient_id, date, ra, dec, mag, obj_type = match
            
            transients.append({
                'id': transient_id,
                'date': date,
                'ra': ra.strip(),
                'dec': dec.strip(),
                'mag': float(mag),
                'type': obj_type,
                'source': 'Rochester_Entries_With_Coords'
            })
        
        df = pd.DataFrame(transients)
        print(f"   📊 Found {len(df)} transients with coordinates")
        
        if not df.empty:
            # Remove duplicates
            df = df.drop_duplicates('id')
            print(f"   📊 After deduplication: {len(df)} transients")
            
            print(f"   📈 Magnitude range: {df['mag'].min():.1f} - {df['mag'].max():.1f}")
            print(f"   📍 All objects have coordinates")
        
        return df
    
    def cross_match_with_gaia(self, transients, radius=3.0):
        """Cross-match with Gaia DR3 for proper motion and parallax"""
        if not GAIA_AVAILABLE:
            print("⚠️  Gaia not available, skipping cross-match")
            return transients
        
        print(f"🔭 Cross-matching {len(transients)} objects with Gaia DR3...")
        
        results = []
        
        for idx, row in transients.iterrows():
            try:
                # Parse coordinates
                coord = SkyCoord(row['ra'], row['dec'], unit=(u.hourangle, u.deg))
                
                # Query Gaia
                job = Gaia.cone_search_async(coord, radius * u.arcsec)
                gaia_results = job.get_results()
                
                if len(gaia_results) > 0:
                    # Found match - take nearest
                    star = gaia_results[0]
                    
                    # Calculate separation
                    star_coord = SkyCoord(star['ra'], star['dec'], unit=u.deg)
                    separation = coord.separation(star_coord).arcsec
                    
                    results.append({
                        'id': row['id'],
                        'gaia_match': True,
                        'gaia_dist_arcsec': float(separation),
                        'pmra': float(star['pmra']) if 'pmra' in star.keys() and not np.isnan(star['pmra']) else None,
                        'pmdec': float(star['pmdec']) if 'pmdec' in star.keys() and not np.isnan(star['pmdec']) else None,
                        'parallax': float(star['parallax']) if 'parallax' in star.keys() and not np.isnan(star['parallax']) else None,
                        'g_mag': float(star['phot_g_mean_mag']) if 'phot_g_mean_mag' in star.keys() else None,
                        'gaia_ra': float(star['ra']),
                        'gaia_dec': float(star['dec'])
                    })
                    
                    pm = np.sqrt(results[-1]['pmra']**2 + results[-1]['pmdec']**2) if results[-1]['pmra'] and results[-1]['pmdec'] else 0
                    print(f"   ✓ {row['id']}: Gaia G={results[-1]['g_mag']:.1f}, "
                          f"pm={pm:.0f} mas/yr, "
                          f"sep={separation:.1f}")
                else:
                    results.append({
                        'id': row['id'],
                        'gaia_match': False
                    })
                    
            except Exception as e:
                print(f"   ✗ {row['id']}: Error - {e}")
                results.append({
                    'id': row['id'],
                    'gaia_match': False,
                    'error': str(e)
                })
        
        # Merge results
        gaia_df = pd.DataFrame(results)
        transients = transients.merge(gaia_df, on='id', how='left')
        
        return transients
    
    def calculate_enhanced_score(self, row):
        """Calculate enhanced anomaly score with Gaia data"""
        score = 0.0
        reasons = []
        
        # Brightness anomaly
        if pd.notna(row['mag']):
            if row['mag'] < 15.0:
                score += 4.0
                reasons.append(f"Extremely bright (m={row['mag']:.1f})")
            elif row['mag'] < 16.0:
                score += 3.0
                reasons.append(f"Very bright (m={row['mag']:.1f})")
            elif row['mag'] > 20.0:
                score += 2.0
                reasons.append(f"Very faint (m={row['mag']:.1f})")
        
        # Unknown type
        if row['type'] == 'unknown' or row['type'] == 'unk':
            score += 2.0
            reasons.append("Unknown classification")
        
        # LRN (Luminous Red Nova) - very rare
        if 'LRN' in row['type']:
            score += 5.0
            reasons.append("Luminous Red Nova (rare stellar merger)")
        
        # CV with unusual brightness
        if 'CV' in row['type'] and pd.notna(row['mag']):
            if row['mag'] < 16.0:
                score += 4.0
                reasons.append("CV at unusual brightness")
        
        # Gaia match indicates stellar object
        if row.get('gaia_match', False):
            score += 1.0
            reasons.append("Gaia match (stellar object)")
            
            # High proper motion
            if pd.notna(row.get('pmra')) and pd.notna(row.get('pmdec')):
                pm = np.sqrt(row['pmra']**2 + row['pmdec']**2)
                if pm > 100:
                    score += 4.0
                    reasons.append(f"Very high proper motion ({pm:.0f} mas/yr)")
                elif pm > 50:
                    score += 3.0
                    reasons.append(f"High proper motion ({pm:.0f} mas/yr)")
            
            # Parallax distance
            if pd.notna(row.get('parallax')) and row['parallax'] > 0:
                distance_pc = 1.0 / row['parallax'] * 1000
                if distance_pc < 500:
                    score += 3.0
                    reasons.append(f"Very nearby ({distance_pc:.0f} pc)")
                elif distance_pc < 1000:
                    score += 2.0
                    reasons.append(f"Nearby ({distance_pc:.0f} pc)")
        
        return score, reasons
    
    def find_enhanced_anomalies(self, transients):
        """Find anomalies using enhanced scoring"""
        print("🔍 Finding enhanced anomalies...")
        
        anomalies = []
        
        for idx, row in transients.iterrows():
            score, reasons = self.calculate_enhanced_score(row)
            
            if score >= 5.0:
                anomaly = {
                    'id': row['id'],
                    'mag': row['mag'],
                    'type': row['type'],
                    'score': score,
                    'reasons': reasons
                }
                
                # Add RA/Dec if available
                if 'ra' in row and pd.notna(row['ra']):
                    anomaly['ra'] = row['ra']
                    anomaly['dec'] = row['dec']
                
                # Add Gaia data if available
                if row.get('gaia_match', False):
                    anomaly.update({
                        'gaia_match': True,
                        'pmra': row.get('pmra'),
                        'pmdec': row.get('pmdec'),
                        'parallax': row.get('parallax'),
                        'g_mag': row.get('g_mag'),
                        'gaia_dist_arcsec': row.get('gaia_dist_arcsec')
                    })
                
                anomalies.append(anomaly)
        
        # Sort by score
        anomalies = sorted(anomalies, key=lambda x: x['score'], reverse=True)
        
        print(f"   🎯 Found {len(anomalies)} enhanced anomalies")
        return anomalies
    
    def generate_enhanced_report(self, anomalies):
        """Generate enhanced discovery report"""
        report = []
        report.append("=" * 80)
        report.append("ASTRA ENHANCED DISCOVERY REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)
        report.append("")
        
        if not anomalies:
            report.append("No high-priority anomalies found.")
            return "\n".join(report)
        
        # Summary stats
        has_gaia = sum(1 for a in anomalies if a.get('gaia_match', False))
        has_coords = sum(1 for a in anomalies if 'ra' in a)
        report.append(f"📊 Summary: {len(anomalies)} anomalies, {has_coords} with coordinates, {has_gaia} with Gaia matches")
        report.append("")
        
        # Top anomalies
        report.append("🎯 HIGH-PRIORITY ANOMALIES")
        report.append("-" * 40)
        report.append("")
        
        for i, obj in enumerate(anomalies, 1):
            report.append(f"{i}. {obj['id']} (Score: {obj['score']:.1f}/10.0)")
            report.append(f"   Magnitude: {obj['mag']:.1f}")
            report.append(f"   Type: {obj['type']}")
            
            if 'ra' in obj:
                report.append(f"   Position: {obj['ra']} {obj['dec']}")
            
            report.append(f"   Reasons: {', '.join(obj['reasons'])}")
            
            # Gaia info
            if obj.get('gaia_match', False):
                report.append(f"   Gaia: G={obj['g_mag']:.1f}")
                
                if pd.notna(obj.get('parallax')):
                    dist = 1.0 / obj['parallax'] * 1000
                    report.append(f"   Distance: ~{dist:.0f} pc")
                
                if pd.notna(obj.get('pmra')) and pd.notna(obj.get('pmdec')):
                    pm = np.sqrt(obj['pmra']**2 + obj['pmdec']**2)
                    report.append(f"   Proper Motion: {pm:.0f} mas/yr")
            
            report.append("")
        
        # Follow-up recommendations
        report.append("🔭 FOLLOW-UP RECOMMENDATIONS")
        report.append("-" * 40)
        report.append("")
        
        for i, obj in enumerate(anomalies[:3], 1):
            report.append(f"{i}. {obj['id']}:")
            
            if obj['score'] >= 7.0:
                priority = "HIGH"
                instrument = "Low-res spectrograph"
                exposure = "300-600s"
            elif obj['score'] >= 5.0:
                priority = "MEDIUM"
                instrument = "Low-res spectrograph"
                exposure = "600-900s"
            else:
                priority = "LOW"
                instrument = "Photometry"
                exposure = "Monitoring"
            
            report.append(f"   Priority: {priority}")
            report.append(f"   Instrument: {instrument}")
            report.append(f"   Exposure: {exposure}")
            report.append(f"   Goal: Classification and redshift")
            report.append("")
        
        return "\n".join(report)
    
    def run_enhanced_pipeline(self):
        """Run the complete enhanced discovery pipeline"""
        print("🚀 ASTRA Enhanced Discovery Pipeline Starting...")
        print("=" * 60)
        
        # Phase 1: Scrape with coordinates
        transients = self.scrape_with_coordinates()
        
        if transients.empty:
            print("❌ No transients with coordinates found")
            print("   Falling back to basic scraper...")
            # Fallback to original scraper
            from astra_discovery_engine import AstraDiscoveryEngine
            basic_engine = AstraDiscoveryEngine()
            transients = basic_engine.scrape_rochester_page()
        
        if transients.empty:
            print("❌ No transients found at all. Aborting.")
            return None
        
        # Phase 2: Gaia cross-match (if we have coords)
        if 'ra' in transients.columns:
            transients = self.cross_match_with_gaia(transients)
        
        # Phase 3: Find enhanced anomalies
        anomalies = self.find_enhanced_anomalies(transients)
        
        # Phase 4: Generate enhanced report
        report = self.generate_enhanced_report(anomalies)
        
        print("=" * 60)
        print("✅ Enhanced discovery pipeline complete!")
        
        return {
            'transients': transients,
            'anomalies': anomalies,
            'report': report
        }

if __name__ == "__main__":
    engine = EnhancedDiscoveryEngine()
    results = engine.run_enhanced_pipeline()
    
    if results:
        print("\n" + results['report'])
        
        # Save enhanced report
        with open('astra_enhanced_report.txt', 'w') as f:
            f.write(results['report'])
        print("\n📄 Enhanced report saved to: astra_enhanced_report.txt")
        
        # Save enhanced data
        results['transients'].to_csv('enhanced_transients_catalog.csv', index=False)
        print("📊 Enhanced data saved to: enhanced_transients_catalog.csv")
        
        # Show top anomaly
        if results['anomalies']:
            top = results['anomalies'][0]
            print(f"\n🎯 Top Anomaly: {top['id']} (Score: {top['score']:.1f})")
            print(f"   {', '.join(top['reasons'])}")