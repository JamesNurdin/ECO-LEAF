import logging

import networkx as nx
import simpy
import random as rnd

from src.extendedLeaf.animate import Animation
from src.extendedLeaf.application import Task, Application, SourceTask, ProcessingTask, SinkTask
from src.extendedLeaf.events import EventDomain, Event
from src.extendedLeaf.file_handler import FileHandler, FigurePlotter
from src.extendedLeaf.infrastructure import Node, Link, Infrastructure
from src.extendedLeaf.orchestrator import Orchestrator
from src.extendedLeaf.power import PowerModelNode, PowerMeasurement, PowerMeter, PowerModelLink, SolarPower, WindPower, \
    GridPower, PowerDomain, BatteryPower, PoweredInfrastructureDistributor
from src.extended_Examples.main_examples.example_6.settings import *

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')
rnd.seed(100)


def create_sensors():
    sensors = []
    for current_sensor_index in range(NO_SENSORS):
        max_power = rnd.gauss(SENSOR_MAX_POWER_MEAN, SENSOR_MAX_POWER_STD_DEVIATION)
        static_power = rnd.gauss(SENSOR_STATIC_POWER_MEAN, SENSOR_STATIC_POWER_STD_DEVIATION)
        cu = rnd.gauss(SENSOR_CU_POWER_MEAN, SENSOR_CU_STD_DEVIATION)
        sensors.append(Node(f"Sensor_{current_sensor_index}", cu=cu,
                            power_model=PowerModelNode(max_power=max_power, static_power=static_power)))
    return sensors


