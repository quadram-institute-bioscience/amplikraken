import pytest
import amplikraken.kraken

def test_confidence():
    z = '3:83 52:11 0:11 3:81 |:| 3:3 0:3 52:6 3:81'
    assert amplikraken.kraken.str_to_confidence(z) ==  0.75

def test_taxonomy_splitter():
    z = 'Bacteria (taxid 3)'
    assert amplikraken.kraken.taxonomy_splitter(z) == (3, 'Bacteria')

def test_taxonomy_splitter_spaces():
    z = 'More bacteria (taxid 10000000)'
    assert amplikraken.kraken.taxonomy_splitter(z) == (10000000, 'More bacteria')

def test_taxonomy_fails_badformat1():
    z = 'Bacteria (taxid 3'
    with pytest.raises(Exception):
        amplikraken.kraken.taxonomy_splitter(z)


def test_taxonomy_fails_isint():
    z = '3'
    assert amplikraken.kraken.taxonomy_splitter(z) == (3, None)

def test_taxonomy_fails_non_int_taxid():
    z = 'Bacteria (taxid abc)'
    with pytest.raises(Exception):
        amplikraken.kraken.taxonomy_splitter(z)

def test_kraken_record():
    # Create record from line, check its string representation is the same
    line = 'C	M00967:43:000000000-A3JHG:1:1101:17025:1426	2911	251|251	3:83 52:11 3:1 52:5 3:5 52:11 3:10 459:5 874:2 459:3 52:5 3:17 1:14 3:3 1:1 3:19 0:1 2882:4 3:17 |:| 3:43 1:1 3:3 1:36 3:15 0:10 2911:5 0:11 3:3 0:3 52:6 3:81'
    kr = amplikraken.kraken.KrakenRecord(line=line)
    assert str(kr) == line

def test_kraken_record_len():
    # Length is the sum of paired reads lengths
    line = 'C	M00967:43:000000000-A3JHG:1:1101:17025:1426	2911	251|251	3:83 52:11 3:1 52:5 3:5 52:11 3:10 459:5 874:2 459:3 52:5 3:17 1:14 3:3 1:1 3:19 0:1 2882:4 3:17 |:| 3:43 1:1 3:3 1:36 3:15 0:10 2911:5 0:11 3:3 0:3 52:6 3:81'
    kr = amplikraken.kraken.KrakenRecord(line=line)
    assert len(kr) == 502

def test_kraken_record_len_invalid():
    # Wrong length, simply return 0
    line = 'C	M00967:43:000000000-A3JHG:1:1101:17025:1426	2911	x|x	3:83 52:11 3:1 52:5 3:5 52:11 3:10 459:5 874:2 459:3 52:5 3:17 1:14 3:3 1:1 3:19 0:1 2882:4 3:17 |:| 3:43 1:1 3:3 1:36 3:15 0:10 2911:5 0:11 3:3 0:3 52:6 3:81'
    kr = amplikraken.kraken.KrakenRecord(line=line)
    assert len(kr) == 0

def test_fastqdataset_repr_and_eq():
    from amplikraken.fastq import FastqDataset
    ds1 = FastqDataset('s1', 'r1.fq', 'r2.fq')
    ds2 = FastqDataset('s1', 'r1.fq', 'r2.fq')
    assert isinstance(repr(ds1), str)
    assert ds1 == ds2
