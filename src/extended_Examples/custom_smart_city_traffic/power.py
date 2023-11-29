import csv
import logging
import math

import os
from abc import ABC, abstractmethod
from functools import reduce
from typing import Union, Collection, Callable, Optional, Iterable

import simpy
from simpy import Environment
from enum import auto

from src.extended_Examples.custom_smart_city_traffic.settings import BATTERY_CAR_TOTAL, BATTERY_CAR_CHARGE_RATE

logger = logging.getLogger(__name__)
_unnamed_power_meters_created = 0


class PowerMeasurement:
    def __init__(self, dynamic: float, static: float):
        """Power measurement of one or more entities at a certain point in time.

        Args:
            dynamic: Dynamic (load-dependent) power usage in Watt
            static: Static (load-independent) power usage in Watt
        """
        self.dynamic = dynamic
        self.static = static

    @classmethod
    def sum(cls, measurements: Iterable["PowerMeasurement"]):
        dynamic, static = reduce(lambda acc, cur: (acc[0] + cur.dynamic, acc[1] + cur.static), measurements, (0, 0))
        return PowerMeasurement(dynamic, static)

    def __repr__(self):
        return f"PowerMeasurement(dynamic={self.dynamic:.2f}W, static={self.static:.2f}W)"

    def __float__(self) -> float:
        return float(self.dynamic + self.static)

    def __int__(self) -> float:
        return int(self.dynamic + self.static)

    def __add__(self, other):
        return PowerMeasurement(self.dynamic + other.dynamic, self.static + other.static)

    def __radd__(self, other):  # Required for sum()
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def __sub__(self, other):
        return PowerMeasurement(self.dynamic - other.dynamic, self.static - other.static)

    def multiply(self, factor: float):
        return PowerMeasurement(self.dynamic * factor, self.static * factor)

    def total(self) -> float:
        return float(self)


class PowerModel(ABC):
    """Abstract base class for power models."""

    # TODO: Validator! Only one power model per entity

    @abstractmethod
    def measure(self) -> PowerMeasurement:
        """Return the current power usage."""

    @abstractmethod
    def set_parent(self, parent):
        """Set the entity which the power model is responsible for.

        Should be called in the parent's `__init__()`.
        """


class PowerModelNode(PowerModel):
    def __init__(self, max_power: float = None, power_per_cu: float = None, static_power: float = 0):
        """Power model for compute nodes with static and dynamic power usage.

        Power usage is scaled linearly with resource usage.

        Example:
            A computer which constantly uses 10 Watt even when being idle (`static_power=10`) but can consume
            up to 150 Watt when under full load (`max_power=150`).

        Args:
            max_power: Maximum power usage of the node under full load. Cannot be combined with `power_per_cu`.
            power_per_cu: Incremental power usage for each used compute unit. Cannot be combined with `max_power`.
            static_power: Idle power usage of the node without any load.
        """
        if max_power is None and power_per_cu is None:
            raise ValueError("Either `max_power` or `power_per_cu` have to be stated.")
        if max_power is not None and power_per_cu is not None:
            raise ValueError("The parameters `max_power` or `power_per_cu` cannot be combined.")
        self.max_power = max_power
        self.power_per_cu = power_per_cu
        self.static_power = static_power
        self.node = None
        self.power_source = None

    def measure(self) -> PowerMeasurement:
        if self.max_power is not None:
            dynamic_power = (self.max_power - self.static_power) * self.node.utilization()
        elif self.power_per_cu is not None:
            dynamic_power = self.power_per_cu * self.node.used_cu
        else:
            raise RuntimeError("Invalid state of PowerModelNode: `max_power` and `power_per_cu` are undefined.")
        return PowerMeasurement(dynamic=dynamic_power, static=self.static_power)

    def set_parent(self, parent):
        self.node = parent


class PowerModelLink(PowerModel):
    def __init__(self, energy_per_bit: float):
        """Power model for network links.

        Args:
            energy_per_bit: Incremental energy per bit in J/bit (or W/(bit/s))
        """
        self.energy_per_bit = energy_per_bit
        self.link = None

    def measure(self) -> PowerMeasurement:
        dynamic_power = self.energy_per_bit * self.link.used_bandwidth
        return PowerMeasurement(dynamic=dynamic_power, static=0)

    def set_parent(self, parent):
        self.link = parent


