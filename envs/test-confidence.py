"""
At present, we have not yet developed a confidence score with a probabilistic interpretation for Kraken 2. 
However, we have developed a simple scoring scheme that has yielded good results for us, 
and we've made that available in Kraken 2 through use of the --confidence option to kraken2. 
The approach we use allows a user to specify a threshold score in the [0,1] interval; 
the classifier then will adjust labels up the tree until the label's score (described below) meets or exceeds that threshold. 

If a label at the root of the taxonomic tree would not have a score exceeding the threshold, 
the sequence is called unclassified by Kraken 2 when this threshold is applied.

A sequence label's score is a fraction C/Q, where C is the number of k-mers mapped to LCA values in the clade rooted at the label, and Q is the number of k-mers in the sequence that lack an ambiguous nucleotide (i.e., they were queried against the database). Consider the example of the LCA mappings in Kraken 2's output given earlier:

"562:13 561:4 A:31 0:1 562:3" would indicate that:

the first 13 k-mers mapped to taxonomy ID #562
the next 4 k-mers mapped to taxonomy ID #561
the next 31 k-mers contained an ambiguous nucleotide
the next k-mer was not in the database
the last 3 k-mers mapped to taxonomy ID #562
In this case, ID #561 is the parent node of #562. 

Here, a label of #562 for this sequence would have a score of C/Q = (13+3)/(13+4+1+3) = 16/21 0.761  

A label of #561 would have a score of C/Q = (13+4+3)/(13+4+1+3) = 20/21 = 0.95. 

If a user specified a --confidence threshold over 16/21, the classifier would adjust the original label from #562 to #561; if the threshold was greater than 20/21, the sequence would become unclassified.
"""

def kraken2_confidence_unrankedtaxonomy(kmer_string, taxid=None):
    kmer_counts = {}
    total_kmers = 0

    # Parse the k-mer string
    kmer_list = kmer_string.split()

    for kmer in kmer_list:
        taxonID, count = kmer.split(":")
        if taxonID == "A":
            # Skip ambiguous k-mers
            continue
        count = int(count)
        kmer_counts[taxonID] = kmer_counts.get(taxonID, 0) + count
        total_kmers += count

    print(kmer_counts, total_kmers)
    # Calculate the confidence scores
    confidence_scores = {tid: kmer_counts[tid] / total_kmers for tid in kmer_counts}

    if taxid is not None:
        # Return the confidence score for the specified taxid
        return confidence_scores.get(str(taxid), 0)
    else:
        # Return the confidence score of the most common taxid
        most_common_taxid = max(confidence_scores, key=confidence_scores.get)
        return confidence_scores[most_common_taxid]

kmer_string = "562:13 561:4 A:31 0:1 562:3"

# Calculate the confidence score for taxid 562
for taxid in [562, 561, 0, "A"]:
    confidence_score = kraken2_confidence_unrankedtaxonomy(kmer_string, taxid)
    print(f"{taxid}\t Confidence score:", confidence_score)

# Calculate the confidence score for the most common taxid
confidence_score_most_common = kraken2_confidence_unrankedtaxonomy(kmer_string)
print("Confidence score for the most common taxid:", confidence_score_most_common)
