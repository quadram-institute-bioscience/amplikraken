import subprocess
import os

 
    
    
def has_kraken():
    return _has_tool('kraken2')

def has_seqfu():
    return _has_tool('seqfu')

def has_nextflow():
    if _has_tool('java', '--version'):
        return _has_tool('nextflow', '-version')
    else:
        return False
    
def _has_tool(binary, switch=None):
    switch_list = ['--version', '--help', '-h'] if switch is None else [switch]
    for switch in switch_list:
        try:
            subprocess.check_output([binary, switch])
            return True
        except:
            continue
    return False
 