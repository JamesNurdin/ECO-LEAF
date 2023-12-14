import unittest
from unittest.mock import MagicMock

from src.extendedLeaf.power import NodeDistributor, SolarPower, GridPower, PowerDomain


class MyTestCase(unittest.TestCase):
    """ Unit tests for the node distributor, loigc tests will be carried out in intergration testing. """
    def setUp(self):
        # Create a mock environment for testing
        self.mock_env = MagicMock()
        # Create a mock associated node for testing
        self.mock_node = MagicMock()
        self.mock_node.power_model = MagicMock()

        # Provided valid entry data
        self.node_distributor = NodeDistributor(node_distributor_method=None,
                                                smart_distribution=True, static_nodes=False)
        self.mock_env.now = 600
        self.power_domain = PowerDomain(self.mock_env, name="Power Domain 1", associated_nodes=[self.mock_node],
                                        start_time_str="00:00:00", update_interval=1, node_distributor=self.node_distributor)
        self.high_priority_power_source = SolarPower(self.mock_env, "Test Solar Power Source", "test_data.csv",
                                                power_domain=self.power_domain, priority=0)
        self.low_priority_power_source = GridPower(self.mock_env, "Test Solar Power Source",
                                              power_domain=self.power_domain, priority=5)

    def test_default_update_node_distribution_method_dynamic_smart(self):
        """ Test to ensure that the side effect causes the node to move to the desirable power source. """
        # Create mock power sources and nodes
        self.mock_env.now = 600
        self.low_priority_power_source.associated_nodes = [self.mock_node]
        # Node initially is in a lower power node
        self.mock_node.power_model.power_source = self.low_priority_power_source
        self.mock_node.power_model.update_sensitive_measure.return_value = 30.0

        # Mock the get_current_time method to return a specific value (600 in this case)
        self.node_distributor.default_update_node_distribution_method_dynamic(self.high_priority_power_source,
                                                                              self.power_domain)

        # Assert that the node is now associated with the higher priority power source
        self.assertEqual([self.mock_node], self.high_priority_power_source.associated_nodes)
        self.assertEqual([], self.low_priority_power_source.associated_nodes)

    def test_default_update_node_distribution_method_dynamic_not_smart(self):
        """ Test to ensure that the side effect causes the node to not move to the desirable power source. """

        # Create mock power sources and nodes
        self.low_priority_power_source.associated_nodes = [self.mock_node]
        # Node initially is in a lower power node
        self.mock_node.power_model.power_source = self.low_priority_power_source
        self.mock_node.power_model.update_sensitive_measure.return_value = 30.0
        self.node_distributor.smart_distribution = False

        # Mock the get_current_time method to return a specific value (600 in this case)
        self.node_distributor.default_update_node_distribution_method_dynamic(self.high_priority_power_source,
                                                                              self.power_domain)

        # Assert that the node is now associated with the higher priority power source
        self.assertEqual([], self.high_priority_power_source.associated_nodes)
        self.assertEqual([self.mock_node], self.low_priority_power_source.associated_nodes)

    def default_update_node_distribution_method_static(self):
        """ Tests will be carried out in Integration testing as too many side effects to model for unit, logic
            is similar to dynamic so assumed correct."""


if __name__ == '__main__':
    unittest.main()
