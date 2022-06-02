# avoid Module not found, see https://gideonbrimleaf.github.io/2021/01/26/relative-imports-python.html
import unittest
import sys

from . context import crumbs

from crumbs import get_successful_simulations_rowids
from crumbs import get_failed_simulations_rowids
from crumbs import retrieve_parameters
from crumbs import simulate_phylip_sequences

class TestGetSimulation(unittest.TestCase):
    def SetUp(self):
        pass

    def test_database_IDS(self):
        # Open the file:
        success_rowids = get_successful_simulations_rowids.get_successful_simulations_rowids("tests/data/database_with_newicks.db", "quetzal_EGG_1")
        self.assertEqual(success_rowids, list(range(1,31)))

        failed_rowids = get_failed_simulations_rowids.get_failed_simulations_rowids("tests/data/database_failed_newicks.db", "quetzal_EGG_1")
        self.assertEqual(failed_rowids, list(range(1,31)))

    def test_simulate_phylip(self):
        rowids = get_successful_simulations_rowids.get_successful_simulations_rowids("tests/data/database_with_newicks.db", "quetzal_EGG_1")

        sequence_size = 100
        scale_tree = 0.000025

        simulate_phylip_sequences.simulate_phylip_sequences("tests/data/database_with_newicks.db", "quetzal_EGG_1", rowids[0], sequence_size, scale_tree, "sim_test.phyl", "sim_test_temp")

        a = retrieve_parameters.retrieve_parameters("tests/data/database_with_newicks.db", "quetzal_EGG_1", rowids[0])
        b = retrieve_parameters.retrieve_parameters("tests/data/database_with_newicks.db", "quetzal_EGG_1", rowids[0], True)
        c = retrieve_parameters.retrieve_parameters("tests/data/database_with_newicks.db", "quetzal_EGG_1", rowids[0], False)

        self.assertEqual(a,b)

    @classmethod
    def tearDownClass(cls):
        from pathlib import Path
        Path("sim_test.phyl").unlink()


if __name__=="__main__":
    unittest.main()
