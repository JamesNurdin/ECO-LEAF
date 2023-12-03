import csv
import logging
import math

import os
from abc import ABC, abstractmethod
from functools import reduce
from typing import Union, Collection, Callable, Optional, Iterable

import numpy
import simpy
from simpy import Environment
from enum import auto


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

    def update_sensitive_measure(self, update_interval):
        if self.max_power is not None:
            dynamic_power = (self.max_power - self.static_power) * self.node.utilization()
        elif self.power_per_cu is not None:
            dynamic_power = self.power_per_cu * self.node.used_cu * update_interval/60
        else:
            raise RuntimeError("Invalid state of PowerModelNode: `max_power` and `power_per_cu` are undefined.")
        return PowerMeasurement(dynamic=dynamic_power* update_interval/60, static=self.static_power* update_interval/60)

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
    """Power is consumed from a source that is renewable, we assume that the carbon intensity is small and static."""
    RENEWABLE = auto()

    """Power is consumed from a source that is unsustainable, we assume that that the carbon intensity is dynamic."""
    NONRENEWABLE = auto()

    """Power is consumed from a source that is the combination of various sources that cant be isolated to a 
    single source, as a result of this we assume that the carbon intensity is dynamic. """
    MIXED = auto()

    """Power is consumed from a local battery with a finite supply of power, it is charged by another power source,
     because the source of this power is arbitrary we infer the carbon intensity from the source it recharged from."""
    BATTERY = auto()

    """For simplicity sake will assume that only 1 Mixed power source will be allowed, as in reality a power domain 
    wont retrieve power from multiple sources that are mixed i.e. Grids """


class PowerSource(ABC):
    """Abstract class for the power sources.

            Args:
                env: Simpy environment (for timing and correct retrieval of data read from file)
                data_set_filename: filename for data of the power source (either power or carbon intensity)
                power_domain: The power domain associated with the source, we require a two-way association between
                    classes to allow for the correct starting time of the simulation as it occurs during file reading
                priority: An integer value determining the importance of the power source, priority allows for the
                    distribution of nodes when being executed, with 0 being the most important
    """
    def __init__(self, env: Environment, name, data_set_filename, power_domain=None, priority: int = 0):
        self.name = name
        self.env = env
        self.carbon_intensity = 0

        self.nodes_being_powered = []

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
        """Retrieve the current carbon intensity"""

    @abstractmethod
    def update_carbon_intensity(self):
        """Update a power sources carbon intensity"""

    def remove_node(self, node):
        if node not in self.nodes_being_powered:
            raise ValueError(f"Error: {node.id} not present in list")
        self.nodes_being_powered.remove(node)

    def _retrieve_power_data(self, data_set_filename: str, start_time: str = None):
        """Reads the data concerning the power source from file, and formats it according to the start time

                Args:
                    data_set_filename: The filename of the file
                    start_time: The string of the start time of the file, this will reshuffle the data and store
                    this time at the front and attach the data that came before it at the end

                Requirements:
                    data_set_filename: the file exists in the dataset folder and is a csv file with headers:
                        time, data
                    start_time: Must exist in the file

        """
        if start_time is None:
            raise ValueError(f"Error no start time is provided")
        # find the file path we want
        current_script_path = os.path.abspath(__file__)
        target_directory = "project-carbon-emissions-estimation-in-edge-cloud-computing-simulations"
        # Navigate upwards from the current script path until you find the target directory
        base_directory = current_script_path
        while not base_directory.endswith(target_directory):
            base_directory = os.path.dirname(base_directory)
        abs_file_path = os.path.join(base_directory + "\src\dataSets", data_set_filename)

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
    """Class for the distribution of nodes between power sources during runtime.

                Args:
                    node_distributor_method: An optional user defined custom method that allows the user to exactly
                        specify how nodes are distributed between power sources during runtime, the arguments are:
                        - The current power source being considered
                        - The power domains list of nodes (this can be filtered to only consider the subset for the
                            power source's nodes, NOTE: need to ensure at the end of an iteration all nodes of the
                            power domain have been provided a power source
                        - The update interval, as the power measurements are in Watts and the amount of power used
                            is subjective to the amount of time since the last update (the update interval) when
                           retrieving power measurements as we are in a time sensitive context we need to call
                           update_sensitive_measure(update_interval)
                    smart_distribution: A boolean value used to determine whether to allow a power source with
                        excess energy to take nodes from lower priority if the available power is there.
    """
    def __init__(self, node_distributor_method: Callable[[PowerSource, ["Node"], int], None] = None,
                 smart_distribution: bool = True):
        self.node_distributor_method = node_distributor_method or self.default_update_node_distribution_method
        self.smart_distribution = smart_distribution

    """DEFAULT Node handler for a power source, every pass of the while loop in the simulation, have to expect
    that the power sources may not be able to power their nodes, depending on the power sources provided to the 
    power domain"""
    def default_update_node_distribution_method(self, current_power_source, associated_nodes, update_interval):
        """The standard node distribution method if the user does not provide a method. The method works based on the
            knowledge that the order of execution of the method is based on priority, if power source i is passed into
            the method then all power sources prior in list powerDomain.power_sources (sources with a higher priority)
            have already been sorted so power source i should acquire as many nodes as possible. The inner working logic
            goes as:
                1. Check if all existing nodes can be powered, if not release excess nodes
                2. if remaining power is available try and add unpowered nodes to source
                3. if there is still excess power, try and add nodes being powered by less preferable power sources
            Finally there is an expectation in the default method that the last power source adds all remaining
            unpowered nodes, in order to avoid a raised exception.

                Args:
                    current_power_source: the current power source being considered
                    associated_nodes: All nodes associated with the power domain
                    update_interval: the update period, this is needed inorder to find out power requirements of nodes
                    in a time conscious context
        """

        """Update renewable sources"""
        total_current_power = current_power_source.get_current_power()

        for node in associated_nodes:
            current_node_power_requirement = float(node.power_model.update_sensitive_measure(update_interval))

            """Check if node is currently being powered by the desired power source"""
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
                if node.power_model.power_source is not None \
                        and node.power_model.power_source.priority > current_power_source.priority:
                    if current_node_power_requirement < total_current_power:
                        current_power_source.add_node(node)
                        node.power_model.power_source.remove_node(node)
                        node.power_model.power_source = current_power_source
                        total_current_power = total_current_power - current_node_power_requirement

        if current_power_source.powerType == PowerType.BATTERY:
            print(f"Updated Battery")
            current_power_source.set_current_power(total_current_power)



