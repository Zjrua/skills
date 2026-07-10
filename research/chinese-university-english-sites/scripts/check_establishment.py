#!/usr/bin/env python3
"""Check establishment dates for multiple university English sites.

Usage: python3 check_establishment.py site1_url site2_url ...

For each site, checks if pre-2026 articles exist (established before 2026).
Returns: site_url | established_before_2026 | evidence
"""
import subprocess, re, sys

def fetch(url, timeout=8):
    try:
        r = subprocess.run(
            ["curl", "-sL", "-m", str(timeout), "-A", 
             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
             url],
            capture_output=True, text=True, timeout=timeout+5
        )
        return r.stdout, r.returncode
    except:
        return "", 1

def find_pre_2026_dates(html):
    dates = []
    for m in re.finditer(r'20(2[0-5]|1[0-9]|0[0-9])[-/](\d{1,2})[-/](\d{1,2})', html):
        dates.append(m.group(0))
    for m in re.finditer(r'20(2[0-5]|1[0-9]|0[0-9])年(\d{1,2})月', html):
        dates.append(m.group(0))
    return sorted(set(dates))

def check_site(url):
    body, code = fetch(url)
    if code != 0 and code != 200:
        return url, "inaccessible", "HTTP error"
    
    pre_dates = find_pre_2026_dates(body)
    if pre_dates:
        return url, "yes", pre_dates[0]
    
    # Try a few more pages
    sep = "&" if "?" in url else "?"
    for p in [2, 3, 5]:
        body2, _ = fetch(f"{url}{sep}page={p}")
        pre_dates = find_pre_2026_dates(body2)
        if pre_dates:
            return url, "yes", pre_dates[0]
    
    return url, "unknown", "no pre-2026 dates found"

if __name__ == "__main__":
    urls = sys.argv[1:]
    if not urls:
        print("Usage: python3 check_establishment.py URL1 URL2 ...")
        sys.exit(1)
    
    for url in urls:
        url, status, evidence = check_site(url)
        print(f"{url} | {status} | {evidence}")
