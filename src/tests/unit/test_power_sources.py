import unittest

import numpy
import simpy

from unittest.mock import MagicMock
from src.extendedLeaf.power import SolarPower, PowerType, validate_str_time, WindPower, GridPower, BatteryPower


class TestSolarPower(unittest.TestCase):
    """ Given a solar power source class. """
    def setUp(self):
        # Create a mock environment for testing
        self.mock_env = MagicMock()
        # Create a mock power domain for testing
        self.mock_power_domain = MagicMock()
        self.mock_power_domain.start_time_string = "00:00:00"
        # Create a mock associated entity for testing
        self.mock_entity = MagicMock()
        self.mock_entity.power_model = MagicMock()
        self.power_source = SolarPower(self.mock_env, "Test Solar Power Source", "test_data.csv",
                                       self.mock_power_domain, priority=1)

    def test_remove_entity(self):
        """ Abstract Test: Test that when entities are removed from the power source they are done so correctly. """

        self.mock_entity.power_source = self.power_source
        self.power_source.powered_entities = [self.mock_entity]

        self.power_source.remove_entity(self.mock_entity)

        self.assertEqual(self.power_source.powered_entities, [])
        self.assertIsNone(self.mock_entity.power_model.power_source)
        with self.assertRaises(ValueError):
            self.power_source.remove_entity(self.mock_entity)

    def test_add_entity(self):
        """ Abstract Test: Test that when entities are added to the power source they are done so correctly. """

        self.mock_entity.power_source = None
        self.power_source.powered_entities = []

        self.power_source.add_entity(self.mock_entity)

        self.assertEqual(self.power_source.powered_entities, [self.mock_entity])
        self.assertEqual(self.mock_entity.power_model.power_source, self.power_source)
        with self.assertRaises(ValueError):
            self.power_source.add_entity(self.mock_entity)

    def test_validate_str_time(self):
        """ Test the ability to validate times as strings.
            Correct times return None, incorrect times raise an error. """

        self.assertIsNone(validate_str_time("12:34:56"))  # Valid time
        self.assertIsNone(validate_str_time("00:00:00"))  # An extreme time

        # Test with an invalid time format
        with self.assertRaises(ValueError):
            validate_str_time("123:45:67")
            validate_str_time("24:00:00")

    def test_retrieve_power_data(self):
        """ Abstract Test: Test that the file data is correctly to file. """

        expected_power_data = {'00:00:00': 0, '01:00:00': 0, '02:00:00': 0, '03:00:00': 0, '04:00:00': 0, '05:00:00': 0,
                               '06:00:00': 0, '07:00:00': 25, '08:00:00': 50, '09:00:00': 75, '10:00:00': 100,
                               '11:00:00': 125, '12:00:00': 150, '13:00:00': 175, '14:00:00': 150, '15:00:00': 125,
                               '16:00:00': 100, '17:00:00': 75, '18:00:00': 50, '19:00:00': 25, '20:00:00': 0,
                               '21:00:00': 0, '22:00:00': 0, '23:00:00': 0}

        # Test: correct test data, invalid file name, incorrect time
        data_set_filename = "test_data.csv"
        start_time = "00:00:00"
        power_data = self.power_source._retrieve_power_data(data_set_filename, start_time)
        self.assertEqual(expected_power_data, power_data)

        # Test: invalid file name
        data_set_filename = "fake_file_name.csv"
        start_time = "00:00:00"
        with self.assertRaises(ValueError):
            self.power_source._retrieve_power_data(data_set_filename, start_time)

        # Test: incorrect time
        data_set_filename = "test_data.csv"
        start_time = "25:00:00"
        with self.assertRaises(ValueError):
            self.power_source._retrieve_power_data(data_set_filename, start_time)

        # Test: start time non-existent
        data_set_filename = "test_data.csv"
        start_time = "12:00:01"
        with self.assertRaises(AttributeError):
            self.power_source._retrieve_power_data(data_set_filename, start_time)

    def test_constructor(self):
        """ Test that the class can be correctly created. """

        self.assertEqual(self.power_source.env, self.mock_env)
        self.assertEqual(self.power_source.name, "Test Solar Power Source")
        self.assertEqual(self.power_source.priority, 1)
        self.assertEqual(self.power_source.power_domain, self.mock_power_domain)
        self.assertEqual(self.power_source.powered_entities, [])

        self.assertEqual(self.power_source.inherent_carbon_intensity, 46)
        self.assertEqual(self.power_source.powerType, PowerType.RENEWABLE)
        self.assertEqual(self.power_source.carbon_intensity, 0)
        self.assertEqual(self.power_source.next_update_time, "00:00:00")

    def test_get_start_time_index(self):
        """ Test that when provided a string time, the correct corresponding index is returned. """

        start_time_1 = "00:00:00"  # First correct time
        start_time_2 = "23:00:00"  # Last correct time
        start_time_3 = "25:00:00"  # Erroneous time
        start_time_4 = "a"  # Erroneous value

        self.assertEqual(self.power_source._get_start_time_index(start_time_1), 0)
        self.assertEqual(self.power_source._get_start_time_index(start_time_2), 23)
        with self.assertRaises(ValueError):
            self.power_source._get_start_time_index(start_time_3)
            self.power_source._get_start_time_index(start_time_4)

    def test_get_current_power(self):
        """ Test that a power source can retrieve the current power. """

        self.power_source.update_interval = 60

        """ Testing purposes only, the framework does not anticipate erroneous times. """
        self.power_source.env = simpy.Environment(600)  # A valid time
        self.assertEqual(self.power_source.get_current_power(), 100)

        self.power_source.env = simpy.Environment(659)  # A valid time, outside of update interval
        self.assertEqual(self.power_source.get_current_power(), 100)  # Should retain previous power before update

        self.power_source.env = simpy.Environment(2040)  # A valid time, after the 24 hours (24*60) = 1440
        self.assertEqual(self.power_source.get_current_power(), 100)  # Should loop around back, 10am of Day 2

        self.power_source.env = simpy.Environment(-1)  # An invalid time
        self.assertEqual(self.power_source.get_current_power(), 0)

    def test_update_carbon_intensity(self):
        """ Irrelevant abstract class method of power source. """

        pass

    def test_get_current_carbon_intensity(self):
        """ Test that the static carbon intensity can be retrieved. """

        self.power_source.inherent_carbon_intensity = 50
        self.assertEqual(self.power_source.get_current_carbon_intensity(0), 50)