class PowerModelLinkWirelessTx(PowerModel):
    def __init__(self, energy_per_bit: float, amplifier_dissipation: float):
        """Power model for transmitting on wireless network links.

        TODO Explain

        Note:
            If you don't know the amplifier dissipation or distance of nodes or if you are concerned with performance,
            you can also just use the regular :class:`PowerModelLink`

        Args:
            energy_per_bit: Incremental energy per bit in J/bit (or W/(bit/s))
            amplifier_dissipation: Amplifier energy dissipation in free space channel in J/bit/m^2
        """
        self.energy_per_bit = energy_per_bit
        self.amplifier_dissipation = amplifier_dissipation
        self.link = None

    def measure(self) -> PowerMeasurement:
        distance = self.link.src.distance(self.link.dst)
        dissipation_energy_per_bit = self.amplifier_dissipation * distance ** 2
        dynamic_power = (self.energy_per_bit + dissipation_energy_per_bit) * self.link.used_bandwidth
        return PowerMeasurement(dynamic=dynamic_power, static=0)

    def set_parent(self, parent):
        self.link = parent


class PowerAware(ABC):
    """Abstract base class for entites whose power can be measured.

    This may be parts of the infrastructure as well as applications.
    """

    @abstractmethod
    def measure_power(self) -> PowerMeasurement:
        """Returns the power that is currently used by the entity."""


class PowerMeter:
    """Power meter that stores the power of one or more entites in regular intervals.

    Args:
        entities: Can be either (1) a single :class:`PowerAware` entity (2) a list of :class:`PowerAware` entities
            (3) a function which returns a list of :class:`PowerAware` entities, if the number of these entities
            changes during the simulation.
        name: Name of the power meter for logging and reporting
        measurement_interval: The freequency in which measurement take place.
        callback: A function which will be called with the PowerMeasurement result after each conducted measurement.
    """

    def __init__(self,
                 entities: Union[PowerAware, Collection[PowerAware], Callable[[], Collection[PowerAware]]],
                 name: Optional[str] = None,
                 measurement_interval: Optional[float] = 1,
                 callback: Optional[Callable[[PowerMeasurement], None]] = None):
        self.entities = entities
        if name is None:
            global _unnamed_power_meters_created
            self.name = f"power_meter_{_unnamed_power_meters_created}"
            _unnamed_power_meters_created += 1
        else:
            self.name = name
        self.measurement_interval = measurement_interval
        self.callback = callback
        self.measurements = []

    def run(self, env: simpy.Environment, delay: Optional[float] = 0):
        """Starts the power meter process.

        Args:
            env: Simpy environment (for timing the measurements)
            delay: The delay after which the measurements shall be conducted. For some scenarios it makes sense to e.g.
            include a tiny delay to make sure that all events at a previous time step were processed before the
            measurement is conducted.

        Returns:
            sim
        """
        yield env.timeout(delay)
        while True:
            if isinstance(self.entities, PowerAware):
                measurement = self.entities.measure_power()
            else:
                if isinstance(self.entities, Collection):
                    entities = self.entities
                elif isinstance(self.entities, Callable):
                    entities = self.entities()
                else:
                    raise ValueError(
                        f"{self.name}: Unsupported type {type(self.entities)} for observable={self.entities}.")
                measurement = PowerMeasurement.sum(entity.measure_power() for entity in entities)
            self.measurements.append(measurement)
            if self.callback is not None:
                self.callback(measurement)
            logger.debug(f"{env.now}: {self.name}: {measurement}")
            yield env.timeout(self.measurement_interval)


class PowerType(auto):
    RENEWABLE = auto()
    NONRENEWABLE = auto()
    BATTERY = auto()


class PowerLocation(auto):
    ONSITE = auto()
    OFFSITE = auto()
    LOCAL = auto()


