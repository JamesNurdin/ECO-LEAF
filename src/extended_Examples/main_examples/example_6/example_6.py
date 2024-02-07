import logging

import networkx as nx
import numpy as np
import simpy
from src.extendedLeaf.application import Task, Application, SourceTask, ProcessingTask, SinkTask
from src.extendedLeaf.events import EventDomain, PowerDomainEvent
from src.extendedLeaf.file_handler import FileHandler, FigurePlotter
from src.extendedLeaf.infrastructure import Node, Link, Infrastructure
from src.extendedLeaf.orchestrator import Orchestrator
from src.extendedLeaf.power import PowerModelNode, PowerMeasurement, PowerMeter, PowerModelLink, SolarPower, WindPower, \
    GridPower, PowerDomain, BatteryPower, PoweredInfrastructureDistributor
from src.extended_Examples.main_examples.example_6.settings import *

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')


def main():
    """
    Log Output:
    DEBUG	0: application_meter: PowerMeasurement(dynamic=0.00W, static=0.00W)
    DEBUG	0: application_meter: PowerMeasurement(dynamic=0.00W, static=0.00W)
    DEBUG	0: infrastructure_meter: PowerMeasurement(dynamic=0.00W, static=24.00W)
    DEBUG	1: application_meter: PowerMeasurement(dynamic=0.00W, static=0.00W)
    DEBUG	1: application_meter: PowerMeasurement(dynamic=0.00W, static=0.00W)
    DEBUG	1: infrastructure_meter: PowerMeasurement(dynamic=0.00W, static=24.00W)
    ...
    DEBUG	148: application_meter: PowerMeasurement(dynamic=0.00W, static=0.00W)
    DEBUG	148: application_meter: PowerMeasurement(dynamic=13.77W, static=3.00W)
    DEBUG	148: infrastructure_meter: PowerMeasurement(dynamic=34.89W, static=24.00W)
    DEBUG	149: application_meter: PowerMeasurement(dynamic=0.00W, static=0.00W)
    DEBUG	149: application_meter: PowerMeasurement(dynamic=13.77W, static=3.00W)
    DEBUG	149: infrastructure_meter: PowerMeasurement(dynamic=34.89W, static=24.00W)
    INFO	Total application power usage: 5334.118215384617 Ws
    INFO	Total application power usage: 6149.721237948734 Ws
    INFO	Total infrastructure power usage: 14544.43333333332 Ws
    INFO	Total carbon emitted: 35.62215131399992 gCo2
    """
    env = simpy.Environment()  # creating SimPy simulation environment
    infrastructure = Infrastructure()

    # Initializing infrastructure and workload
    source_node = Node("source_node", cu=40, power_model=PowerModelNode(max_power=30, static_power=3))  # Source
    grid_node = Node("grid_node", cu=20, power_model=PowerModelNode(max_power=40, static_power=5))  # processing task
    solar_node = Node("solar_node", cu=40, power_model=PowerModelNode(max_power=70, static_power=10))  # processing task
    battery_node = Node("battery_node", cu=30, power_model=PowerModelNode(max_power=50, static_power=7))  # processing task
    sink_node = Node("sink_node", cu=25, power_model=PowerModelNode(max_power=50, static_power=6))  # sink
    source_link_to_grid = Link(name="source_link_to_grid 1", src=source_node, dst=grid_node, latency=10, bandwidth=30e6, power_model=PowerModelLink(300e-9))
    grid_link_to_sink = Link(name="grid_link_to_sink 2", src=grid_node, dst=sink_node, latency=12, bandwidth=50e6, power_model=PowerModelLink(400e-9))
    source_link_to_solar = Link(name="source_link_to_solar 2", src=source_node, dst=solar_node, latency=12, bandwidth=50e6, power_model=PowerModelLink(400e-9))
    solar_link_to_battery = Link(name="solar_link_to_battery 2", src=solar_node, dst=battery_node, latency=12, bandwidth=50e6, power_model=PowerModelLink(400e-9))
    source_link_to_battery = Link(name="source_link_to_battery 2", src=source_node, dst=battery_node, latency=12, bandwidth=50e6, power_model=PowerModelLink(400e-9))
    battery_link_to_sink = Link(name="battery_link_to_sink 2", src=battery_node, dst=sink_node, latency=12, bandwidth=50e6, power_model=PowerModelLink(400e-9))
    all_entities = [source_node,grid_node,solar_node,battery_node,sink_node,source_link_to_grid,grid_link_to_sink,source_link_to_solar,solar_link_to_battery,
                    source_link_to_battery, battery_link_to_sink]
    infrastructure.add_link(source_link_to_grid)
    infrastructure.add_link(grid_link_to_sink)
    infrastructure.add_link(source_link_to_solar)
    infrastructure.add_link(solar_link_to_battery)
    infrastructure.add_link(source_link_to_battery)
    infrastructure.add_link(battery_link_to_sink)

    power_domain = PowerDomain(env, name="Power Domain 1",
                               start_time_str="15:00:00", update_interval=1, powered_infrastructure_distributor=
                               PoweredInfrastructureDistributor(static_powered_infrastructure=True))

    grid_power = GridPower(env, power_domain=power_domain, priority=5, powered_infrastructure=[grid_node, sink_node, grid_link_to_sink])
    solar_power = SolarPower(env, power_domain=power_domain, priority=1, powered_infrastructure=[source_node, solar_node, source_link_to_solar, source_link_to_battery, source_link_to_grid])
    battery_power = BatteryPower(env, power_domain=power_domain, priority=0, total_power_available=30,
                                 powered_infrastructure=[battery_node, battery_link_to_sink])
    power_domain.add_power_source(grid_power)
    power_domain.add_power_source(solar_power)
    power_domain.add_power_source(battery_power)

    # three nodes 1,2,3
    # #two Wi-Fi links between 1 -> 2 and 2 -> 3

    # Initialise three tasks
    app1_source_task = SourceTask(cu=0.4, bound_node=source_node)
    app1_processing_task = ProcessingTask(cu=20)
    app1_sink_task = SinkTask(cu=12, bound_node=sink_node)

    app2_source_task = SourceTask(cu=0.4, bound_node=source_node)
    app2_processing_task1 = ProcessingTask(cu=20)
    app2_processing_task2 = ProcessingTask(cu=20)
    app2_sink_task = SinkTask(cu=12, bound_node=sink_node)

    # Build Applications
    application1 = Application(name="Application1")
    application1.add_task(app1_source_task)
    application1.add_task(app1_processing_task, incoming_data_flows=[(app1_source_task, 1000)])
    application1.add_task(app1_sink_task, incoming_data_flows=[(app1_processing_task, 300)])

    application2 = Application(name="Application2")
    application2.add_task(app2_source_task)
    application2.add_task(app2_processing_task1, incoming_data_flows=[(app2_source_task, 1000)])
    application2.add_task(app2_processing_task2, incoming_data_flows=[(app2_processing_task1, 1000)])
    application2.add_task(app2_sink_task, incoming_data_flows=[(app2_processing_task2, 300)])

    # Place over Infrastructure
    orchestrator = SimpleOrchestrator(infrastructure, power_domain)
    # orchestrator.place(application2)

    event_domain = EventDomain(env, update_interval=1, start_time_str="15:00:00")
    event_domain.add_event(PowerDomainEvent(event=orchestrator.place, args=[application1], time_str="15:10:00", repeat=False))
    event_domain.add_event(PowerDomainEvent(event=battery_power.recharge_battery, args=[solar_power], time_str="15:30:00", repeat=False))
    event_domain.add_event(PowerDomainEvent(event=orchestrator.place, args=[application2], time_str="15:40:00", repeat=False))
    event_domain.add_event(PowerDomainEvent(event=battery_power.recharge_battery, args=[solar_power], time_str="16:00:00", repeat=False))
    event_domain.add_event(PowerDomainEvent(event=application1.deallocate, args=[], time_str="16:30:00", repeat=False))
    event_domain.add_event(PowerDomainEvent(event=battery_power.recharge_battery, args=[solar_power], time_str="17:00:00", repeat=False))

    # Early power meters when exploring isolated power measurements
    application1_pm = PowerMeter(application1, name="application_meter")
    application2_pm = PowerMeter(application2, name="application_meter")
    infrastructure_pm = PowerMeter(infrastructure.nodes(), name="infrastructure_meter", measurement_interval=1)

    # Run simulation
    env.process(power_domain.run(env))
    env.process(event_domain.run())
    env.process(application1_pm.run(env))
    env.process(application2_pm.run(env))

    env.process(infrastructure_pm.run(env))

    env.run(until=150)

    logger.info(f"Total application power usage: {float(PowerMeasurement.sum(application1_pm.measurements))} Ws")
    logger.info(f"Total application power usage: {float(PowerMeasurement.sum(application2_pm.measurements))} Ws")
    logger.info(f"Total infrastructure power usage: {float(PowerMeasurement.sum(infrastructure_pm.measurements))} Ws")
    logger.info(f"Total carbon emitted: {power_domain.return_total_carbon_emissions()} gCo2")

    file_handler = FileHandler()
    filename = "Results.Json"
    file_handler.write_out_results(filename=filename, power_domain=power_domain)

    figure_plotter = FigurePlotter(power_domain, event_domain, show_event_lines=True)
    fig2 = figure_plotter.subplot_time_series_entities("Power Used", entities=all_entities)
    fig3 = figure_plotter.subplot_time_series_power_sources("Power Available", power_sources=[solar_power, battery_power])
    fig4 = figure_plotter.subplot_time_series_power_meter(power_meters=[application1_pm,application2_pm,infrastructure_pm])
    figs = [fig2, fig3, fig4]
    main_fig = figure_plotter.aggregate_subplots(figs)
    file_handler.write_figure_to_file(main_fig, len(figs))
    main_fig.show()