class TestWindPower(unittest.TestCase):
    """ Given a wind power source class. """
    def setUp(self):
        # Create a mock environment for testing
        self.mock_env = MagicMock()
        # Create a mock power domain for testing
        self.mock_power_domain = MagicMock()
        self.mock_power_domain.start_time_string = "00:00:00"
        # Create a mock associated entity for testing
        self.mock_entity = MagicMock()
        self.mock_entity.power_model = MagicMock()

        self.power_source = WindPower(self.mock_env, "Test Wind Power Source", "test_data.csv",
                                      self.mock_power_domain, priority=1)

    def test_constructor(self):
        """ Test that the class can be correctly created. """

        self.assertEqual(self.power_source.env, self.mock_env)
        self.assertEqual(self.power_source.name, "Test Wind Power Source")
        self.assertEqual(self.power_source.priority, 1)
        self.assertEqual(self.power_source.power_domain, self.mock_power_domain)
        self.assertEqual(self.power_source.powered_entities, [])

        self.assertEqual(self.power_source.inherent_carbon_intensity, 12)
        self.assertEqual(self.power_source.powerType, PowerType.RENEWABLE)
        self.assertEqual(self.power_source.carbon_intensity, 0)
        self.assertEqual(self.power_source.next_update_time, "00:00:00")

    def test_get_start_time_index(self):
        """ Test that when provided a string time, the correct corresponding index is returned. """

        start_time_1 = "00:00:00"  # First correct time
        start_time_2 = "23:00:00"  # Last correct time
        start_time_3 = "25:00:00"  # Erroneous time
        start_time_4 = "a"  # Erroneous value

        self.assertEqual(self.power_source._get_start_time_index(start_time_1), 0)
        self.assertEqual(self.power_source._get_start_time_index(start_time_2), 23)
        with self.assertRaises(ValueError):
            self.power_source._get_start_time_index(start_time_3)
            self.power_source._get_start_time_index(start_time_4)

    def test_get_current_power(self):
        """ Test that a power source can retrieve the current power. """

        self.power_source.update_interval = 60

        """ Testing purposes only, the framework does not anticipate erroneous times. """
        self.power_source.env = simpy.Environment(600)  # A valid time
        self.assertEqual(self.power_source.get_current_power(), 100)

        self.power_source.env = simpy.Environment(659)  # A valid time, outside of update interval
        self.assertEqual(self.power_source.get_current_power(), 100)  # Should retain previous power before update

        self.power_source.env = simpy.Environment(2040)  # A valid time, after the 24 hours (24*60) = 1440
        self.assertEqual(self.power_source.get_current_power(), 100)  # Should loop around back, 10am of Day 2

        self.power_source.env = simpy.Environment(-1)  # An invalid time
        self.assertEqual(self.power_source.get_current_power(), 0)

    def test_update_carbon_intensity(self):
        """ Irrelevant abstract class method of power source. """

        pass

    def test_get_current_carbon_intensity(self):
        """ Test that the static carbon intensity can be retrieved. """

        self.power_source.inherent_carbon_intensity = 50
        self.assertEqual(self.power_source.get_current_carbon_intensity(0), 50)

    class TestWindPower(unittest.TestCase):
        """ Given a wind power source class. """

        def setUp(self):
            # Create a mock environment for testing
            self.mock_env = MagicMock()
            # Create a mock power domain for testing
            self.mock_power_domain = MagicMock()
            self.mock_power_domain.start_time_string = "00:00:00"
            # Create a mock associated entity for testing
            self.mock_entity = MagicMock()
            self.mock_entity.power_model = MagicMock()

            self.power_source = WindPower(self.mock_env, "Test Wind Power Source", "test_data.csv",
                                          self.mock_power_domain, priority=1)

        def test_constructor(self):
            """ Test that the class can be correctly created. """

            self.assertEqual(self.power_source.env, self.mock_env)
            self.assertEqual(self.power_source.name, "Test Wind Power Source")
            self.assertEqual(self.power_source.priority, 1)
            self.assertEqual(self.power_source.power_domain, self.mock_power_domain)
            self.assertEqual(self.power_source.powered_entities, [])

            self.assertEqual(self.power_source.inherent_carbon_intensity, 12)
            self.assertEqual(self.power_source.powerType, PowerType.RENEWABLE)
            self.assertEqual(self.power_source.carbon_intensity, 0)
            self.assertEqual(self.power_source.next_update_time, "00:00:00")

        def test_get_start_time_index(self):
            """ Test that when provided a string time, the correct corresponding index is returned. """

            start_time_1 = "00:00:00"  # First correct time
            start_time_2 = "23:00:00"  # Last correct time
            start_time_3 = "25:00:00"  # Erroneous time
            start_time_4 = "a"  # Erroneous value

            self.assertEqual(self.power_source._get_start_time_index(start_time_1), 0)
            self.assertEqual(self.power_source._get_start_time_index(start_time_2), 23)
            with self.assertRaises(ValueError):
                self.power_source._get_start_time_index(start_time_3)
                self.power_source._get_start_time_index(start_time_4)

        def test_get_current_power(self):
            """ Test that a power source can retrieve the current power. """

            self.power_source.update_interval = 60

            """ Testing purposes only, the framework does not anticipate erroneous times. """
            self.power_source.env = simpy.Environment(600)  # A valid time
            self.assertEqual(self.power_source.get_current_power(), 100)

            self.power_source.env = simpy.Environment(659)  # A valid time, outside of update interval
            self.assertEqual(self.power_source.get_current_power(), 100)  # Should retain previous power before update

            self.power_source.env = simpy.Environment(2040)  # A valid time, after the 24 hours (24*60) = 1440
            self.assertEqual(self.power_source.get_current_power(), 100)  # Should loop around back, 10am of Day 2

            self.power_source.env = simpy.Environment(-1)  # An invalid time
            self.assertEqual(self.power_source.get_current_power(), 0)

        def test_get_current_carbon_intensity(self):
            """ Test that the static carbon intensity can be retrieved. """

            self.power_source.inherent_carbon_intensity = 50
            self.assertEqual(self.power_source.get_current_carbon_intensity(0), 50)


