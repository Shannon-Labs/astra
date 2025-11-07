#!/usr/bin/env python3
"""Test the scraper and debug the page structure"""

import requests
from bs4 import BeautifulSoup
import re

# Test the main page
url = "http://www.rochesterastronomy.org/snimages/sn2025.html"
print(f"Fetching: {url}")

try:
    response = requests.get(url, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.text)} characters")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all pre tags
    pre_tags = soup.find_all('pre')
    print(f"\nFound {len(pre_tags)} <pre> tags")
    
    if pre_tags:
        # Show first 500 chars of first pre tag
        first_pre = pre_tags[0]
        print("\nFirst <pre> tag content (first 500 chars):")
        print(first_pre.text[:500])
        print("...")
        
        # Try to find transient patterns
        print("\nSearching for transient patterns...")
        pattern = r'(AT\d{4}[\w]+)\s*=.*?\s+discovered\s+(\d{4}/\d{2}/\d{2})'
        matches = re.findall(pattern, first_pre.text)
        print(f"Found {len(matches)} transient matches")
        
        if matches:
            print("\nFirst few matches:")
            for i, match in enumerate(matches[:5]):
                print(f"  {i+1}. {match[0]} on {match[1]}")
    else:
        print("No <pre> tags found!")
        # Show first 500 chars of page
        print("\nPage content (first 500 chars):")
        print(response.text[:500])
        
except Exception as e:
    print(f"Error: {e}")

# Also try the main supernova page
print("\n" + "="*60)
url2 = "http://www.rochesterastronomy.org/supernova.html"
print(f"\nFetching: {url2}")

try:
    response2 = requests.get(url2, timeout=30)
    print(f"Status: {response2.status_code}")
    
    soup2 = BeautifulSoup(response2.text, 'html.parser')
    pre_tags2 = soup2.find_all('pre')
    print(f"Found {len(pre_tags2)} <pre> tags")
    
    if pre_tags2:
        text = pre_tags2[0].text
        pattern = r'(AT\d{4}[\w]+)\s*=.*?\s+discovered\s+(\d{4}/\d{2}/\d{2})'
        matches = re.findall(pattern, text)
        print(f"Found {len(matches)} transient matches")
        
        if matches:
            print("\nFirst few matches:")
            for i, match in enumerate(matches[:5]):
                print(f"  {i+1}. {match[0]} on {match[1]}")
                
except Exception as e:
    print(f"Error: {e}")