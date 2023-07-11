"""
Run Kraken2
"""

import os
import sys
import subprocess

# import utils.py from this dir
import amplikraken.utils



class KrakenRunner:
    def __init__(self, db, binary="kraken2",  threads=1, confidence=0.0, output=None, verbose=False, keepunclassified=False, workdir=None):
        self.binary = binary
        self.db = db
        self.threads = threads
        self.confidence = confidence
        self.output = output
        self.verbose = verbose
        self.workdir = workdir if workdir else os.getcwd()
        self.keepunclassified = keepunclassified
        self._cmd = None
        self._process = None
        self._output = None

        # Check kraken version
        try:
            vercmd = [self.binary, "--version"]
            cmd_output = subprocess.check_output(vercmd, stderr=subprocess.STDOUT, universal_newlines=True)
            # Output is two lines, the first like "Kraken versoin x.y.z"
            # and the second like "Build date: ..."
            # Split the first line on spaces and take the last element
            self.version = cmd_output.split("\n")[0].split(" ")[-1]
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error running Kraken2 ({self.binary}): {e.output}")
        


    def run(self, file1, file2=None):
        cmd = [self.binary, "--db", self.db, "--threads", str(self.threads), "--confidence", str(self.confidence)]
        if file2:
            cmd += ["--paired", "--use-names",  file1, file2]
        else:
            cmd += ["--use-names",  file1]
        
        self._cmd = amplikraken.utils.list_to_string(cmd)
        print(" ".join(self._cmd))
        # Use subprocess to run the command, streaming stdout to a function process_line(line)
        self._process = subprocess.Popen(
            self._cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        # Read the output line by line as it is generated
        for line in self._process.stdout:
            self.process_line(line)

        # Wait for the process to finish and get the return code
        return_code = self._process.wait()

        # Handle any error messages from stderr
        error_message = self._process.stderr.read()

        # Check the return code and return appropriate output
        if return_code == 0:
            return True
        else:
            raise RuntimeError(f"Error running Kraken2: {error_message}")

    def process_line(self, line):
        # Process each line of the output (e.g., store or display)
        # Implement your logic here
        if not self.keepunclassified and line.startswith("U"):
            return
            
        print(line, end="")
        pass