class TestGridPower(unittest.TestCase):
    """ Given a grid power source class. """
    def setUp(self):
        # Create a mock environment for testing
        self.mock_env = MagicMock()
        # Create a mock power domain for testing
        self.mock_power_domain = MagicMock()
        self.mock_power_domain.start_time_string = "00:00:00"
        # Create a mock associated entity for testing
        self.mock_entity = MagicMock()
        self.mock_entity.power_model = MagicMock()
        self.power_source = GridPower(self.mock_env, "Test Grid Power Source", "test_data.csv",
                                      self.mock_power_domain, priority=1)

    def test_constructor(self):
        """ Test that the class can be correctly created. """

        self.assertEqual(self.power_source.env, self.mock_env)
        self.assertEqual(self.power_source.name, "Test Grid Power Source")
        self.assertEqual(self.power_source.priority, 1)
        self.assertEqual(self.power_source.power_domain, self.mock_power_domain)
        self.assertEqual(self.power_source.powered_entities, [])

        self.assertEqual(self.power_source.powerType, PowerType.MIXED)
        self.assertEqual(self.power_source.carbon_intensity, 0)
        self.assertEqual(self.power_source.next_update_time, "00:00:00")

    def test_get_start_time_index(self):
        """ Test that when provided a string time, the correct corresponding index is returned. """

        start_time_1 = "00:00:00"  # First correct time
        start_time_2 = "23:00:00"  # Last correct time
        start_time_3 = "25:00:00"  # Erroneous time
        start_time_4 = "a"  # Erroneous value

        self.assertEqual(self.power_source._get_start_time_index(start_time_1), 0)
        self.assertEqual(self.power_source._get_start_time_index(start_time_2), 23)
        with self.assertRaises(ValueError):
            self.power_source._get_start_time_index(start_time_3)
            self.power_source._get_start_time_index(start_time_4)

    def test_get_current_power(self):
        """ Test that the power available is infinite. """
        self.assertEqual(self.power_source.get_current_power(), numpy.inf)

    def test_get_current_carbon_intensity(self):
        """ Test to ensure that when the simulation proceeds forward in time the carbon intensity is changed """
        self.power_source.update_interval = 60

        """ Testing purposes only, the framework does not anticipate erroneous times. """
        self.power_source.env = simpy.Environment(600)  # A valid time
        self.assertEqual(self.power_source.get_current_carbon_intensity(0), 100)

        self.power_source.env = simpy.Environment(659)  # A valid time, outside of update interval
        self.assertEqual(self.power_source.get_current_carbon_intensity(0), 100)  # Should retain previous data before update

        self.power_source.env = simpy.Environment(2040)  # A valid time, after the 24 hours (24*60) = 1440
        self.assertEqual(self.power_source.get_current_carbon_intensity(0), 100)  # Should loop around back, 10am of Day 2

        self.power_source.env = simpy.Environment(-1)  # An invalid time
        self.assertEqual(self.power_source.get_current_carbon_intensity(0), 0)

    def test_update_carbon_intensity(self):
        """ Test that the carbon intensity attribute is updated, utilise method above so test not extensive. """
        self.power_source.update_interval = 60
        self.power_source.env = simpy.Environment(600)  # A valid time
        self.power_source.carbon_intensity = 0  # initial value to demonstrate update

        self.power_source.update_carbon_intensity()

        self.assertEqual(self.power_source.carbon_intensity, 100)


