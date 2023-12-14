import json
import os
import unittest
from unittest.mock import MagicMock

from src.extendedLeaf.file_handler import FileHandler
from src.extendedLeaf.power import PowerDomain, SolarPower


class TestPowerDomain(unittest.TestCase):
    """ Given a power domain.

    NOTE: The run method will be fully tested in the integration testing as the side effects are the main
          desire of the method being run. """

    def setUp(self):
        # Create a mock environment for testing
        self.mock_env = MagicMock()
        # Create a mock entity distributor
        self.mock_entity_distributor = MagicMock()
        self.mock_entity_distributor.static_entities = False
        # Create a mock power domain for testing
        self.mock_power_domain = MagicMock()
        self.mock_power_domain.start_time_string = "00:00:00"
        # Create a mock associated entity for testing
        self.mock_entity = MagicMock()
        self.mock_entity.power_model = MagicMock()

        # Provided valid entry data
        self.power_domain = PowerDomain(self.mock_env, "Test power domain", self.mock_entity_distributor, "12:00:00",
                                        [self.mock_entity], 15,
                                        [("19:40:00", False, (self.mock_power_domain.remove_entity, [self.mock_entity]))])

    def test_constructor(self):
        """ Test that the power domain class can be correctly created. """
        name = "Test power domain"
        string_start_time = "12:00:00"
        powered_entities = [self.mock_entity]
        update_interval = 15
        events = [("19:40:00", False, (self.mock_power_domain.remove_entity, [self.mock_entity]))]

        # Provided valid entry data
        power_domain = PowerDomain(self.mock_env, name, self.mock_entity_distributor, string_start_time,
                                   powered_entities, update_interval, events)
        self.assertEqual(power_domain.env, self.mock_env)
        self.assertEqual(power_domain.name, name)
        self.assertEqual(power_domain.entity_distributor, self.mock_entity_distributor)
        self.assertEqual(power_domain.start_time_string, string_start_time)
        self.assertEqual(power_domain.powered_entities, powered_entities)
        self.assertEqual(power_domain.update_interval, update_interval)
        self.assertEqual(power_domain.power_source_events, events)

        # Assert attributes constructed automatically
        self.assertEqual(power_domain.carbon_emitted, [])
        self.assertEqual(power_domain.start_time_index, 720)

        # Provide invalid data
        with self.assertRaises(ValueError):
            # invalid env
            PowerDomain(None, name, self.mock_entity_distributor, string_start_time,
                        powered_entities, update_interval, events)
            # invalid name
            PowerDomain(self.mock_env, None, self.mock_entity_distributor, string_start_time,
                        powered_entities, update_interval, events)
            # invalid start time
            PowerDomain(self.mock_env, None, self.mock_entity_distributor, "Invalid start time",
                        powered_entities, update_interval, events)
            # invalid update interval
            PowerDomain(self.mock_env, None, self.mock_entity_distributor, "Invalid start time",
                        powered_entities, -15, events)

    def test_run(self):
        """ PowerDomain.run() is the main driver for the carbon capture process, side effects will be explored in
            integration testing."""
        pass

    def test_record_power_source_carbon_released(self):
        """ Test that the relevant power information can be recorded properly. """
        mock_current_power_source = MagicMock()
        mock_entity_1 = MagicMock(name='mock_entity_1_name')
        mock_entity_2 = MagicMock(name='mock_entity_2_name')
        mock_current_power_source.powered_entities = [mock_entity_1, mock_entity_2]
        mock_entity_1.power_model.update_sensitive_measure.return_value = 50.0
        mock_current_power_source.get_current_carbon_intensity.return_value = 0.5
        mock_entity_2.power_model.update_sensitive_measure.return_value = 75.0
        expected_dict = {
            mock_entity_1.name: {'Power Used': 50.0, 'Carbon Intensity': 0.5, 'Carbon Released': 0.025},
            mock_entity_2.name: {'Power Used': 75.0, 'Carbon Intensity': 0.5, 'Carbon Released': 0.0375}
        }
        expected_carbon_released = 0.025 + 0.0375

        result_dict, result_carbon_released = \
            self.power_domain.record_power_source_carbon_released(mock_current_power_source)

        self.assertEqual(result_dict, expected_dict)
        self.assertEqual(result_carbon_released, expected_carbon_released)

        with self.assertRaises(ValueError):
            self.power_domain.record_power_source_carbon_released(None)

    def test_add_power_source(self):
        """ Test that the power sources can be correctly added to the power domain. """
        power_source_1 = SolarPower(self.mock_env, "Test Solar Power Source", "test_data.csv",
                                    self.mock_power_domain, priority=0)
        power_source_2 = SolarPower(self.mock_env, "Test Solar Power Source", "test_data.csv",
                                    self.mock_power_domain, priority=0)
        power_source_3 = SolarPower(self.mock_env, "Test Solar Power Source", "test_data.csv",
                                    self.mock_power_domain, priority=1)
        self.power_domain.power_sources = []

        self.power_domain.add_power_source(power_source_1)

        self.assertEqual(self.power_domain.power_sources, [power_source_1])
        # test error raise of duplicate power sources
        with self.assertRaises(ValueError):
            self.power_domain.add_power_source(power_source_1)
        # test error raise of duplicate priorities
        with self.assertRaises(BufferError):
            self.power_domain.add_power_source(power_source_2)

        power_source_2.priority = 2
        self.power_domain.add_power_source(power_source_2)

        self.assertEqual(self.power_domain.power_sources, [power_source_1, None, power_source_2])

        self.power_domain.add_power_source(power_source_3)

        self.assertEqual(self.power_domain.power_sources, [power_source_1, power_source_3, power_source_2])

    def test_remove_power_source(self):
        """ Test that power sources can be removed from the power domain correctly. """
        power_source_1 = SolarPower(self.mock_env, "Test Solar Power Source", "test_data.csv",
                                    self.mock_power_domain, priority=0)
        power_source_2 = SolarPower(self.mock_env, "Test Solar Power Source", "test_data.csv",
                                    self.mock_power_domain, priority=0)
        power_source_3 = SolarPower(self.mock_env, "Test Solar Power Source", "test_data.csv",
                                    self.mock_power_domain, priority=1)
        self.power_domain.power_sources = [power_source_1, power_source_3, power_source_2]

        self.power_domain.remove_power_source(power_source_3)

        self.assertEqual(self.power_domain.power_sources, [power_source_1, None, power_source_2])
        # test error raise of duplicate power sources
        with self.assertRaises(ValueError):
            self.power_domain.remove_power_source(power_source_3)

        self.power_domain.remove_power_source(power_source_1)

        self.assertEqual(self.power_domain.power_sources, [None, None, power_source_2])

        self.power_domain.remove_power_source(power_source_2)

        self.assertEqual(self.power_domain.power_sources, [None, None, None])

    def test_assign_power_source_priority(self):
        """ Test that the power sources can have their priority readjusted based on their location within the list. """
        power_source_1 = SolarPower(self.mock_env, "Test Solar Power Source", "test_data.csv",
                                    self.mock_power_domain, priority=3)
        power_source_2 = SolarPower(self.mock_env, "Test Solar Power Source", "test_data.csv",
                                    self.mock_power_domain, priority=20)
        power_source_3 = SolarPower(self.mock_env, "Test Solar Power Source", "test_data.csv",
                                    self.mock_power_domain, priority=10)
        self.power_domain.power_sources = [power_source_1, power_source_2, power_source_3]

        # Check that the previous priorities are as intended to show functionality
        previous_priorities = [3, 20, 10]
        for counter in range(len(self.power_domain.power_sources)):
            self.assertEqual(self.power_domain.power_sources[counter].priority, previous_priorities[counter])

        self.power_domain.assign_power_source_priority()
        for counter in range(len(self.power_domain.power_sources)):
            self.assertEqual(self.power_domain.power_sources[counter].priority, counter)

    def test_calculate_carbon_released(self):
        """ Test to check that correct calculation of carbon from a power reading.
            Power is in kWH -> from time sensitive reading (captures initially in W then converts using time elapsed)
            Carbon intensity is in gCO2/kWH"""

        result_1 = self.power_domain.calculate_carbon_released(50.0, 0.5)
        result_2 = self.power_domain.calculate_carbon_released(75.0, 0.75)

        # Assert that the results are as expected
        self.assertAlmostEqual(result_1, 0.025, places=3)  # Adjust the expected value based on your calculation
        self.assertAlmostEqual(result_2, 0.05625, places=3)  # Adjust the expected value based on your calculation

    def test_update_carbon_intensity(self):
        """ Test to check that when an update interval occurs the total amount of carbon released is calculated
            correctly. """
        self.power_domain.carbon_emitted = []
        update_interval_data = {'Solar': {'node2': {'Power Used': 0.1,
                                                    'Carbon Intensity': 1,
                                                    'Carbon Released': 0.1},
                                          'Total Carbon Released': 0.1},
                                'Grid': {'node1': {'Power Used': 0.06,
                                                   'Carbon Intensity': 2,
                                                   'Carbon Released': 0.12},
                                         'node3': {'Power Used': 0.15,
                                                   'Carbon Intensity': 1,
                                                   'Carbon Released': 0.15},
                                         'Total Carbon Released': 0.27}}
        self.power_domain.update_carbon_intensity(update_interval_data)
        self.assertEqual(self.power_domain.carbon_emitted, [0.37])

    def test_return_total_carbon_emissions(self):
        """ Test to check that the final total amount of carbon is calculated correctly. """
        self.power_domain.carbon_emitted = []
        self.assertEqual(self.power_domain.return_total_carbon_emissions(), 0.0)

        self.power_domain.carbon_emitted = [2, 3, 5]
        self.assertEqual(self.power_domain.return_total_carbon_emissions(), 10)

        with self.assertRaises(ValueError):
            self.power_domain.carbon_emitted = None
            self.power_domain.return_total_carbon_emissions()

    def test_add_entity(self):
        """ Test to ensure that entities are correctly added to the power domain. """

        self.power_domain.powered_entities = []

        self.power_domain.add_entity(self.mock_entity)

        self.assertEqual(self.power_domain.powered_entities, [self.mock_entity])
        with self.assertRaises(ValueError):
            # attempt to add an entity already present
            self.power_domain.add_entity(self.mock_entity)
            # attempt to add an entity when entities should only be added to power sources
            self.power_domain.entity_distributor.static_entities = True
            self.power_domain.add_entity(self.mock_entity)

    def test_remove_entity(self):
        """ Test to ensure that entities are correctly removed from the power domain. """

        self.power_domain.associated_entities = [self.mock_entity]

        self.power_domain.remove_entity(self.mock_entity)

        self.assertEqual(self.power_domain.powered_entities, [])
        with self.assertRaises(ValueError):
            # attempt to add an entity already present
            self.power_domain.remove_entity(self.mock_entity)

    def test_get_current_time(self):
        result_1 = self.power_domain.get_current_time("01:30:00")
        result_2 = self.power_domain.get_current_time("12:45:00")

        self.assertEqual(result_1, 90)  # 1 hour and 30 minutes
        self.assertEqual(result_2, 765)  # 12 hours and 45 minutes

        with self.assertRaises(ValueError):
            self.power_domain.get_current_time("24:00:00")
            self.power_domain.get_current_time("a")

    def test_convert_to_time_string(self):

        result_1 = self.power_domain.convert_to_time_string(90)
        result_2 = self.power_domain.convert_to_time_string(120)

        self.assertEqual(result_1, "01:30:00")
        self.assertEqual(result_2, "02:00:00")

        # Test with invalid input
        with self.assertRaises(ValueError):
            self.power_domain.convert_to_time_string("invalid_input")

        with self.assertRaises(ValueError):
            self.power_domain.convert_to_time_string(-5)

    def test_write_out_results(self):
        file_handler = FileHandler(self.power_domain)
        """ Test the write out function to ensure that side effect is a json file. """
        filename = "test_output.json"
        current_script_path = os.path.abspath(__file__)
        parent_directory = os.path.dirname(os.path.dirname(os.path.dirname(current_script_path)))
        expected_filepath = os.path.join(parent_directory, "results", f"{file_handler.creation_time}_results", filename)
        mocked_data = {"01:00:00": {'Wind': {'node2': {'Power Used': 0.1,
                                                       'Carbon Intensity': 1,
                                                       'Carbon Released': 0.1},
                                             'Total Carbon Released': 0.1},
                                    'Grid': {'node1': {'Power Used': 0.06,
                                                       'Carbon Intensity': 2,
                                                       'Carbon Released': 0.12},
                                             'node3': {'Power Used': 0.15,
                                                       'Carbon Intensity': 1,
                                                       'Carbon Released': 0.15},
                                             'Total Carbon Released': 0.27}}}
        expected_data = json.dumps(mocked_data, indent=2)

        self.power_domain.captured_data = mocked_data
        filepath_written_to, data_written = file_handler.write_out_results(filename=filename)

        self.assertEqual(expected_data, data_written)
        self.assertEqual(expected_filepath, filepath_written_to)


if __name__ == '__main__':
    unittest.main()
