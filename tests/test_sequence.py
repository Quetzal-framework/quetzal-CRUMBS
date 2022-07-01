import pytest

from . context import crumbs

class TestSequence():

    def setup_method(self, test_method):
        pass

    def test_new(self):
        from crumbs import sequence
        s = sequence.Sequence(">HEADER","--ACGT")
        assert(s.header == "HEADER")
        assert(s.sequence == "--ACGT")

    def test_parse(self):
        from crumbs import sequence
        generator = sequence.fasta_parse("data/sequences.fasta")
        sequences = list(generator)
        assert(sequences[0].header == "QWER1")
        assert(sequences[0].sequence == "GGCAGATTCCCCCTA")
        assert(sequences[1].header == "AZER2")
        assert(sequences[1].sequence == "---CTGCACTCACCG")