class TestBatteryPower(unittest.TestCase):
    """ Given a battery power source class. """
    def setUp(self):
        # Create a mock environment for testing
        self.mock_env = MagicMock()
        # Create a mock power domain for testing
        self.mock_power_domain = MagicMock()
        # Create a mock associated entity for testing
        self.mock_entity = MagicMock()
        self.mock_entity.power_model = MagicMock()
        self.power_source = BatteryPower(self.mock_env, "Test Battery Power Source", self.mock_power_domain, priority=1,
                                         total_power_available=100, charge_rate=20)

    def test_constructor(self):
        """ Test that the class can be correctly created. """

        self.assertEqual(self.power_source.env, self.mock_env)
        self.assertEqual(self.power_source.name, "Test Battery Power Source")
        self.assertEqual(self.power_source.priority, 1)
        self.assertEqual(self.power_source.power_domain, self.mock_power_domain)
        self.assertEqual(self.power_source.powered_entities, [])

        self.assertEqual(self.power_source.powerType, PowerType.BATTERY)
        self.assertEqual(self.power_source.carbon_intensity, 0)

    def test_get_current_power(self):
        """ Test that the power available is infinite. """
        self.power_source.remaining_power = 50

        self.assertEqual(self.power_source.get_current_power(), 50)

    def test_set_current_power(self):
        """ Test that the remaining power left is correct. """
        self.power_source.remaining_power = 50
        self.power_source.set_current_power(100)  # Valid power
        self.assertEqual(self.power_source.get_current_power(), 100)
        with self.assertRaises(ValueError):
            self.power_source.set_current_power(-1)  # Invalid power

    def test_recharge_battery(self):
        """ Test to check that the battery can be correctly recharged. """
        # Create a mock power domain for testing
        other_mock_power_domain = MagicMock()
        other_mock_power_domain.start_time_string = "00:00:00"
        other_power_source = SolarPower(MagicMock(), "Test Solar Power Source", "test_data.csv",
                                        other_mock_power_domain, priority=1)
        self.power_source.remaining_power = 10
        self.power_source.recharge_battery(other_power_source)
        self.assertEqual(self.power_source.get_current_power(), self.power_source.total_power)

    def test_consume_battery_power(self):
        """ Test to check that power can be correctly taken away from the battery. """
        starting_power = 100
        self.power_source.set_current_power(starting_power)

        # Test: remove valid amount
        valid_amount_of_power = 50
        self.power_source.consume_battery_power(valid_amount_of_power)

        self.assertEqual(self.power_source.get_current_power(), starting_power-valid_amount_of_power)

        with self.assertRaises(ValueError):
            self.power_source.set_current_power(starting_power)
            # Test: remove too large amount
            invalid_amount_of_power = 200
            self.power_source.consume_battery_power(invalid_amount_of_power)
            # Test: remove negative amount
            invalid_amount_of_power = -100
            self.power_source.consume_battery_power(invalid_amount_of_power)

    def test_get_current_carbon_intensity(self):
        """ Test to ensure that no carbon intensity is being given off, given off through recharge instead. """
        self.assertEqual(self.power_source.get_current_carbon_intensity(0), 0)


if __name__ == '__main__':
    unittest.main()
