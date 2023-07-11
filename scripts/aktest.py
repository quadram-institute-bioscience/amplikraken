#!/usr/bin/env python3
import os
import sys
import argparse
import pandas as pd
from amplikraken.run import KrakenRunner
import tempfile
def main():

    args = argparse.ArgumentParser(description='Merge kraken output files')
    
    args.add_argument('FQ', type=str, nargs='+', help='Path to FASTQ file 1 (required) and 2 (optional)')
    args.add_argument('-d', '--database', type=str, help='Database name (default: %(default)s)', default=os.environ.get('KRAKEN2_DEFAULT_DB'))
    args.add_argument('-o', '--output', type=str, help='Output file name')
    args.add_argument('-c', '--confidence', type=float, default='0.0', help='Minimum confidence score (default: %(default)s)')
    args.add_argument('-t', '--threads', type=int, default='1', help='Number of threads (default: %(default)s)')
    args.add_argument('-w', '--workdir', type=str,  help='Temporary directory (default: %(default)s)', default=tempfile.gettempdir())
    args.add_argument('--verbose', action="store_true", help='Verbose output')
    args = args.parse_args()

    # Check files
    if len(args.FQ) == 1:
        fq1 = args.FQ[0]
        fq2 = None
    elif len(args.FQ) == 2:
        fq1 = args.FQ[0]
        fq2 = args.FQ[1]
    else:
        print("ERROR: Invalid number of files", file=sys.stderr)
        sys.exit(1)
    
    # Check db
    if args.database is None:
        print(f"ERROR: No database specified", file=sys.stderr)
        sys.exit(1)
    elif not os.path.exists(os.path.join(args.database, "hash.k2d")):
        print(f"ERROR: Invalid database {args.database}", file=sys.stderr)
        sys.exit(1)

    runner = KrakenRunner(db=args.database, confidence=args.confidence, verbose=args.verbose)
    
    runner.run(fq1, fq2)

if __name__ == '__main__':
    main()