class PowerDomain:
    """The power domain for a collection of nodes, the main interface and point of interaction for dealing with
        Extended LEAF power classes

                Args:
                    env: Simpy environment (for timing and to allow running during the simulation)
                    name: Name of the power domain
                    node_distributor: The node distributor class to distribute nodes between power sources
                    start_time_str: A string denoting the start time of the simulation
                    associated_nodes: All nodes that want to be associated with the power domain
                    update_interval: The number of units of time between measurements of the carbon released.
                    power_source_events: a list of events the user wants to occur during runtime, the structure follows:
                        - time of event, in the format hh:mm:ss
                        - if executed, this is an internal attribute used to determine during runtime if the event has
                            already been run
                        - method, the method desired to be run
                        - args, a list arguments required by the method call

                Assumptions:
                    - 1 unit in env.timeout is equal to a minute

                Requirements:
                    name: Must be unique
                    start_time_str: must appear in all initial power source files, power sources added during execution
                        of the simulation can be ignored
    """
    def __init__(self, env: Environment, name=None, node_distributor: NodeDistributor = None,
                 start_time_str: str = "00:00:00", associated_nodes=None, update_interval: int = 1,
                 power_source_events: [(str, bool, (Callable[[], None], []))] = None):

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
        if update_interval < 1:
            raise ValueError(f"Error update interval should be positive.")
        self.update_interval = update_interval
        if power_source_events is None:
            self.power_source_events = []
        else:
            self.power_source_events = power_source_events

    def run(self, env):
        """Run method for the simpy environment, this will execute until the end of the simulation occurs,

                Args:
                    env: Simpy environment (for timing the measurements)

                Requirements:
                    -A power domain is provided with:
                        - Power source(s) to provide power to nodes
                        - Associated node(s) to provide power to
        """
        if self.power_sources is None:
            raise AttributeError(f"Error: No power source was provided")
        if not self.associated_nodes:
            raise AttributeError(f"Error: No nodes are present in the power domain")

        while True:
            yield env.timeout(self.update_interval)

            """Execute any pre-planned commands at the current moment of time"""
            for index, (time, ran, (event, args)) in enumerate(self.power_source_events):
                if (self.env.now + self.start_time_index) >= self.get_current_time(time):
                    if not ran:
                        event(*args)
                        updated_event = list(self.power_source_events[index])
                        updated_event[1] = True
                        self.power_source_events[index] = tuple(updated_event)

            self.assign_power_source_priority()

            """Go through every power source and:
                - distribute nodes among power sources
                - log the carbon released since the last update"""
            current_carbon_intensities = {}
            current_interval_released_carbon = 0
            for current_power_source in [power_source for power_source in self.power_sources if
                                         power_source is not None]:

                """distribute nodes among power sources"""
                self.node_distributor.node_distributor_method(current_power_source,
                                                              self.associated_nodes, self.update_interval)

                """Record respective power readings this interval"""
                current_ps_dictionary, current_ps_carbon_released = \
                    self.record_power_source_carbon_released(current_power_source)
                current_ps_dictionary["Total Carbon Released"] = current_ps_carbon_released
                current_carbon_intensities[current_power_source.name] = current_ps_dictionary
                current_interval_released_carbon += current_ps_carbon_released

            for node in self.associated_nodes:
                if node.power_model.power_source is None:
                    raise ValueError(f"Error: no power source found for node {node} at time {self.env.now}")

            """log the carbon released since the last update"""
            self.update_carbon_intensity(current_carbon_intensities)
            print(current_carbon_intensities)
            logger.debug(f"{env.now}: ({self.convert_to_time_string(self.env.now + self.start_time_index)}) "
                         f"{self.name} released {current_interval_released_carbon} gCO2")

    def record_power_source_carbon_released(self, current_power_source):
        current_power_source_dictionary = {}
        current_power_source_carbon_released = 0
        for node in current_power_source.nodes_being_powered:
            power_used = float(node.power_model.update_sensitive_measure(self.update_interval))
            carbon_intensity = current_power_source.get_current_carbon_intensity(0)
            carbon_released = self.calculate_carbon_released(power_used, carbon_intensity)
            node_data = {"Power Used": power_used,
                         "Carbon Intensity": carbon_intensity,
                         "Carbon Released": carbon_released}
            current_power_source_carbon_released += carbon_released
            current_power_source_dictionary[node.name] = node_data
        return current_power_source_dictionary, current_power_source_carbon_released

    def add_power_source(self, power_source):
        if power_source in self.power_sources:
            raise ValueError(f"Error: Power source {power_source.name} is already present at priority "
                             f"{self.power_sources.index(power_source)} ")

        if power_source.powerType == PowerType.MIXED and len([power_source for power_source in self.power_sources
                                                              if power_source.powerType == PowerType.MIXED]) > 0:
            raise ValueError(f"Error: Power domain can only accept 1 mixed power source")

        if power_source.priority >= len(self.power_sources):
            extra_nodes = power_source.priority - len(self.power_sources)
            self.power_sources.extend([None] * extra_nodes)
            self.power_sources.append(power_source)
        else:
            if self.power_sources[power_source.priority] is None:
                self.power_sources[power_source.priority] = power_source
            else:
                raise BufferError(f"Error: Priority {power_source.priority} "
                                  f"is occupied with {self.power_sources[power_source.priority]}")

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

    @classmethod
    def calculate_carbon_released(cls, power_used, carbon_intensity):
        return float(power_used) * (10 ** -3) * float(carbon_intensity)

    def update_carbon_intensity(self, increment_data):
        increment_total_carbon_omitted = 0
        for increment in increment_data.values():
            increment_total_carbon_omitted += increment["Total Carbon Released"]
        self.carbon_emitted.append(increment_total_carbon_omitted)  # this is to account for the time interval

    def return_total_carbon_emissions(self) -> float:
        return sum(self.carbon_emitted)

    def add_node(self, node):
        if node in self.associated_nodes:
            raise ValueError(f"Error: {node.id} already present in list")
        self.associated_nodes.append(node)

    def remove_node(self, node):
        if node not in self.associated_nodes:
            raise ValueError(f"Error: {node.id} not present in list")
        self.associated_nodes.remove(node)

    @classmethod
    def get_current_time(cls, time):
        hh, mm, ss = map(int, time.split(':'))
        return mm + (60 * hh)

    @classmethod
    def convert_to_time_string(cls, time):
        hours, minutes = divmod(time, 60)
        return f"{hours:02d}:{minutes:02d}:00"


