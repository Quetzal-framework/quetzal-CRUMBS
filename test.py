import unittest
from crumbs import sequence, bpp

class TestSequence(unittest.TestCase):
    def SetUp(self):
        pass

    def test_new(self):
        s = sequence.Sequence(">HEADER","--ACGT")
        self.assertEqual(s.header,"HEADER")
        self.assertEqual(s.sequence,"--ACGT")

    def test_parse(self):
        generator = sequence.fasta_parse("test_data/sequences.fasta")
        sequences = list(generator)
        self.assertEqual(sequences[0].header, "QWER1")
        self.assertEqual(sequences[0].sequence, "GGCAGATTCCCCCTA")
        self.assertEqual(sequences[1].header, "AZER2")
        self.assertEqual(sequences[1].sequence, "---CTGCACTCACCG")

class TestSequence(unittest.TestCase):
    def SetUp(self):
        pass

    def test_bpp_extract_probability(self):
        p1, p2 = bpp.extract_probabilities("test_data/bpp_output.txt")
        self.assertEqual(p1, 0.0)
        self.assertEqual(p2, 0.985)

if __name__=="__main__":
    unittest.main()