class SimpleOrchestrator(Orchestrator):
    def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
        dest_node = self.infrastructure.node("sink_node")
        source_node = self.infrastructure.node("source_node")
        paths = list(nx.all_simple_paths(self.infrastructure.graph, source=source_node.name, target=dest_node.name))
        # iterate through all the potential nodes
        current_best_carbon_intensity = np.inf
        return_node = None
        for path in paths:
            for i, node in enumerate(path):
                node = self.infrastructure.node(node)
                remaining_path = path[i:]
                if len(application.get_application_paths(processing_task)[0]) == len(remaining_path):
                    if node.paused is False:
                        power_source = node.power_model.power_source
                        carbon_intensity = power_source.get_current_carbon_intensity(0)
                        if carbon_intensity < current_best_carbon_intensity:
                            return_node = node
                            current_best_carbon_intensity = carbon_intensity

        return return_node


if __name__ == '__main__':
    main()

import logging

import networkx as nx
import simpy
import random as rnd

from src.extendedLeaf.animate import Animation
from src.extendedLeaf.application import Task, Application, SourceTask, ProcessingTask, SinkTask
from src.extendedLeaf.events import EventDomain, PowerDomainEvent
from src.extendedLeaf.file_handler import FileHandler, FigurePlotter
from src.extendedLeaf.infrastructure import Node, Link, Infrastructure
from src.extendedLeaf.orchestrator import Orchestrator
from src.extendedLeaf.power import PowerModelNode, PowerMeasurement, PowerMeter, PowerModelLink, SolarPower, WindPower, \
    GridPower, PowerDomain, BatteryPower, PoweredInfrastructureDistributor
