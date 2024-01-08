import unittest
from unittest.mock import MagicMock

from src.extendedLeaf.power import EntityDistributor, SolarPower, GridPower, PowerDomain


class MyTestCase(unittest.TestCase):
    """ Unit tests for the entity distributor, logic tests will be carried out in integration testing. """
    def setUp(self):
        # Create a mock environment for testing
        self.mock_env = MagicMock()
        # Create a mock associated entity for testing
        self.mock_entity = MagicMock()
        self.mock_entity.power_model = MagicMock()

        # Provided valid entry data
        self.entity_distributor = EntityDistributor(entity_distributor_method=None,
                                                smart_distribution=True, static_entities=False)
        self.mock_env.now = 600
        self.power_domain = PowerDomain(self.mock_env, name="Power Domain 1", powered_entities=[self.mock_entity],
                                        start_time_str="00:00:00", update_interval=1, entity_distributor=self.entity_distributor)
        self.high_priority_power_source = SolarPower(self.mock_env, "Test Solar Power Source", "test_data.csv",
                                                power_domain=self.power_domain, priority=0)
        self.high_priority_power_source.update_power_available()
        self.low_priority_power_source = GridPower(self.mock_env, "Test Solar Power Source",
                                              power_domain=self.power_domain, priority=5)
        self.low_priority_power_source.update_power_available()


    def test_default_update_entity_distribution_method_dynamic_smart(self):
        """ Test to ensure that the side effect causes the entity to move to the desirable power source. """
        # Create mock power sources and entities
        self.mock_env.now = 600
        self.low_priority_power_source.powered_entities = [self.mock_entity]
        # Entity initially is in a lower power source
        self.mock_entity.power_model.power_source = self.low_priority_power_source
        self.mock_entity.power_model.update_sensitive_measure.return_value = 30.0

        # Mock the get_current_time method to return a specific value (600 in this case)
        self.entity_distributor.default_update_entity_distribution_method_dynamic(self.high_priority_power_source,
                                                                              self.power_domain)

        # Assert that the entity is now associated with the higher priority power source
        self.assertEqual([self.mock_entity], self.high_priority_power_source.powered_entities)
        self.assertEqual([], self.low_priority_power_source.powered_entities)

    def test_default_update_enitity_distribution_method_dynamic_not_smart(self):
        """ Test to ensure that the side effect causes the entity to not move to the desirable power source. """

        # Create mock power sources and entities
        self.low_priority_power_source.powered_entities = [self.mock_entity]
        # Entity initially is in a lower power source
        self.mock_entity.power_model.power_source = self.low_priority_power_source
        self.mock_entity.power_model.update_sensitive_measure.return_value = 30.0
        self.entity_distributor.smart_distribution = False

        # Mock the get_current_time method to return a specific value (600 in this case)
        self.entity_distributor.default_update_entity_distribution_method_dynamic(self.high_priority_power_source,
                                                                              self.power_domain)

        # Assert that the entity is now associated with the higher priority power source
        self.assertEqual([], self.high_priority_power_source.powered_entities)
        self.assertEqual([self.mock_entity], self.low_priority_power_source.powered_entities)

    def default_update_entity_distribution_method_static(self):
        """ Tests will be carried out in Integration testing as too many side effects to model for unit, logic
            is similar to dynamic so assumed correct."""


if __name__ == '__main__':
    unittest.main()
