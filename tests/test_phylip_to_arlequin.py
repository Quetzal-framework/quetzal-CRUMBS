# avoid Module not found, see https://gideonbrimleaf.github.io/2021/01/26/relative-imports-python.html
import unittest
import sys
sys.path.append("..")
# from src.crumbs import my_module

from src.crumbs import get_gbif

class TestConvertPhylipToArlequin(unittest.TestCase):

    output_filename = "test.arlequin"
    def SetUp(self):
        pass

    def test_phylip_to_alequin(self):
        from src.crumbs import phylip2arlequin
        phylip2arlequin.phylip2arlequin("data/seq.phyl", "data/imap.txt", self.output_filename)

    def tearDown(self):
        from pathlib import Path
        import glob
        # Remove all occurrences files generated
        for p in Path(".").glob( self.output_filename):
            p.unlink()

if __name__=="__main__":
    unittest.main()
