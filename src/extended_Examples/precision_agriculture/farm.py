from typing import List, Tuple, Iterator, TypeVar, Union, Type
import networkx as nx
import simpy
from matplotlib import pyplot as plt
import matplotlib

from src.extended_Examples.precision_agriculture.power import EntityDistributor
from src.extended_Examples.precision_agriculture.infrastructure import *
from mobility import Location
from src.extended_Examples.precision_agriculture.orchestrator import CityOrchestrator
from src.extended_Examples.precision_agriculture.power import PowerDomain, SolarPower, GridPower, EntityDistributor, \
    PowerSource
from src.extended_Examples.precision_agriculture.settings import *
from src.extendedLeaf.infrastructure import Infrastructure, Node

matplotlib.use('TkAgg')
_recharge_station_counter: int = 0


class Plot:
    def __init__(self, env: simpy.Environment, infrastructure: Infrastructure, plot_index, start_time, name: str = "Plot", power_sources_types=None):
        if power_sources_types is None:
            raise ValueError(f"Error: No power sources provided")
        self.env = env
        self.graph, sensor_locations, fog_location = _create_plot_graph(plot_index)
        self.name = name

        self.power_domain = PowerDomain(self.env, name=f"{self.name}_power_domain", start_time_str=start_time, update_interval=1)
        self.power_sources = [self._choose_power_source(power_source_type) for power_source_type in power_sources_types]
        self.sensors = [CropSensor(infrastructure, self, index, sensor_location) for index, sensor_location in enumerate(sensor_locations)]
        self.fog_node = self._add_fog_node(infrastructure, fog_location)
        cloud = infrastructure.nodes(type_filter=Cloud)[0]
        infrastructure.add_link(LinkEthernet(self.fog_node, cloud, f"Link_{self.fog_node.name}_to_{cloud.name}"))

    def _add_fog_node(self, infrastructure: Infrastructure, location: Location) -> FogNode:
        """Fog nodes are connected to a traffic lights via Ethernet (no power usage)"""
        fog_node = FogNode(self, location)
        infrastructure.add_node(fog_node)
        for sensor in self.sensors:
            infrastructure.add_link(LinkEthernet(sensor, fog_node, f"Link_{sensor.name}_to_{fog_node.name}"))
            infrastructure.add_link(LinkEthernet(fog_node, sensor, f"Link_{fog_node.name}_to_{sensor.name}"))
        return fog_node

    def _choose_power_source(self, power_source) -> PowerSource:
        """ def __init__(self, env: Environment, name: str = "Grid", data_set_filename: str = GRID_DATASET_FILENAME,
                     power_domain: PowerDomain = None, priority: int = 0, powered_entities=None):"""
        if power_source == SolarPower:
            return_power_source = SolarPower(self.env, power_domain=self.power_domain, priority=0)
            self.power_domain.add_power_source(return_power_source)
            return return_power_source
        elif power_source == GridPower:
            return_power_source = GridPower(self.env, power_domain=self.power_domain, priority=5)
            self.power_domain.add_power_source(return_power_source)
            return return_power_source
        elif power_source == WindPower:
            return_power_source = WindPower(self.env, power_domain=self.power_domain, priority=1)
            self.power_domain.add_power_source(return_power_source)
            return return_power_source


def _create_plot_graph(current_plot_index):
    graph = nx.Graph()
    sensor_locations: [Location]
    fog_node_location: Location = Location(0, 0)

    n_points = SENSORS_PER_AXIS
    step_size_x = PLOT_SIZES[current_plot_index][0] / (n_points - 1)
    step_size_y = PLOT_SIZES[current_plot_index][1] / (n_points - 1)

    sensor_locations = [[None for _ in range(n_points)] for _ in range(n_points)]
    for x in range(n_points):
        for y in range(n_points):
            location = Location((x + 1) * step_size_x, y * step_size_y)
            sensor_locations[x][y] = location
            graph.add_node(location)
            if x > 0:
                graph.add_edge(location, sensor_locations[x - 1][y])
            if y > 0:
                graph.add_edge(location, sensor_locations[x][y - 1])

    graph.add_edge(fog_node_location, sensor_locations[0][0])

    return graph, sensor_locations, fog_node_location


class Farm:
    def __init__(self, env: simpy.Environment, start_time="12:00:00"):
        self.env = env
        self.farm_graph, self.entry_point_locations, self.recharge_locations = _create_street_graph()

        self.infrastructure = Infrastructure()
        self.cloud = Cloud()
        self.infrastructure.add_node(self.cloud)
        self.plots: [Plot] = self._create_farm_plots(start_time)

        """main_graph = nx.Graph()
        for plot_index, plot in enumerate(self.plots, start=1):
            mapping = {node: f'G{plot_index}_{node}' for node in plot.graph.nodes}
            plot.graph = nx.relabel_nodes(plot.graph, mapping)
            main_graph = nx.union(plot.graph, main_graph)
        pos = nx.spring_layout(main_graph)"""

        # Draw the combined graph with the specified layout
        """
        pos = nx.spring_layout(main_graph)
        nx.draw(main_graph, pos, with_labels=False, node_size=500, node_color="skyblue", font_size=8, font_color="black", font_weight="bold", edge_color="gray", width=0.5)
        plt.title('Combined Graph')
        plt.show()"""

    def run(self, env):
        for plot in self.plots:
            env.process(plot.power_domain.run(env))

    def _create_farm_plots(self, start_time) -> [Plot]:
        plots = []
        occupied_locations = []  # perimeter = [(top left),(bottom_right)]
        for current_plot_index in range(NUMBER_OF_PLOTS):
            current_plot = Plot(self.env, self.infrastructure, current_plot_index, start_time,
                                name=f"{PLOT_NAMES[current_plot_index]}", power_sources_types=POWER_SOURCES_AVAILABLE[current_plot_index])
            plots.append(current_plot)
        return plots


