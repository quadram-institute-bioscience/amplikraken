# This file contains classes and functions for handling fastq files
import os

class FastqDataset:
    def __init__(self, name, forward=None, reverse=None, basename=False) -> None:
        self.name = name
        self.forward = forward if forward is not None else None
        self.reverse = reverse if reverse is not None else None
        self.paired = False
        self.valid = False
        self.basename = basename
        self._update()
    
    def setR1(self, r1):
        if os.path.isfile(r1):
            self.forward = os.path.abspath(r1) if os.path.isfile(r1) else None
        else:
            raise FileNotFoundError(f"File {r1} not found")
        self._update()
    
    def setR2(self, r2):
        if os.path.isfile(r2):
            self.reverse = os.path.abspath(r2) if os.path.isfile(r2) else None
        else:
            raise FileNotFoundError(f"File {r2} not found")
        self._update()

    def setName(self, name):
        self.name = name

    def __str__(self) -> str:
        fwd = os.path.basename(self.forward) if self.basename else self.forward
        rev = os.path.basename(self.reverse) if self.basename else self.reverse
        if self.paired and self.forward is not None and self.reverse is not None:
            return f"PE:{self.name} -> [{fwd}, {rev}]"
        elif self.paired:
            return f"PE:{self.name} -> [{fwd}, {rev}] (incomplete)"
        else:
            return f"SE:{self.name} -> {fwd}"
        
    def __repr__(self) -> str:
        return f"FastqDataset({self.name}, {self.forward}, {self.reverse})"
        
    def _update(self):
        if self.forward is not None and os.path.isfile(self.forward):
            self.forward = os.path.abspath(self.forward)
        #else:
        #    self.forward = None

        if self.reverse is not None and os.path.isfile(self.reverse):
            self.reverse = os.path.abspath(self.reverse)
        #else:
        #    self.reverse = None
        

        if self.forward is not None and self.reverse is not None:
            self.paired = True
            self.valid = True
        elif self.forward is None and self.reverse is None:
            self.paired = False
            self.valid = True
        else:
            # Invalid but we don't want to raise an exception
            self.paired = True
            self.valid = False

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, FastqDataset):
            return self.forward == __value.forward and self.reverse == __value.reverse
        return NotImplemented
        
    
    def __lt__(self, __value: object) -> bool:
        return self.name < __value.name

class FastqDatasets:
    def __init__(self, name="FQ", ext=None, basename=False) -> None:
        self.datasets = {}
        self.ext = ext
        
        self.display = "basename" if basename == True else "absolute"
        self.name = name
    
    def add(self, dataset):
        if dataset.name in self.datasets:
            raise ValueError(f"Dataset {dataset.name} already exists")
        else:
            self.datasets[dataset.name] = dataset

    def addFile(self, datasetname, path, rev=False):
        if datasetname in self.datasets:
            if rev:
                self.datasets[datasetname].setR2(path)
            else:
                self.datasets[datasetname].setR1(path)
        else:
            if rev:
                self.datasets[datasetname] = FastqDataset(datasetname, reverse=path)
            else:
                self.datasets[datasetname] = FastqDataset(datasetname, forward=path)
    
    def stripSuffix(self, suffix):
        if suffix is None:
            return
        for name, data in self.datasets.items():
            self.datasets[name].setName(name.replace(suffix, ''))

    # Sort datasets by name
    def sort(self):
        self.datasets = dict(sorted(self.datasets.items()))

    def __len__(self):
        return len(self.datasets)

    def __str__(self) -> str:
        sampleList = []
        nl = "\n"
        for dataset in self.datasets.values():
            sampleList.append(str(dataset))
        return f"FastqDatasets({self.name}) ext={self.ext} len={len(self)}\n{nl.join(sampleList)}"
    
    def __repr__(self) -> str:
        return f"@FastqDatasets({self.name})"
    
    def displayBasename(self):
        self.display = "basename"
        for dataset in self.datasets.values():
            dataset.basename = True

    def displayAbsolute(self):
        self.display = "absolute"
        for dataset in self.datasets.values():
            dataset.basename = False
  
def pairedend_samples_from_path(path, ext=None, r1=None, r2=None):
    exts = [ext] if ext is not None else ['.fastq', '.fq', '.fastq.gz', '.fq.gz']
    r1s = [r1] if r1 is not None else ['_R1_', '_1.', '_r1', '_R1.', '_1_001', '_r1_001']
    r2s = [r2] if r2 is not None else ['_R2_', '_2.', '_r2', '_R2.', '_2_001', '_r2_001']

    
    
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    
    # among [exts] extension, which is the most common in files?
    ext_count = {}
    for file in files:
        for ext in exts:
            if file.endswith(ext):
                ext_count[ext] = ext_count.get(ext, 0) + 1
    most_common_ext = None
    max_count = 0
    for ext, count in ext_count.items():
        if count > max_count:
            most_common_ext = ext
            max_count = count

    if most_common_ext is None:
        raise ValueError(f"No files with supported extensions ({exts}) found in the directory.\n{len(files)} files found: {files}")
    
    samples = FastqDatasets(name=os.path.basename(os.path.abspath(path)), ext=most_common_ext)
    # Now, for each file with the most common extension, check if it is a R1 or R2
    for file in files:
        if not file.endswith(most_common_ext):
            continue
        for i in range(len(r1s)):
            if r1s[i] in file and r2s[i] in file:
                # Cannot be
                continue
            elif r1s[i] in file:
                # Assume it's R1
                sample = file.replace(r1s[i], '')
                samples.addFile(sample, os.path.join(path, file), rev=False)
            elif r2s[i] in file:
                # Assume it's R2
                sample = file.replace(r2s[i], '')
                samples.addFile(sample, os.path.join(path, file), rev=True)
            else:
                continue
        
  
    suff = getSuffixFromList(samples.datasets.keys())

    # Strip suff to all samples
    samples.stripSuffix(suff)
    return samples
    


def getSuffixFromList(lst):
    """
    Identify the common suffix in a list of strings
    """
    # Identify the common suffix
    lst = list(lst)
    splitters = ['_', '.', '-']
    suffix = None
    char = None
    
    for i in range(1, min([len(s) for s in lst])):
        if len(set([s[-i] for s in lst])) == 1:
            char = lst[0][-i]
            suffix = char + suffix if suffix is not None else char
            
        else:
            break
    
    for i, c in enumerate(suffix):
        if c in splitters:
            suffix = suffix[i+1:]
        else:
            break
    return suffix