from src.extended_Examples.main_examples.example_5.settings import *

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')
rnd.seed(100)


def create_sensors():
    sensors = []
    for current_sensor_index in range(NO_SENSORS):
        max_power = rnd.gauss(SENSOR_MAX_POWER_MEAN, SENSOR_MAX_POWER_STD_DEVIATION)
        static_power = rnd.gauss(SENSOR_STATIC_POWER_MEAN, SENSOR_STATIC_POWER_STD_DEVIATION)
        cu = rnd.gauss(SENSOR_CU_POWER_MEAN, SENSOR_CU_STD_DEVIATION)
        sensors.append(Node(f"Sensor{current_sensor_index}", cu=cu,
                            power_model=PowerModelNode(max_power=max_power, static_power=static_power)))
    return sensors


def create_microprocessors(no_microproc):
    microprocessors = []
    for current_sensor_index in range(no_microproc):
        max_power = rnd.gauss(MICROPROCESSORS_MAX_POWER_MEAN, MICROPROCESSORS_MAX_POWER_STD_DEVIATION)
        static_power = rnd.gauss(MICROPROCESSORS_STATIC_POWER_MEAN, MICROPROCESSORS_STATIC_POWER_STD_DEVIATION)
        cu = rnd.gauss(MICROPROCESSORS_CU_POWER_MEAN, MICROPROCESSORS_CU_STD_DEVIATION)
        microprocessors.append(Node(f"Microprocessor{current_sensor_index}", cu=cu,
                                    power_model=PowerModelNode(max_power=max_power, static_power=static_power)))
    return microprocessors


