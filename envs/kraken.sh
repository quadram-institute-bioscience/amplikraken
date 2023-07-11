#!/bin/bash

CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
DB="${ROOTDIR}/db/silva138"

if [[ ! -e $DB ]]; then
 echo "Download Silva 138 database to ${DB}"
 exit
fi

mkdir -p output
for R1 in ${ROOTDIR}/data/*_R1*;
do
    BASE=$(basename $R1 | cut -f 1 -d_)
    R2=${R1/_R1/_R2}
    if [[ ! -e output/${BASE}.report ]];
    then
        kraken2 --db $DB --threads 8 --report output/${BASE}.report --paired $R1 $R2 > output/${BASE}.tsv
    fi
    if [[ ! -e output/${BASE}.names.txt ]];
    then
        kraken2 --db $DB --threads 8  --use-names --paired $R1 $R2 > output/${BASE}.names.txt
    fi
done