def create_microprocessors(sensors):
    microprocessors = []
    for current_sensor_index, sensor in enumerate(sensors):
        max_power = rnd.gauss(MICROPROCESSORS_MAX_POWER_MEAN, MICROPROCESSORS_MAX_POWER_STD_DEVIATION)
        static_power = rnd.gauss(MICROPROCESSORS_STATIC_POWER_MEAN, MICROPROCESSORS_STATIC_POWER_STD_DEVIATION)
        cu = rnd.gauss(MICROPROCESSORS_CU_POWER_MEAN, MICROPROCESSORS_CU_STD_DEVIATION)
        microprocessors.append(Node(f"Microprocessor_{current_sensor_index}", cu=cu,
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
        app1_processing_task = ProcessingTask(cu=50)
        app1_sink_task = SinkTask(cu=150, bound_node=server)

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
        INFO	- SourceTask(id=0, cu=0.135) on Node('Sensor_0', cu=0/10.40723309678577).
        INFO	- ProcessingTask(id=1, cu=50) on Node('Microprocessor_45', cu=0/413.4351017695709).
        INFO	- SinkTask(id=2, cu=150) on Node('Server', cu=0/inf).
        INFO	- DataFlow(bit_rate=1000) on [Link('Sensor_0' -> 'Microprocessor_45', bandwidth=0/55698945.73270142)].
        INFO	- DataFlow(bit_rate=300) on [Link('Microprocessor_45' -> 'Server', bandwidth=0/29893092.583964024)].
        INFO	Placing Application(tasks=3):
        ...

        DEBUG	598: infrastructure_meter: PowerMeasurement(dynamic=195.51W, static=380.32W)
        DEBUG	599: infrastructure_meter: PowerMeasurement(dynamic=195.51W, static=380.32W)
        INFO	Total infrastructure power usage: 302325.10891564295 Ws
        INFO	Total carbon emitted: 501.64921496653466 gCo2
    """
    env = simpy.Environment()  # creating SimPy simulation environment
    infrastructure = Infrastructure()

    # Initializing infrastructure and workload
    sensors = create_sensors()
    microprocessors = create_microprocessors(sensors)
    server = Node("Server", power_model=PowerModelNode(power_per_cu=SERVER_POWER_PER_CU,
                                                       static_power=SERVER_STATIC_POWER))  # sink

    links_from_sensors = create_links_from_sensors(sensors, microprocessors)
    links_to_server = create_links_to_server(microprocessors, server)
    for link in links_from_sensors + links_to_server:
        infrastructure.add_link(link)
    entities = sensors + microprocessors + links_from_sensors + links_to_server

    power_domain = PowerDomain(env, name="Power Domain 1",
                               start_time_str="10:00:00", update_interval=1)
    grid_power = GridPower(env, power_domain=power_domain, priority=5,
                           powered_infrastructure=[server] + links_to_server, static=True)
    battery_power = BatteryPower(env, power_domain=power_domain, priority=0, total_power_available=15, charge_rate=15,
                                 powered_infrastructure=sensors + microprocessors + links_from_sensors, static=True)
    power_domain.add_power_source(battery_power)
    power_domain.add_power_source(grid_power)

    applications = create_applications(sensors, server)

    orchestrator = CustomOrchestrator(infrastructure, power_domain)
    for application in applications:
        orchestrator.place(application)

    event_domain = EventDomain(env, update_interval=1, start_time_str="10:00:00")
    event_domain.add_event(
        Event(event=battery_power.recharge_battery, args=[grid_power], time_str="10:30:00", repeat=True,
              repeat_counter=240))

    infrastructure_pm = PowerMeter(infrastructure.nodes(), name="infrastructure_meter", measurement_interval=1)

    # Run simulation
    env.process(event_domain.run())
    env.process(power_domain.run(env))

    env.process(infrastructure_pm.run(env))

    env.run(until=600)  # run the simulation for 10 hours

    logger.info(f"Total infrastructure power usage: {float(PowerMeasurement.sum(infrastructure_pm.measurements))} Ws")
    logger.info(f"Total carbon emitted: {power_domain.return_total_carbon_emissions()} gCo2")

    file_handler = FileHandler()
    filename = "Results.Json"
    file_handler.write_out_results(filename=filename, power_domain=power_domain)

    figure_plotter = FigurePlotter(power_domain, event_domain, show_event_lines=True)
    fig1 = figure_plotter.subplot_events(event_domain.event_history,
                                         title="(6.1) Time Series of Events.")
    fig2 = figure_plotter.subplot_time_series_entities("Power Used",
                                                       entities=entities,
                                                       axis_label="Energy Consumed (Wh)",
                                                       title="(6.2) Time Series of Energy Consumed for Infrastructure.")
    fig3 = figure_plotter.subplot_time_series_power_sources("Power Used",
                                                            power_sources=[grid_power, battery_power],
                                                            axis_label="Energy Consumed (Wh)",
                                                            title="(6.3) Time Series of Energy Provided by Power Sources.")
    fig4 = figure_plotter.subplot_time_series_entities("Carbon Released",
                                                       entities=entities,
                                                       axis_label="Carbon Released (gC02eq/kWh)",
                                                       title="(6.4) Time Series of Carbon Released for Infrastructure.")
    fig5 = figure_plotter.subplot_time_series_power_sources("Carbon Released",
                                                            power_sources=[grid_power, battery_power],
                                                            axis_label="Carbon Released (gC02eq/kWh)",
                                                            title="(6.5) Time Series of Carbon Released for Power Sources.")
    fig6 = figure_plotter.subplot_time_series_power_sources("Power Available",
                                                            power_sources=[grid_power, battery_power],
                                                            axis_label="Energy Available (Wh)",
                                                            title="(6.6) Time Series of Energy Available for Battery Power.")

    figs = [fig1, fig2, fig3, fig4, fig5, fig6]
    for i, fig in enumerate(figs):
        main_fig = FigurePlotter.aggregate_subplots([fig], title="")
        file_handler.write_figure_to_file(main_fig, 1, filename=f"example_6-{i}")

    main_fig = FigurePlotter.aggregate_subplots(figs,title="Results for Example 6.")
    file_handler.write_figure_to_file(figure=main_fig, number_of_figs=len(figs))
    main_fig.show()
    main_fig = FigurePlotter.aggregate_subplots([fig2,fig6], title="Results for Example 6.")
    file_handler.write_figure_to_file(figure=main_fig, number_of_figs=2,filename="example_6_cutoff")

class CustomOrchestrator(Orchestrator):
    def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
        source_node = application.tasks(type_filter=SourceTask)[0].node
        dest_node = self.infrastructure.node("Server")
        paths = list(nx.all_simple_paths(self.infrastructure.graph, source=source_node.name, target=dest_node.name))

        return self.infrastructure.node(paths[0][1])


if __name__ == '__main__':
    main()
