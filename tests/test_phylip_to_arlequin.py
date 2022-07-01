import pytest
import sys

from . context import crumbs
from crumbs import phylip2arlequin

def test_phylip_to_alequin(tmp_path):
    output_filename = tmp_path / "test.arlequin"
    phylip2arlequin.phylip2arlequin("data/seq.phyl", "data/imap.txt", output_filename)
