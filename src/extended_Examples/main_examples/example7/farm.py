import networkx as nx
import matplotlib
import simpy

from src.extended_Examples.main_examples.example7.infrastructure import *
from src.extendedLeaf.mobility import Location
from src.extended_Examples.main_examples.example7.orchestrator import FarmOrchestrator
from src.extendedLeaf.power import PowerDomain, PowerSource
from src.extended_Examples.main_examples.example7.settings import *
from src.extendedLeaf.infrastructure import Infrastructure

matplotlib.use('TkAgg')
_recharge_station_counter = 0


class Plot:
    def __init__(self, env: simpy.Environment, infrastructure: Infrastructure, plot_index, start_time, name: str = "Plot"):
        self.env = env
        self.graph, self.sensor_locations, self.fog_location = _create_plot_graph(plot_index)
        self.recharge_station_location = self.fog_location
        self.name = name
        self.plot_index = plot_index

        self.sensors = self.create_sensors(infrastructure)

        self.fog_node = self._add_fog_node(infrastructure, self.fog_location)
        cloud = infrastructure.nodes(type_filter=Cloud)[0]

        infrastructure.add_link(LinkEthernet(self.fog_node, cloud, f"Link_{self.fog_node.name}_to_{cloud.name}"))

        global _recharge_station_counter
        self.recharge_station = RechargeStation(self.recharge_station_location, cloud, _recharge_station_counter)
        _recharge_station_counter += 1

        self.power_domain = PowerDomain(self.env, name=f"{self.name}_power_domain", start_time_str=start_time,
                                        update_interval=1)
        self.power_sources = [self._choose_power_source(power_source_type) for power_source_type in
                              POWER_SOURCES_AVAILABLE[self.plot_index]]

        self.all_entities = self.sensors + [self.fog_node]

        if DRONE_DISTRIBUTION[self.plot_index]:
            self.drone = Drone(self, self.fog_location, self.env, self.power_domain, infrastructure)

            self.all_entities.append(self.drone)
            infrastructure.add_node(self.drone)
            infrastructure.add_link(LinkWanUp(self.drone, self.fog_node, f"Link_{self.drone.name}_to_{self.fog_node.name}"))
            self.power_domain.add_power_source(self.drone.battery_power)
            self.power_sources.append(self.drone.battery_power)
        else:
            self.drone = None

        for sensor in self.sensors:
            if STATIC_CONFIG[self.plot_index]:
                self.power_sources[0].add_entity(sensor)
            else:
                self.power_domain.add_entity(sensor)

        if STATIC_CONFIG[self.plot_index]:
            self.power_sources[0].add_entity(self.fog_node)
        else:
            self.power_domain.add_entity(self.fog_node)

        self.orchestrator = FarmOrchestrator(infrastructure, self.power_domain)

    def _add_fog_node(self, infrastructure: Infrastructure, location: Location) -> FogNode:
        fog_node = FogNode(self, location)
        infrastructure.add_node(fog_node)
        for sensor in self.sensors:
            infrastructure.add_link(LinkEthernet(sensor, fog_node, f"Link_{sensor.name}_to_{fog_node.name}"))
            infrastructure.add_link(LinkEthernet(fog_node, sensor, f"Link_{fog_node.name}_to_{sensor.name}"))
        return fog_node

    def _choose_power_source(self, power_source) -> PowerSource:
        if power_source == SolarPower:
            return_power_source = SolarPower(self.env, name=f"plot_{self.plot_index}_solar_power",
                                             power_domain=self.power_domain, priority=0,
                                             static=STATIC_CONFIG[self.plot_index])
            self.power_domain.add_power_source(return_power_source)
            return return_power_source
        elif power_source == GridPower:
            return_power_source = GridPower(self.env, name=f"plot_{self.plot_index}_grid_power",
                                            power_domain=self.power_domain, priority=5,
                                            static=STATIC_CONFIG[self.plot_index])
            self.power_domain.add_power_source(return_power_source)
            return return_power_source
        elif power_source == WindPower:
            return_power_source = WindPower(self.env, name=f"plot_{self.plot_index}_wind_power",
                                            power_domain=self.power_domain, priority=2,
                                            static=STATIC_CONFIG[self.plot_index])
            self.power_domain.add_power_source(return_power_source)
            return return_power_source

    def get_drone_path(self):
        path: [Location]

        n_points = int(SENSORS_PER_AXIS[self.plot_index] * DRONE_MEASURE_DENSITY) - 1
        step_size_x = PLOT_SIZES[self.plot_index][0] / (n_points - 1)
        step_size_y = PLOT_SIZES[self.plot_index][1] / (n_points - 1)
        offset_x = step_size_x // 2
        offset_y = step_size_y // 2

        path = []
        for x in range(n_points):
            for y in range(n_points):
                location = Location(((x + 1) * step_size_x) + offset_x, (y * step_size_y) + offset_y)
                path.append(location)
        path.append(self.recharge_station_location)
        return iter(path)

    def create_sensors(self, infrastructure):
        sensors = []
        index = 0
        for x in range(SENSORS_PER_AXIS[self.plot_index]):
            for y in range(SENSORS_PER_AXIS[self.plot_index]):
                sensor_location = self.sensor_locations[x][y]
                sensors.append(CropSensor(infrastructure, self, index, sensor_location))
                index += 1
        return sensors


def _create_plot_graph(current_plot_index):
    graph = nx.Graph()
    sensor_locations: [Location]
    fog_node_location: Location = Location(0, 0)

    n_points = SENSORS_PER_AXIS[current_plot_index]
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
    """
        Farm class depicting the entire infrastructure of the scenario. A farm will contain multiple plots depicting
        various plots and connected infrastructure, every plot will be connected to each other through fog nodes
        which connect to a central cloud/server node acting as a sink for all processing tasks.
    """
    def __init__(self, env: simpy.Environment):
        self.env = env
        self.infrastructure = Infrastructure()
        self.cloud = Cloud()
        self.infrastructure.add_node(self.cloud)
        self.plots: [Plot] = self._create_farm_plots(START_TIME)

    def run(self, env):
        for plot in self.plots:
            env.process(plot.power_domain.run(env))

    def deploy_sensor_applications(self):
        for plot in self.plots:
            for sensor in plot.sensors:
                plot.orchestrator.place(sensor.application)

    def terminate_sensor_applications(self):
        for plot in self.plots:
            for sensor in plot.sensors:
                sensor.application.deallocate()


    def _create_farm_plots(self, start_time) -> [Plot]:
        plots = []
        for current_plot_index in range(NUMBER_OF_PLOTS):
            current_plot = Plot(self.env, self.infrastructure, current_plot_index, start_time,
                                name=f"{PLOT_NAMES[current_plot_index]}")
            plots.append(current_plot)
        return plots