class PowerSource(ABC):

    def __init__(self, env: Environment, name, data_set_filename, power_domain=None, priority: int = 0,
                 nodes_being_powered = None):
        self.name = name
        self.env = env
        self.carbon_intensity = 0
        if nodes_being_powered is None:
            self.nodes_being_powered = []
        else:
            self.nodes_being_powered = nodes_being_powered
        self.priority = priority

        self.powerType = None

        if power_domain is None:
            raise AttributeError(f"No power manager was supplied")
        self.power_domain = power_domain

        self._retrieve_power_data(data_set_filename, self.power_domain.start_time_string)
        self.next_update_time = list(self.power_data.keys())[0]
        self.update_interval = self.power_domain.get_current_time(
            list(self.power_data.keys())[1]) - self.power_domain.get_current_time(list(self.power_data.keys())[0])

    @abstractmethod
    def get_current_power(self) -> PowerMeasurement:
        """Return the current power provided."""

    @abstractmethod
    def get_current_carbon_intensity(self, offset: int):
        """retrieve the current carbon intensity"""

    @abstractmethod
    def update_carbon_intensity(self):
        """Add a node to be powered b"""

    def remove_node(self, node):
        if node not in self.nodes_being_powered:
            raise ValueError(f"Error: {node.id} not present in list")
        self.nodes_being_powered.remove(node)

    def _retrieve_power_data(self, data_set_filename: str, start_time: str = None):
        if start_time is None:
            raise ValueError(f"Error no start time is provided")
        # find the file path we want
        current_script_path = os.path.abspath(__file__)
        target_directory = "LEAF"
        # Navigate upwards from the current script path until you find the target directory
        base_directory = current_script_path
        while not base_directory.endswith(target_directory):
            base_directory = os.path.dirname(base_directory)
        abs_file_path = os.path.join(base_directory + "\dataSets", data_set_filename)

        # this data we will capture then will add at the end
        data_before_start = {}
        start_found = False
        power_data = {}
        try:
            with open(abs_file_path, mode='r', encoding='utf-8-sig') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                line_count = 0
                for row in csv_reader:
                    time = row["time"]
                    data = int(float(row["data"]))
                    if (time == start_time) | start_found:
                        power_data[time] = data
                        start_found = True
                    else:
                        data_before_start[time] = data
                    line_count += 1
                power_data |= data_before_start
        except FileNotFoundError:
            print(f"Error: {data_set_filename} does not exist.")
        if not start_found:
            raise ValueError(f"Error: Start time {start_time} was not found in data")
        self.power_data = power_data

    def _map_to_time(self, current_increment: int = 0) -> str:
        if self.power_data is None:
            raise ValueError(f"Error: no data set has been provided")
        times = list(self.power_data.keys())
        return times[current_increment]

    def add_node(self, node):
        if node in self.nodes_being_powered:
            raise ValueError(f"Error: {node.id} already present in list")
        self.nodes_being_powered.append(node)

class NodeDistributor:

    def __init__(self, node_distributor_method: Callable[[PowerSource, ["Node"]], None] = None,
                 smart_distribution: bool = True):
        self.node_distributor_method = node_distributor_method or self.default_update_node_distribution_method
        self.smart_distribution = smart_distribution

    def default_update_node_distribution_method(self, current_power_source, associated_nodes):
        """Update renewable sources"""
        if current_power_source.powerType == PowerType.RENEWABLE:
            current_power = current_power_source.get_current_power()
            self.update_renewable_power_source(current_power, current_power_source, associated_nodes)
        else:
            """Update NonRenewable sources"""
            self.update_non_renewable_power_source(current_power_source, associated_nodes)

    def update_renewable_power_source(self, total_current_power, current_power_source, associated_nodes):
        for node in associated_nodes:
            current_node_power_requirement = int(node.power_model.measure())
            """Check if node is currently being powered by the desired node"""
            if node.power_model.power_source == current_power_source:
                if total_current_power < current_node_power_requirement:
                    node.power_model.power_source = None
                    current_power_source.remove_node(node)
                else:
                    total_current_power = total_current_power - current_node_power_requirement
                continue

            """Check if node is currently unpowered"""
            if node.power_model.power_source is None and current_node_power_requirement < total_current_power:
                current_power_source.add_node(node)
                node.power_model.power_source = current_power_source
                total_current_power = total_current_power - current_node_power_requirement
                continue

            """Check if any nodes in lower priority power sources can move up if excess energy is available"""
            if self.smart_distribution:
                if node.power_model.power_source is not None and node.power_model.power_source.priority > current_power_source.priority:
                    if current_node_power_requirement < total_current_power:
                        current_power_source.add_node(node)
                        node.power_model.power_source.remove_node(node)
                        node.power_model.power_source = current_power_source
                        total_current_power = total_current_power - current_node_power_requirement

    def update_non_renewable_power_source(self, current_power_source, associated_nodes):
        for node in associated_nodes:
            if node.power_model.power_source is None:
                node.power_model.power_source = current_power_source
                current_power_source.add_node(node)
                continue
            if node.power_model.power_source.priority > current_power_source.priority:
                node.power_model.power_source.remove_node(node)
                node.power_model.power_source = current_power_source