class City:
    _TNode = TypeVar("_TNode", bound=Node)  # Generics
    _NodeTypeFilter = Union[Type[_TNode], Tuple[Type[_TNode], ...]]

    def __init__(self, env: simpy.Environment):
        self.env = env
        self.street_graph, self.entry_point_locations, self.recharge_locations = _create_street_graph()

        self.infrastructure = Infrastructure()

        # Create infrastructure
        self.infrastructure.add_node(Cloud())

        self.power_domains = []
        for location in self.recharge_locations:
            self.power_domains.append(self._add_recharge_station(self.env, location))

    def _add_recharge_station(self, env: simpy.Environment, location: Location):
        """Recharge Points are connected to the cloud via WAN, they are powered by solar panels and the National Grid"""
        global _recharge_station_counter
        cloud: Cloud = self.infrastructure.nodes(type_filter=Cloud)[0]
        recharge_station = RechargeStation(location=location, application_sink=cloud,
                                           _recharge_station_counter=_recharge_station_counter)
        power_domain = PowerDomain(env, name=f"Power Domain Recharge Station {_recharge_station_counter}",
                                   entity_distributor=EntityDistributor(static_entities=False),
                                   start_time_str=START_TIME, update_interval=1, powered_entities=[recharge_station])
        solar_power = SolarPower(env, name=f"Solar Panel Recharge Station {_recharge_station_counter}",
                                 power_domain=power_domain, priority=0)
        grid1 = GridPower(env, power_domain=power_domain, priority=5)
        power_domain.add_power_source(grid1)
        power_domain.add_power_source(solar_power)

        self.infrastructure.add_link(
            LinkWanUp(name=f"Link up {_recharge_station_counter}", src=recharge_station, dst=cloud))
        self.infrastructure.add_link(
            LinkWanDown(name=f"Link up {_recharge_station_counter}", src=cloud, dst=recharge_station))
        _recharge_station_counter += 1
        return power_domain

    def find_power_domain_containing_node(self, node_name):
        for power_domain in self.power_domains:
            for node in power_domain.powered_entities:
                if node.name == node_name:
                    return power_domain
        return None

    def _update_wifi_connections(self):
        """Recalculates the traffic lights in range for all taxis."""
        g = self.infrastructure.graph
        while True:
            yield self.env.timeout(UPDATE_WIFI_CONNECTIONS_INTERVAL)
            for taxi in self.infrastructure.nodes(type_filter=Taxi):
                tl_connected_name = next(g.neighbors(taxi.name))
                tl_closest = self._closest_traffic_light(taxi)
                if tl_connected_name != tl_closest.name:
                    g.remove_edge(taxi.name, tl_connected_name)
                    self.infrastructure.add_link(LinkWifiTaxiToTrafficLight(taxi, tl_closest))

    def _traffic_lights_in_range(self, traffic_light: TrafficLight) -> Iterator[TrafficLight]:
        for tl in self.infrastructure.nodes(type_filter=TrafficLight):
            if traffic_light.location.distance(tl.location) <= WIFI_RANGE:
                yield tl

    def _closest_traffic_light(self, taxi: Taxi) -> TrafficLight:
        return min(self.infrastructure.nodes(type_filter=TrafficLight),
                   key=lambda tl: taxi.location.distance(tl.location))


def _create_street_graph() -> Tuple[nx.Graph, List[Location], List[Location]]:
    graph = nx.Graph()
    """Need to consider, charge points, smart cameras and entry points"""
    n_points = STREETS_PER_AXIS + 2  # plus two accounting for removal of corners
    step_size_x = CITY_WIDTH / (n_points - 1)
    step_size_y = CITY_HEIGHT / (n_points - 1)

    entry_point_locations = []
    locations = [[None for _ in range(n_points)] for _ in range(n_points)]
    for x in range(n_points):
        for y in range(n_points):
            location = Location(x * step_size_x, y * step_size_y)
            if x == 0 or x == (n_points - 1) or y == 0 or y == (n_points - 1):
                entry_point_locations.append(location)
            locations[x][y] = location
            graph.add_node(location)
            if x > 0 and y > 0:
                if y < n_points - 1:
                    graph.add_edge(location, locations[x - 1][y])
                if x < n_points - 1:
                    graph.add_edge(location, locations[x][y - 1])

    for corner_location in [locations[0][0],
                            locations[n_points - 1][0],
                            locations[0][n_points - 1],
                            locations[n_points - 1][n_points - 1]]:
        graph.remove_node(corner_location)
        entry_point_locations.remove(corner_location)

    potential_charging_points = []
    for x in range(n_points):
        for y in range(n_points):
            location = locations[x][y]
            if location not in entry_point_locations:
                potential_charging_points.append(location)

    charging_points = RNG.choice(potential_charging_points, size=NUMBER_RECHARGE_POINTS, replace=False)

    return graph, entry_point_locations, charging_points
