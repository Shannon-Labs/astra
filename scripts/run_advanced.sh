#!/bin/bash

# ASTRA Advanced Discovery Runner
# Automated discovery pipeline with enhanced scoring
# Usage: ./run_advanced.sh [options]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 ASTRA Advanced Discovery System${NC}"
echo "====================================="
echo "Starting enhanced discovery run at $(date)"
echo ""

# Change to script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d "astra_env" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo "   Run: python3 -m venv astra_env"
    echo "   Then: source astra_env/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source astra_env/bin/activate
echo -e "${GREEN}✓${NC} Environment activated"
echo ""

# Create output directory for this run
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT_DIR="discovery_run_$TIMESTAMP"
mkdir -p "$OUTPUT_DIR"

echo "📁 Output directory: $OUTPUT_DIR"
echo ""

# Step 1: Run bright transient scraper (baseline)
echo "🔭 Step 1: Collecting bright transients..."
python src/transient_scraper.py > "$OUTPUT_DIR/bright_transients.log" 2>&1

if [ -f "bright_transients.csv" ]; then
    cp bright_transients.csv "$OUTPUT_DIR/"
    COUNT=$(wc -l < bright_transients.csv)
    echo -e "${GREEN}✓${NC} Found $((COUNT-1)) bright transients"
else
    echo -e "${YELLOW}⚠️${NC} No bright transients found"
fi
echo ""

# Step 2: Run advanced discovery pipeline
echo "🔬 Step 2: Running advanced discovery pipeline..."
python src/advanced_discovery.py > "$OUTPUT_DIR/advanced_discovery.log" 2>&1

if [ -f "astra_advanced_report.txt" ]; then
    cp astra_advanced_report.txt "$OUTPUT_DIR/"
    cp advanced_transients_catalog.csv "$OUTPUT_DIR/"
    
    # Count anomalies
    ANOMALY_COUNT=$(grep -c "Score:" astra_advanced_report.txt || echo "0")
    echo -e "${GREEN}✓${NC} Found $ANOMALY_COUNT high-priority anomalies"
else
    echo -e "${RED}❌${NC} Advanced discovery pipeline failed"
    echo "   Check $OUTPUT_DIR/advanced_discovery.log for details"
fi
echo ""

# Step 3: Package top discoveries
echo "📦 Step 3: Packaging top discoveries..."
if [ -f "astra_advanced_report.txt" ]; then
    # Extract top 3 anomalies and package them
    python scripts/package_top_discoveries.py "$OUTPUT_DIR/astra_advanced_report.txt" > "$OUTPUT_DIR/packaging.log" 2>&1
    echo -e "${GREEN}✓${NC} Packaged discoveries"
fi
echo ""

# Step 4: Generate summary
echo "📊 Step 4: Generating summary..."
{
    echo "ASTRA Advanced Discovery Run Summary"
    echo "===================================="
    echo "Date: $(date)"
    echo "Output: $OUTPUT_DIR"
    echo ""
    
    if [ -f "$OUTPUT_DIR/bright_transients.csv" ]; then
        echo "Bright Transients:"
        echo "------------------"
        head -5 "$OUTPUT_DIR/bright_transients.csv" | column -t -s ','
        echo ""
    fi
    
    if [ -f "$OUTPUT_DIR/astra_advanced_report.txt" ]; then
        echo "Top Anomalies:"
        echo "--------------"
        head -20 "$OUTPUT_DIR/astra_advanced_report.txt"
        echo ""
    fi
    
    echo "Files generated:"
    ls -lh "$OUTPUT_DIR"
    
} > "$OUTPUT_DIR/summary.txt"

echo -e "${GREEN}✓${NC} Summary generated"
echo ""

# Step 5: Create/update stable symlinks
echo "🔗 Step 5: Updating stable symlinks..."
rm -f latest_discovery advanced_report latest_catalog
ln -s "$OUTPUT_DIR" latest_discovery
ln -s "$OUTPUT_DIR/astra_advanced_report.txt" advanced_report
ln -s "$OUTPUT_DIR/advanced_transients_catalog.csv" latest_catalog
echo -e "${GREEN}✓${NC} Symlinks updated"
echo ""

# Step 6: Show top discoveries
echo "🎯 Step 6: Top discoveries this run:"
echo "-----------------------------------"
if [ -f "astra_advanced_report.txt" ]; then
    # Extract top 3 anomalies
    awk '/HIGH-PRIORITY ANOMALIES/,/IMMEDIATE FOLLOW-UP/' astra_advanced_report.txt | \
    grep -E "^[0-9]+\." | head -3
else
    echo -e "${YELLOW}⚠️${NC} No anomalies found"
fi
echo ""

# Final status
echo "==================================="
echo -e "${GREEN}✅ Advanced discovery run complete!${NC}"
echo ""
echo "Results: $OUTPUT_DIR"
echo "Latest:  latest_discovery/"
echo "Summary: latest_discovery/summary.txt"
echo "Report:  advanced_report (symlink)"
echo ""
echo "Quick commands:"
echo "  cat latest_discovery/summary.txt"
echo "  cat advanced_report"
echo "  ls -lh latest_discovery/"
echo ""
echo "Next run: Add to crontab for automation"
echo "  crontab -e"
echo "  # Run daily at 2 AM"
echo "  0 2 * * * cd $PROJECT_ROOT && ./scripts/run_advanced.sh"