class PowerDomain:

    def __init__(self, env: Environment, name=None, start_time_str: str = "00:00:00", associated_nodes=None,
                 update_interval=1, node_distributor: NodeDistributor = None,
                 power_source_events: [(str, (Callable[[], None], []))] = None):

        self.env = env
        if name is None:
            raise ValueError(f"Error: Power  Domain was not supplied a name")
        else:
            self.name = name
        self.power_sources = []
        self.carbon_emitted = []

        self.node_distributor = node_distributor or NodeDistributor()

        self.start_time_string = start_time_str
        self.start_time_index = self.get_current_time(start_time_str)
        if associated_nodes is None:
            self.associated_nodes = []
        else:
            self.associated_nodes = associated_nodes
        self.update_interval = update_interval
        if power_source_events is None:
            self.power_source_events = []
        else:
            self.power_source_events = power_source_events

    """Prerequisites, a power domain is provided with:
            - Power source(s) to provide power to nodes
            - Associated node(s) to provide power to"""

    def run(self, env):

        if self.power_sources is None:
            raise AttributeError(f"Error: No power source was provided")
        if not self.associated_nodes:
            raise AttributeError(f"Error: No nodes are present in the power domain")

        while True:
            """Execute any pre-planned commands at the current moment of time"""
            for time, (event, args) in self.power_source_events:
                if (self.env.now + self.start_time_index) == self.get_current_time(time):
                    event(*args)

            self.assign_power_source_priority()
            """Should go through every power source and check for an update, only 
            when an update needs to occur should we carry it out, in particular we call update
            environment which will correctly ensure that nodes are updated after this has happened
            the next update period is found"""
            current_carbon_intensities = {}
            current_carbon_intensity = 0
            for current_power_source in [power_source for power_source in self.power_sources if
                                         power_source is not None]:
                current_dictionary = {}

                self.node_distributor.node_distributor_method(current_power_source, self.associated_nodes)

                if (env.now + self.start_time_index) >= self.get_current_time(current_power_source.next_update_time):
                    current_power_source.get_next_update_time()

                """Record respective power readings this interval"""
                carbon_currently_released = 0

                for node in current_power_source.nodes_being_powered:
                    power_used = node.power_model.measure()
                    carbon_intensity = current_power_source.get_current_carbon_intensity(0)
                    carbon_released = self.calculate_carbon_released(power_used, carbon_intensity)
                    node_data = {"Power Used": power_used,
                                 "Carbon Intensity": carbon_intensity,
                                 "Carbon Released": carbon_released}
                    carbon_currently_released += carbon_released
                    current_dictionary[node.name] = node_data

                current_dictionary["Total Carbon Released"] = carbon_currently_released
                current_carbon_intensities[current_power_source.name] = current_dictionary
                logger.debug(f"{env.now}: ({self.convert_to_time_string(self.env.now + self.start_time_index)}) "
                             f"{current_power_source.name} released {carbon_currently_released} gCO2")
                current_carbon_intensity += carbon_currently_released
            self.update_carbon_intensity(current_carbon_intensities, self.update_interval)

            for node in self.associated_nodes:
                if node.power_model.power_source is None:
                    raise ValueError(f"Error: no power source found for node {node} at time {self.env.now}")

            logger.debug(f"{env.now}: ({self.convert_to_time_string(self.env.now + self.start_time_index)}) "
                         f"{self.name} released {current_carbon_intensity} gCO2")
            yield env.timeout(self.update_interval)

    def add_power_source(self, power_source):
        if power_source in self.power_sources:
            raise ValueError(f"Error: Power source {power_source.name} is already present at priority "
                             f"{self.power_sources.index(power_source)} ")

        if (power_source.powerType == PowerType.NONRENEWABLE
                and power_source.powerLocation == PowerLocation.OFFSITE):
            if any(
                    current_power_source
                    and current_power_source.powerType == PowerType.NONRENEWABLE
                    and current_power_source.powerLocation == PowerLocation.OFFSITE
                    for current_power_source in self.power_sources
            ):
                raise ValueError(f"Error: Power domain can only accept 1 offsite nonrenewable "
                                 f"power source")

        if power_source.priority >= len(self.power_sources):
            extra_nodes = power_source.priority - len(self.power_sources)
            self.power_sources.extend([None] * extra_nodes)
            self.power_sources.append(power_source)
        else:
            if self.power_sources[power_source.priority] is None:
                self.power_sources[power_source.priority] = power_source
            else:
                raise BufferError(
                    f"Error: Priority {power_source.priority} is occupied with {self.power_sources[power_source.priority]}")

    def remove_power_source(self, power_source):
        self.power_sources[self.power_sources.index(power_source)] = None
        power_source.power_domain = None
        power_source.priority = None
        for node in power_source.nodes_being_powered:
            node.power_model.power_source = None
        power_source.nodes_being_powered = []

    def assign_power_source_priority(self):
        for counter in range(len(self.power_sources)):
            if self.power_sources[counter] is not None:
                self.power_sources[counter].priority = counter

    def calculate_carbon_released(self, power_used, carbon_intensity):
        return float(power_used) * (10 ** -3) * float(carbon_intensity)

    def update_carbon_intensity(self, increment_data, repeats):
        increment_total_carbon_omitted = 0
        for increment in increment_data.values():
            increment_total_carbon_omitted += increment["Total Carbon Released"]
        for i in range(repeats):
            self.carbon_emitted.append(increment_total_carbon_omitted)  # this is to account for the time interval

    def return_total_carbon_emissions(self) -> int:
        return sum(self.carbon_emitted)

    def add_node(self, node):
        if node in self.associated_nodes:
            raise ValueError(f"Error: {node.id} already present in list")
        self.associated_nodes.append(node)

    def remove_node(self, node):
        if node not in self.associated_nodes:
            raise ValueError(f"Error: {node.id} not present in list")
        self.associated_nodes.remove(node)

    def get_current_time(self, time):
        hh, mm, ss = map(int, time.split(':'))
        return mm + (60 * hh)

    def convert_to_time_string(self, time):
        hours, minutes = divmod(time, 60)
        return f"{hours:02d}:{minutes:02d}:00"