def create_links_from_sensors(sensors, microprocessors):
    links = []
    for sensor in sensors:
        microprocessor = rnd.choice(microprocessors)
        bandwidth = rnd.gauss(WIRED_BANDWIDTH_MEAN, WIRED_BANDWIDTH_STD_DEVIATION)
        energy_per_bit = rnd.gauss(WIRED_ENERGY_PER_BIT_MEAN, WIRED_ENERGY_PER_BIT_STD_DEVIATION)
        links.append(Link(name=f"Link_from{sensor.name}_to_{microprocessor.name}", src=sensor, dst=microprocessor,
                          latency=0, bandwidth=bandwidth, power_model=PowerModelLink(energy_per_bit)))
    return links


def create_links_to_server(microprocessors, server):
    links = []
    for microprocessor in microprocessors:
        bandwidth = rnd.gauss(WIRELESS_BANDWIDTH_MEAN, WIRELESS_BANDWIDTH_STD_DEVIATION)
        energy_per_bit = rnd.gauss(WIRELESS_ENERGY_PER_BIT_MEAN, WIRELESS_ENERGY_PER_BIT_STD_DEVIATION)
        links.append(Link(name=f"Link_from{microprocessor.name}_to_{server.name}", src=microprocessor,
                          dst=server, latency=0, bandwidth=bandwidth, power_model=PowerModelLink(energy_per_bit)))
    return links


def create_applications(sensors, server):
    applications = []
    for sensor in sensors:
        app1_source_task = SourceTask(cu=0.9 * sensor.power_model.max_power, bound_node=sensor)
        app1_processing_task = ProcessingTask(cu=3)
        app1_sink_task = SinkTask(cu=12, bound_node=server)

        application = Application(name=f"Application{sensor.name}")

        application.add_task(app1_source_task)
        application.add_task(app1_processing_task, incoming_data_flows=[(app1_source_task, 1000)])
        application.add_task(app1_sink_task, incoming_data_flows=[(app1_processing_task, 300)])

        applications.append(application)
    return applications


