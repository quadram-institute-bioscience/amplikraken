#!/usr/bin/env python

from ete3 import NCBITaxa
import os
import sys
import argparse

def main():
    ncbi = NCBITaxa()

    args = argparse.ArgumentParser(description='Do taxon things')
    args.add_argument("-k", action="store_true", help="Treat as kraken output")
    args.add_argument('taxaid', type=str, nargs='+', help='Taxon names')
    args = args.parse_args()

    if len(args.taxaid) < 1:
        print("ERROR: Invalid number of files", file=sys.stderr)
        sys.exit(1)

    taxa = []
    names = []

    # Put the integers in args.taxaid in taxa and the strings in names
    if not args.k:
        for taxaid in args.taxaid:
            try:
                taxa.append(int(taxaid))
            except ValueError:
                names.append(taxaid)
        
        taxid2name = ncbi.get_taxid_translator(taxa)
        print(taxid2name)
        # {9443: u'Primates', 9606: u'Homo sapiens'}

        name2taxid = ncbi.get_name_translator(names)
        print(name2taxid)
        # {'Homo sapiens': [9606], 'primates': [9443]}
        exit()

    # Kraken
    items = {}
    array = []
    for bit in args.taxaid:
        temp = bit.split(" ")
        array.extend(temp)


    for info in array:
        if "|" in info:
            continue
        if not ":" in info:
            raise "Invalid kraken format"
        tax, quant = info.split(":")
        if tax == "A":
            continue
        try:
            items[tax] = int(quant) if not tax in items else int(quant) + items[tax]
        except Exception as e:
            print("Skipping " + quant, file=sys.stderr)

    for tax, quant in items.items():
        species = ncbi.get_taxid_translator([tax])
        
        # check if tax is a key of species
         
        if int(tax) in species.keys():
            lineage = ncbi.get_lineage(tax)
            print("ok", tax, f"{quant}X", species, lineage, sep="\t")

    


if __name__=="__main__":
    main()