class SolarPower(PowerSource):
    SOLAR_DATASET_FILENAME = "08-08-2020 Glasgow pv data.csv"

    def __init__(self, env: Environment, data_set_filename: str = SOLAR_DATASET_FILENAME,
                 power_domain: PowerDomain = None, name: str = "Solar", priority: int = 0):
        super().__init__(env, name, data_set_filename, power_domain, priority)
        self.inherent_carbon_intensity = 46
        self.powerType = PowerType.RENEWABLE
        self.powerLocation = PowerLocation.OFFSITE

    def get_next_update_time(self):
        new_index = (list(self.power_data.keys()).index(self.next_update_time) + 1) % len(self.power_data)
        self.next_update_time = list(self.power_data.keys())[new_index]

    def _get_start_time_index(self, start_time_str):
        if self.power_data is None:
            raise ValueError(f"Error: no data set has been provided")
        times = list(self.power_data.keys())
        start_time = times.index(start_time_str)
        return start_time

    def get_current_power(self) -> int:
        time = self._map_to_time((self.env.now // self.update_interval) % len(self.power_data))
        return int(self.power_data[time])

    def update_carbon_intensity(self):
        pass

    def get_current_carbon_intensity(self, offset):
        return self.inherent_carbon_intensity


class WindPower(PowerSource):
    WIND_DATASET_FILENAME = "01-01-2023 Ireland wind data.csv"

    def __init__(self, env: Environment, data_set_filename: str = WIND_DATASET_FILENAME,
                 power_domain: PowerDomain = None, name: str = "Wind", priority: int = 0):
        super().__init__(env, name, data_set_filename, power_domain, priority)
        self.inherent_carbon_intensity = 12
        self.powerType = PowerType.RENEWABLE
        self.powerLocation = PowerLocation.ONSITE

    def get_next_update_time(self):
        new_index = (list(self.power_data.keys()).index(self.next_update_time) + 1) % len(self.power_data)
        self.next_update_time = list(self.power_data.keys())[new_index]

    def get_current_power(self) -> int:
        time = self._map_to_time((self.env.now // self.update_interval) % len(self.power_data))
        return int(self.power_data[time])

    def update_carbon_intensity(self):
        pass

    def get_current_carbon_intensity(self, offset):
        return self.inherent_carbon_intensity


class GridPower(PowerSource):
    GRID_DATASET_FILENAME = "08-08-2023 national carbon intensity.csv"

    def __init__(self, env: Environment, data_set_filename: str = GRID_DATASET_FILENAME,
                 power_domain: PowerDomain = None, name: str = "Grid", priority: int = 0):
        super().__init__(env, name, data_set_filename, power_domain, priority)
        self.carbon_intensity = 0
        self.powerType = PowerType.NONRENEWABLE
        self.powerLocation = PowerLocation.OFFSITE

    def get_next_update_time(self):
        new_index = (list(self.power_data.keys()).index(self.next_update_time) + 1) % len(self.power_data)
        self.next_update_time = list(self.power_data.keys())[new_index]

    def _get_start_time_index(self, start_time_str):
        if self.power_data is None:
            raise ValueError(f"Error: no data set has been provided")
        times = list(self.power_data.keys())
        start_time = times.index(start_time_str)
        return start_time

    def update_carbon_intensity(self):
        self.carbon_intensity = self.get_current_carbon_intensity(0)

    def get_current_carbon_intensity(self, offset) -> int:
        time = self._map_to_time(((self.env.now + offset) // self.update_interval) % len(self.power_data))
        return int(self.power_data[time])

    def get_current_power(self) -> int:
        pass


class BatteryPower(PowerSource):
    BATTERY_DATASET_FILENAME = "08-08-2023 national carbon intensity.csv"

    def __init__(self, env: Environment, data_set_filename: str = BATTERY_DATASET_FILENAME,
                 power_domain: PowerDomain = None, name: str = "Battery", priority: int = 10,
                 nodes_being_powered = None):
        super().__init__(env, name, data_set_filename, power_domain, priority, nodes_being_powered=nodes_being_powered)

        self.carbon_intensity = 0  # Assumed that carbon intensity comes from power source charging it
        self.powerType = PowerType.BATTERY
        self.powerLocation = PowerLocation.LOCAL
        self.total_power = BATTERY_CAR_TOTAL  # kWh
        self.remaining_power = 0  # kWh
        self.recharge_rate = BATTERY_CAR_CHARGE_RATE  # kw/h
        self.recharge_data = []

    """def run(self, env, update_interval):
        while True:
            for node in self.nodes_being_powered:
                power_required = node.measure_power()
                if power_required < self.remaining_power:
                    print(f"Cant process node: {node.name}, RECHARGING")
                    time_spent_recharging = self.recharge_battery(self.chargepoint)
                    yield env.timeout(time_spent_recharging)
                print(f"{env.now}: {self.name}'s {node.name} used {power_required}")
                self.update_battery(power_required)
            yield env.timeout(update_interval)"""

    def recharge_battery(self, power_source):
        power_to_recharge = self.total_power - self.remaining_power
        time_to_recharge = math.ceil(power_to_recharge / self.recharge_rate)
        self.remaining_power = self.total_power

        """Calculate how much carbon was released by charging the battery"""
        carbon_released = 0
        for time_offset in range(time_to_recharge):
            carbon_intensity = power_source.get_current_carbon_intensity(time_offset)
            carbon_released += self.power_domain.calculate_carbon_released(self.recharge_rate, carbon_intensity)
        recharge_data = {"Power Used": power_to_recharge,
                     "Carbon Released": carbon_released,
                     "Power Source": power_source.name}
        self.recharge_data.append(recharge_data)
        return time_to_recharge

    def update_battery(self, power_consumed):
        if power_consumed < 0:
            raise ValueError(f"Error: Power consumed cant be negative")
        if power_consumed > self.remaining_power:
            raise ValueError(f"Error: {self.name} does not have enough power for to carry out task")
        else:
            self.remaining_power -= power_consumed

    def _get_start_time_index(self, start_time_str):
        if self.power_data is None:
            raise ValueError(f"Error: no data set has been provided")
        times = list(self.power_data.keys())
        start_time = times.index(start_time_str)
        return start_time

    def update_carbon_intensity(self):
        self.carbon_intensity = self.get_current_carbon_intensity(0)

    def get_current_carbon_intensity(self, offset) -> int:
        time = self._map_to_time((self.env.now // self.update_interval) % len(self.power_data))
        return int(self.power_data[time])

    def get_current_power(self) -> int:
        return self.remaining_power