def main():
    """
    Log Output:
        INFO	Placing Application(tasks=3):
        INFO	- SourceTask(id=0, cu=0.15313193982744164) on Node('Sensor0', cu=0/11.018082741964426).
        INFO	- ProcessingTask(id=1, cu=3) on Node('Microprocessor1', cu=0/44.006079736990166).
        INFO	- SinkTask(id=2, cu=12) on Node('Server', cu=0/inf).
        INFO	- DataFlow(bit_rate=1000) on [Link('Sensor0' -> 'Microprocessor1', bandwidth=0/54214721.2845746)].
        INFO	- DataFlow(bit_rate=300) on [Link('Microprocessor1' -> 'Server', bandwidth=0/30394186.81448846)].
        ...
        DEBUG	597: infrastructure_meter: PowerMeasurement(dynamic=6.25W, static=121.27W)
        DEBUG	598: infrastructure_meter: PowerMeasurement(dynamic=6.25W, static=121.27W)
        DEBUG	599: infrastructure_meter: PowerMeasurement(dynamic=6.25W, static=121.27W)
        INFO	Total infrastructure power usage: 73607.19502847278 Ws
        INFO	Total carbon emitted: 201.0099958668859 gCo2
    """
    env = simpy.Environment()  # creating SimPy simulation environment
    infrastructure = Infrastructure()

    # Initializing infrastructure and workload
    sensors = create_sensors()
    solar_microprocessors = create_microprocessors(NO_SOLAR_MICROPROCESSORS)
    battery_microprocessors = create_microprocessors(NO_BAT_MICROPROCESSORS)
    grid_microprocessors = create_microprocessors(NO_GRID_MICROPROCESSORS)
    all_microprocessors = solar_microprocessors + battery_microprocessors + grid_microprocessors

    server = Node("Server", power_model=PowerModelNode(power_per_cu=SERVER_POWER_PER_CU,
                                                       static_power=SERVER_STATIC_POWER))  # sink

    links_from_sensors = create_links_from_sensors(sensors, microprocessors)
    links_to_server = create_links_to_server(microprocessors, server)
    for link in links_from_sensors + links_to_server:
        infrastructure.add_link(link)
    entities = sensors + microprocessors + links_from_sensors + links_to_server

    power_domain = PowerDomain(env, name="Power Domain 1",
                               start_time_str="10:00:00", update_interval=1, powered_infrastructure_distributor=
                               PoweredInfrastructureDistributor(static_powered_infrastructure=True))
    solar_power = SolarPower(env, power_domain=power_domain, priority=1, powered_infrastructure=[])
    grid_power = GridPower(env, power_domain=power_domain, priority=5,
                           powered_infrastructure=[server] + links_to_server)
    battery_power = BatteryPower(env, power_domain=power_domain, priority=0, total_power_available=175,
                                 powered_infrastructure=sensors + microprocessors + links_from_sensors)
    power_domain.add_power_source(battery_power)
    power_domain.add_power_source(solar_power)
    power_domain.add_power_source(grid_power)

    applications = create_applications(sensors, server)

    orchestrator = CustomOrchestrator(infrastructure, power_domain)
    for application in applications:
        orchestrator.place(application)

    event_domain = EventDomain(env, update_interval=1, start_time_str="10:00:00")
    event_domain.add_event(
        PowerDomainEvent(event=battery_power.recharge_battery, args=[solar_power], time_str="10:30:00", repeat=True,
                         repeat_counter=500))

    infrastructure_pm = PowerMeter(infrastructure.nodes(), name="infrastructure_meter", measurement_interval=1)

    # Run simulation
    env.process(power_domain.run(env))
    env.process(event_domain.run())

    env.process(infrastructure_pm.run(env))

    env.run(until=600)  # run the simulation for 10 hours (until the battery is fully drained)

    logger.info(f"Total infrastructure power usage: {float(PowerMeasurement.sum(infrastructure_pm.measurements))} Ws")
    logger.info(f"Total carbon emitted: {power_domain.return_total_carbon_emissions()} gCo2")

    file_handler = FileHandler()
    filename = "Results.Json"
    file_handler.write_out_results(filename=filename, power_domain=power_domain)

    figure_plotter = FigurePlotter(power_domain, event_domain, show_event_lines=True)
    event_figure = figure_plotter.subplot_events(event_domain.event_history)
    fig1 = figure_plotter.subplot_time_series_entities("Power Used", entities=entities)
    fig2 = figure_plotter.subplot_time_series_power_sources("Power Used", power_sources=[solar_power, battery_power])
    fig3 = figure_plotter.subplot_time_series_power_sources("Power Available", power_sources=[battery_power])
    figs = [event_figure, fig1, fig2, fig3]
    main_fig = figure_plotter.aggregate_subplots(figs)
    file_handler.write_figure_to_file(figure=main_fig, number_of_figs=len(figs))
    main_fig.show()

    animation = Animation(power_domains=[power_domain], env=env, speed_sec=2.5)
    animation.run_animation()


class CustomOrchestrator(Orchestrator):
    def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
        source_node = application.tasks(type_filter=SourceTask)[0].node
        dest_node = self.infrastructure.node("Server")
        paths = list(nx.all_simple_paths(self.infrastructure.graph, source=source_node.name, target=dest_node.name))

        return self.infrastructure.node(paths[0][1])


if __name__ == '__main__':
    main()
