import pytest

from crumbs import (
    get_failed_simulations_rowids,
    get_successful_simulations_rowids,
    retrieve_parameters,
    simulate_phylip_sequences,
)

from .context import crumbs


def test_database_IDS():
    # Open the file:
    success_rowids = (
        get_successful_simulations_rowids.get_successful_simulations_rowids(
            "data/database_with_newicks.db", "quetzal_EGG_1"
        )
    )
    assert success_rowids == list(range(1, 31))

    failed_rowids = get_failed_simulations_rowids.get_failed_simulations_rowids(
        "data/database_failed_newicks.db", "quetzal_EGG_1"
    )
    assert failed_rowids == list(range(1, 31))


def test_simulate_phylip(tmp_path):
    rowids = get_successful_simulations_rowids.get_successful_simulations_rowids(
        "data/database_with_newicks.db", "quetzal_EGG_1"
    )

    sequence_size = 100
    scale_tree = 0.000025

    out = tmp_path / "sim_test.phyl"

    simulate_phylip_sequences.simulate_phylip_sequences(
        "data/database_with_newicks.db",
        "quetzal_EGG_1",
        rowids[0],
        sequence_size,
        scale_tree,
        out,
        "sim_test_temp",
    )

    a = retrieve_parameters.retrieve_parameters(
        "data/database_with_newicks.db", "quetzal_EGG_1", rowids[0]
    )
    b = retrieve_parameters.retrieve_parameters(
        "data/database_with_newicks.db", "quetzal_EGG_1", rowids[0], True
    )
    c = retrieve_parameters.retrieve_parameters(
        "data/database_with_newicks.db", "quetzal_EGG_1", rowids[0], False
    )

    assert a == b
