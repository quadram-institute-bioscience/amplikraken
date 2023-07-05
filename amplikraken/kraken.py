"""
C	M00967:43:000000000-A3JHG:1:1101:17025:1426	2911	251|251	3:83 52:11 3:1 52:5 3:5 52:11 3:10 459:5 874:2 459:3 52:5 3:17 1:14 3:3 1:1 3:19 0:1 2882:4 3:17 |:| 3:43 1:1 3:3 1:36 3:15 0:10 2911:5 0:11 3:3 0:3 52:6 3:81
C	M00967:43:000000000-A3JHG:1:1101:17549:1611	1102	251|250	3:179 1102:5 3:1 1102:5 535:4 3:1 535:5 307:3 3:5 307:1 3:8 |:| 3:9 307:1 3:5 307:3 535:5 3:1 535:4 1102:5 3:1 1102:5 3:122 1102:11 535:8 3:1 535:1 3:8 535:2 3:24
C	M00967:43:000000000-A3JHG:1:1101:15982:1786	1102	251|250	3:26 535:2 21:3 3:5 535:1 21:1 535:11 3:1 535:9 3:1 535:21 307:5 535:13 307:1 535:10 3:5 307:2 3:73 535:4 3:1 535:5 1102:8 0:4 1383:1 0:4 |:| 3:9 535:1 3:8 535:5 3:1 535:4 3:73 307:2 3:5 535:10 307:1 535:11 0:76 1099:2 0:8
C	M00967:43:000000000-A3JHG:1:1101:17592:2407	1102	251|250	3:27 307:1 3:8 21:1 3:1 307:8 535:1 1102:8 3:13 535:6 307:5 1102:32 3:106 |:| 3:107 1102:22 0:5 1102:5 541:5 0:62 1102:2 0:8
"""
import pandas as pd


class KrakenOutput:
    def __init__(self, name=None, minconfidence=0.0, unclassified=False, reads=False) -> None:
        self.name = name
        self.minconfidence = minconfidence
        self.unclassified = unclassified
        self.readname = reads
        self.table = pd.DataFrame()

    def __len__(self):
        return self.table.shape[0]
    def load(self, filename):
        try:
            self.table = pd.read_csv(filename, sep="\t", header=None, names=["Classification", "Read", "TaxID", "Len", "kmers"])
            #Check if the file is a report
            # 1. Column Classification must be either "C" or "U"
            if not self.table['Classification'].isin(['C', 'U']).all():
                raise Exception(f"\n----\nError loading kraken output from {filename}:\n  Column Classification must be either 'C' or 'U'")
            # 2. Column TaxID must be an integer
            if not self.table['TaxID'].astype(str).str.isdigit().all():
                raise Exception(f"\n----\nError loading kraken output from {filename}:\n  Column TaxID must be an integer")
            
            # Set type of TaxID to int
            self.table['TaxID'] = self.table['TaxID'].astype(int)

            # Strip unclassified
            if not self.unclassified:
                self.table = self.table[self.table['Classification'] == 'C']

            # Remove reads
            if not self.readname:
                self.table = self.table.drop(columns=['Read'])
            # Add column "Confidence": str_to_confidence(kmers)
            self.table['Confidence'] = self.table['kmers'].apply(str_to_confidence)

            if self.minconfidence > 0:
                self.table = self.table[self.table['Confidence'] >= self.minconfidence]

            self.table = self.table.drop(columns=['kmers'])
        except Exception as e:
            raise Exception(f"Error loading kraken output from {filename}: {e}")
        return self
    
    def __str__(self) -> str:
        return self.table.to_string()
    
    def collapse(self):
        if self.table.empty:
            return self.table
        
        # Collapse by TaxID
        self.table.drop(columns=['Classification', 'Len', 'Confidence'], inplace=True)

        # Add columnt "Count" and group by TaxID having "Count" as sum of records
        self.table[self.name] = 1
        self.table = self.table.groupby(['TaxID']).sum().reset_index()
        # Index is TaxID
        self.table.set_index('TaxID', inplace=True)
        

def str_to_confidence(s):
    """
    String: 3:83 52:11 3:1 52:5 3:5 52:11 3:10 459:5 874:2 459:3 52:5 3:17 1:14 3:3 1:1 3:19 0:1 2882:4 3:17 |:| 3:43 1:1 3:3 1:36 3:15 0:10 2911:5 0:11 3:3 0:3 52:6 3:81
    Output: defined-kmers / total-kmers
    """
    total = 0
    defined = 0
    for pair in s.split():
        kmer, count = pair.split(":")
        if kmer == "|":
            continue
        total += 1
        if kmer != "0":
            defined += 1
    return defined / total

def taxonomy_splitter(taxonomy_string):
    """
    Input: 'Bacteria (taxid 3)'
    Output: 3, Bacteria
    """
    # Check format "STRING (taxid INT)"
    if not taxonomy_string.endswith(")"):
        raise Exception(f"Error parsing taxonomy string {taxonomy_string}: does not end with `)`")
    
    # Split by " (taxid "
    taxonomy_string = taxonomy_string[:-1].split(" (taxid ")
    if len(taxonomy_string) != 2:
        raise Exception(f"Error parsing taxonomy string {taxonomy_string}: does not contain ` (taxid `")
    
    # Check if taxid is an integer
    try:
        taxid = int(taxonomy_string[1])
    except:
        raise Exception(f"Error parsing taxonomy string {taxonomy_string}: taxid {taxid} is not an integer")
    
    return taxid, taxonomy_string[0]
    