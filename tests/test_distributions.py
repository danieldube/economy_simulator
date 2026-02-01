import random

import pytest

from wealth_sim_germany.data.distributions import DistributionFactory


def test_distribution_factory_register_and_sample_parametric():
    factory = DistributionFactory()
    factory.register("constant", lambda rng, conditions=None: 42)

    sample = factory.sample("constant", random.Random(0))

    assert sample == 42


def test_distribution_factory_empirical_sampling_with_conditions():
    factory = DistributionFactory()
    records = [
        {"value": 10.0, "conditions": {"region": "north"}},
        {"value": 20.0, "conditions": {"region": "south"}},
        {"value": 30.0, "conditions": {"region": "north"}},
    ]
    factory.register_empirical("regional_income", records)

    rng = random.Random(1)
    sample = factory.sample("regional_income", rng, conditions={"region": "north"})

    assert sample in {10.0, 30.0}


def test_distribution_factory_missing_distribution_raises():
    factory = DistributionFactory()

    with pytest.raises(KeyError):
        factory.sample("missing", random.Random(0))
