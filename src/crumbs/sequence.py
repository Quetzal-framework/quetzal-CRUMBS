import re, os, random

class Sequence(object):
    """The Sequence object has a string *header* and various representations."""

    def __init__(self, header, seq):
        self.header = re.findall('^>(\S+)', header)[0]
        self.sequence = seq

    def __len__(self):
        return len(self.sequence)

    @property
    def phylip(self):
        return self.header + " " + self.sequence.replace('.','-') + "\n"

    @property
    def fasta(self):
        return ">" + self.header + "\n" + self.sequence + "\n"

def fasta_parse(path):
    """Reads the file at *path* and yields Sequence objects in a lazy fashion"""
    header = ''
    seq = ''
    with open(path) as f:
        for line in f:
            line = line.strip('\n')
            if line.startswith('>'):
                if header: yield Sequence(header, seq)
                header = line
                seq = ''
                continue
            seq += line
    yield Sequence(header, seq)

def fasta_to_phylip(fasta_file, phylip_file):
    """Reads the file at *fasta_file* and writes its phylip conversion to *phylip_file*"""
    # Check that the path is valid #
    if not os.path.exists(fasta_file): raise Exception("No file at %s." % fasta_file)
    # Use our two functions #
    seqs = fasta_parse(fasta_file)
    # Write the output to temporary file #
    temp_path = phylip_file + '.' + ''.join(random.choice(string.ascii_letters) for i in range(10))
    # Count the sequences #
    count = 0
    with open(temp_path, 'w') as f:
        for seq in seqs:
            f.write("^" + seq.phylip)
            count += 1
    # Add number of entries and length at the top #
    with open(temp_path, 'r') as old, open(phylip_file, 'w') as new:
        new.write(" " + str(count) + " " + str(len(seq)) + "\n")
        new.writelines(old)
    # Clean up #
    os.remove(temp_path)
    return
