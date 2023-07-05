#!/usr/bin/env python3
import os
import sys
import argparse
import pandas as pd
import amplikraken.kraken

def main():
    args = argparse.ArgumentParser(description='Merge kraken output files')
    args.add_argument('TSV', type=str, nargs='+', help='Path to kraken output files (not reports)')
    args.add_argument('-o', '--output', type=str, help='Output file name')
    args.add_argument('-c', '--confidence', type=float, default='0.0', help='Confidence')
    args.add_argument('--verbose', action="store_true", help='Verbose output')
    args.add_argument('--version', help='Print version and exit', action='version', version=amplikraken.__version__)
    args = args.parse_args()

    # Check files
    kraken_outputs = []
    for f in args.TSV:
        if not os.path.exists(f):
            print(f"File not found: {f}")
            sys.exit(1)
        kraken = amplikraken.kraken.KrakenOutput(name=os.path.basename(f))
        kraken.load(f)
        kraken.collapse()
        kraken_outputs.append(kraken)
        print("Loading ", kraken.name, len(kraken), file=sys.stderr)
        
    # Merge all dfs by TaxID, each having kraken.name aas column name of their counts
    merged = pd.concat([k.table for k in kraken_outputs], axis=1, sort=False)
    merged = merged.fillna(0)
    print(merged.head())
        
