import pytest
import sys

from . context import crumbs

class TestConvertPhylipToArlequin():

    output_filename = "test.arlequin"

    def setup_method(self, test_method):
        pass

    def teardown_method(self, test_method):
        from pathlib import Path
        import glob
        # Remove all occurrences files generated
        for p in Path(".").glob( self.output_filename):
            p.unlink()

    def test_phylip_to_alequin(self):
        from crumbs import phylip2arlequin
        phylip2arlequin.phylip2arlequin("data/seq.phyl", "data/imap.txt", self.output_filename)