class SolarPower(PowerSource):
    """A concrete example class of the PowerSource class

                Args:
                    (All arguments relate to the abstract class)

    """
    SOLAR_DATASET_FILENAME = "08-08-2020 Glasgow pv data.csv"

    def __init__(self, env: Environment, name: str = "Solar",data_set_filename: str = SOLAR_DATASET_FILENAME,
                 power_domain: PowerDomain = None, priority: int = 0):
        super().__init__(env, name, data_set_filename, power_domain, priority)
        self.inherent_carbon_intensity = 46
        self.powerType = PowerType.RENEWABLE

    def _get_start_time_index(self, start_time_str):
        if self.power_data is None:
            raise ValueError(f"Error: no data set has been provided")
        times = list(self.power_data.keys())
        start_time = times.index(start_time_str)
        return start_time

    def get_current_power(self) -> float:
        time = self._map_to_time((self.env.now // self.update_interval) % len(self.power_data))
        return float(self.power_data[time])

    def update_carbon_intensity(self):
        pass

    def get_current_carbon_intensity(self, offset):
        return self.inherent_carbon_intensity


class WindPower(PowerSource):
    """A concrete example class of the PowerSource class

                    Args:
                        (All arguments relate to the abstract class)

    """
    WIND_DATASET_FILENAME = "01-01-2023 Ireland wind data.csv"

    def __init__(self, env: Environment, name: str = "Wind", data_set_filename: str = WIND_DATASET_FILENAME,
                 power_domain: PowerDomain = None, priority: int = 0):
        super().__init__(env, name, data_set_filename, power_domain, priority)
        self.inherent_carbon_intensity = 12
        self.powerType = PowerType.RENEWABLE
        self.finite_power = True

    def get_current_power(self) -> float:
        time = self._map_to_time((self.env.now // self.update_interval) % len(self.power_data))
        return float(self.power_data[time])

    def update_carbon_intensity(self):
        pass

    def get_current_carbon_intensity(self, offset):
        return self.inherent_carbon_intensity


class GridPower(PowerSource):
    """A concrete example class of the PowerSource class

                        Args:
                            (All arguments relate to the abstract class)

    """
    GRID_DATASET_FILENAME = "08-08-2023 national carbon intensity.csv"

    def __init__(self, env: Environment, name: str = "Grid",data_set_filename: str = GRID_DATASET_FILENAME,
                 power_domain: PowerDomain = None, priority: int = 0):
        super().__init__(env, name, data_set_filename, power_domain, priority)
        self.carbon_intensity = 0
        self.powerType = PowerType.MIXED

    def _get_start_time_index(self, start_time_str):
        if self.power_data is None:
            raise ValueError(f"Error: no data set has been provided")
        times = list(self.power_data.keys())
        start_time = times.index(start_time_str)
        return start_time

    def update_carbon_intensity(self):
        self.carbon_intensity = self.get_current_carbon_intensity(0)

    def get_current_carbon_intensity(self, offset) -> float:
        time = self._map_to_time(((self.env.now + offset) // self.update_interval) % len(self.power_data))
        return float(self.power_data[time])

    def get_current_power(self) -> float:
        return numpy.inf


class BatteryPower(PowerSource):
    """A concrete example class of the PowerSource class

                        Args:
                            total_power_available: The total amount of power (Watts) the battery can hold
                            charge_rate: The rate at which (Watts/Hour) the battery can be recharged at

    """
    BATTERY_DATASET_FILENAME = "08-08-2023 national carbon intensity.csv"

    def __init__(self, env: Environment, data_set_filename: str = BATTERY_DATASET_FILENAME,
                 power_domain: PowerDomain = None, name: str = "Battery", priority: int = 10,
                 total_power_available=40, charge_rate=22):
        super().__init__(env, name, data_set_filename, power_domain, priority)

        self.carbon_intensity = 0  # Assumed that carbon intensity comes from power source charging it
        self.powerType = PowerType.BATTERY
        self.total_power = total_power_available  # kWh
        self.remaining_power = 0  # kWh
        self.recharge_rate = charge_rate  # kw/h
        self.recharge_data = []

    def recharge_battery(self, power_source):
        print(f"Power before:{self.remaining_power}")
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
        logger.debug(f"{self.name} was recharged by {power_source.name}, {carbon_released} gCO2 was released")
        return time_to_recharge

    def consume_battery_power(self, power_consumed):
        if power_consumed < 0:
            raise ValueError(f"Error: Power consumed cant be negative")
        if power_consumed > self.remaining_power:
            raise ValueError(f"Error: {self.name} does not have enough power for to carry out task")
        else:
            self.remaining_power -= power_consumed

    def get_next_update_time(self):
        pass

    def _get_start_time_index(self, start_time_str):
        pass

    def update_carbon_intensity(self):
        self.carbon_intensity = 0

    def get_current_carbon_intensity(self, offset) -> float:
        return 0

    def get_current_power(self) -> float:
        return self.remaining_power

    def set_current_power(self, remaining_power):
        if remaining_power < 0:
            raise ValueError(f"Error: Battery {self.name} can't store negative power")
        self.remaining_power = remaining_power
