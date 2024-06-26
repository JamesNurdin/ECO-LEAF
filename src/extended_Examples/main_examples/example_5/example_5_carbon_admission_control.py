import logging

import networkx as nx
import numpy as np
import simpy

from src.extendedLeaf.animate import Animation, AllowCertainDebugFilter
from src.extendedLeaf.application import Application, SourceTask, ProcessingTask, SinkTask
from src.extendedLeaf.events import EventDomain, Event
from src.extendedLeaf.file_handler import FileHandler, FigurePlotter
from src.extendedLeaf.infrastructure import Node, Link, Infrastructure
from src.extendedLeaf.orchestrator import Orchestrator
from src.extendedLeaf.power import PowerModelNode, PowerMeasurement, PowerMeter, PowerModelLink, SolarPower, \
    GridPower, PowerDomain, BatteryPower, PoweredInfrastructureDistributor
from src.extended_Examples.main_examples.example_5.settings import *

handler = logging.StreamHandler()
handler.addFilter(AllowCertainDebugFilter())
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s', handlers=[handler])


def create_application_type_1(sensor, server):
    applications = []
    for i in range(NO_TYPE1_APPLICATIONS):
        app1_source_task = SourceTask(cu=int(0.4 * sensor.power_model.max_power), bound_node=sensor)
        app1_processing_task = ProcessingTask(cu=50)
        app1_sink_task = SinkTask(cu=150, bound_node=server)
        application = Application(name=f"{i}_Application_Type_1")
        application.add_task(app1_source_task)
        application.add_task(app1_processing_task, incoming_data_flows=[(app1_source_task, 1000)])
        application.add_task(app1_sink_task, incoming_data_flows=[(app1_processing_task, 300)])

        applications.append(application)
    return applications


def create_application_type_2(sensor, server):
    applications = []
    for i in range(NO_TYPE2_APPLICATIONS):
        app1_source_task = SourceTask(cu=int(0.4 * sensor.power_model.max_power), bound_node=sensor)
        app1_processing_task_1 = ProcessingTask(cu=50)
        app1_processing_task_2 = ProcessingTask(cu=50)
        app1_sink_task = SinkTask(cu=100, bound_node=server)

        application = Application(name=f"{i}_Application_Type_2")

        application.add_task(app1_source_task)
        application.add_task(app1_processing_task_1, incoming_data_flows=[(app1_source_task, 750)])
        application.add_task(app1_processing_task_2, incoming_data_flows=[(app1_processing_task_1, 1000)])
        application.add_task(app1_sink_task, incoming_data_flows=[(app1_processing_task_2, 300)])

        applications.append(application)
    return applications


def main():
    """
    Log Output:
        DEBUG	0: infrastructure_meter: PowerMeasurement(dynamic=0.00W, static=34.41W)
        DEBUG	0: application_1_meter: PowerMeasurement(dynamic=0.00W, static=0.00W)
        DEBUG	0: application_2_meter: PowerMeasurement(dynamic=0.00W, static=0.00W)
        DEBUG	1: infrastructure_meter: PowerMeasurement(dynamic=0.00W, static=34.41W)
        DEBUG	1: application_1_meter: PowerMeasurement(dynamic=0.00W, static=0.00W)
        DEBUG	1: application_2_meter: PowerMeasurement(dynamic=0.00W, static=0.00W)
        ...
        DEBUG	599: infrastructure_meter: PowerMeasurement(dynamic=0.00W, static=29.61W)
        DEBUG	599: application_1_meter: PowerMeasurement(dynamic=0.00W, static=0.00W)
        DEBUG	599: application_2_meter: PowerMeasurement(dynamic=0.00W, static=0.00W)
        INFO	Total infrastructure power usage: 20296.043750000008 Ws
        INFO	Total carbon emitted: 56.33289374999988 gCo2
         """
    env = simpy.Environment()  # creating SimPy simulation environment
    infrastructure = Infrastructure()

    # Initializing infrastructure and workload
    # Source task node
    sensor = Node("Sensor", cu=10, power_model=PowerModelNode(max_power=0.15, static_power=0.007))

    # Processing task nodes
    solar_microprocessor = Node("SolarMicroprocessor", cu=400,
                                power_model=PowerModelNode(max_power=6.25, static_power=4.8))
    battery_microprocessor = Node("BatteryMicroprocessor", cu=400,
                                  power_model=PowerModelNode(max_power=6.25, static_power=4.8))
    grid_microprocessor = Node("GridMicroprocessor", cu=400,
                               power_model=PowerModelNode(max_power=6.25, static_power=4.8))

    # Sink task node
    server = Node("Server", power_model=PowerModelNode(power_per_cu=20e-3, static_power=20))
    infrastructure.add_node(sensor)
    infrastructure.add_node(solar_microprocessor)
    infrastructure.add_node(battery_microprocessor)
    infrastructure.add_node(grid_microprocessor)

    # Links

    # Path 1
    grid_wired_link_from_source = Link(name="GridWiredLink", src=sensor, dst=grid_microprocessor, latency=0,
                                       bandwidth=50e6, power_model=PowerModelLink(0))
    grid_wifi_link_to_server = Link(name="GridWirelessLink", src=grid_microprocessor, dst=server, latency=10,
                                    bandwidth=30e6, power_model=PowerModelLink(0))
    # Path2
    bat_wired_link_from_source = Link(name="BatteryWiredLink", src=sensor, dst=battery_microprocessor, latency=0,
                                      bandwidth=50e6, power_model=PowerModelLink(0))
    bat_wifi_link_to_grid = Link(name="BatteryWirelessLink", src=battery_microprocessor, dst=grid_microprocessor, latency=10,
                                 bandwidth=30e6, power_model=PowerModelLink(0))
    # Path 3
    solar_wired_link_from_source = Link(name="SolarWiredLink", src=sensor, dst=solar_microprocessor, latency=0,
                                        bandwidth=50e6, power_model=PowerModelLink(0))
    solar_wifi_link_to_server = Link(name="SolarWirelessLink", src=solar_microprocessor, dst=server, latency=10,
                                     bandwidth=30e6, power_model=PowerModelLink(0))
    infrastructure.add_link(grid_wired_link_from_source)
    infrastructure.add_link(grid_wifi_link_to_server)
    infrastructure.add_link(bat_wired_link_from_source)
    infrastructure.add_link(bat_wifi_link_to_grid)
    infrastructure.add_link(solar_wired_link_from_source)
    infrastructure.add_link(solar_wifi_link_to_server)

    entities = infrastructure.nodes() + infrastructure.links()

    power_domain = PowerDomain(env, name="Power Domain 1", start_time_str="14:00:00", update_interval=1)
    solar_power = SolarPower(env, power_domain=power_domain, priority=1,
                             powered_infrastructure=[solar_microprocessor, solar_wired_link_from_source,
                                                     solar_wifi_link_to_server], static=True)
    grid_power = GridPower(env, power_domain=power_domain, priority=5,
                           powered_infrastructure=[grid_microprocessor, grid_wired_link_from_source,
                                                   grid_wifi_link_to_server, server], static=True)
    battery_power = BatteryPower(env, power_domain=power_domain, priority=0, total_power_available=30, charge_rate=30,
                                 powered_infrastructure=[sensor, battery_microprocessor, bat_wired_link_from_source,
                                                         bat_wifi_link_to_grid], static=True)
    power_domain.add_power_source(battery_power)
    power_domain.add_power_source(grid_power)

    type_1_applications = create_application_type_1(sensor, server)
    type_2_applications = create_application_type_2(sensor, server)

    # Place over Infrastructure
    orchestrator = ExampleOrchestrator(infrastructure, power_domain)
    # orchestrator.place(application2)

    event_domain = EventDomain(env, update_interval=1, start_time_str="14:00:00")

    event_domain.add_event(
        Event(event=battery_power.recharge_battery, args=[grid_power], time_str="14:00:00", repeat=False))
    event_domain.add_event(
        Event(event=orchestrator.place_applications, args=[type_1_applications], time_str="14:10:00", repeat=True))
    event_domain.add_event(
        Event(event=orchestrator.place_applications, args=[type_2_applications], time_str="14:10:00", repeat=True))
    event_domain.add_event(
        Event(event=orchestrator.deallocate_applications, args=[type_1_applications], time_str="14:20:00", repeat=True))
    event_domain.add_event(
        Event(event=orchestrator.deallocate_applications, args=[type_2_applications], time_str="14:20:00", repeat=True))
    event_domain.add_event(
        Event(event=power_domain.add_power_source, args=[solar_power], time_str="16:00:00", repeat=False))

    infrastructure_pm = PowerMeter(infrastructure.nodes(), name="infrastructure_meter", measurement_interval=1)
    application1_pm = PowerMeter(type_1_applications[0], name="application_1_meter")
    application2_pm = PowerMeter(type_2_applications[0], name="application_2_meter")

    # Run simulation
    env.process(event_domain.run())
    env.process(power_domain.run(env))

    env.process(infrastructure_pm.run(env))
    env.process(application1_pm.run(env))
    env.process(application2_pm.run(env))

    env.run(until=600)  # run the simulation for 10 hours (until the battery is fully drained)

    logger.info(f"Total infrastructure power usage: {float(PowerMeasurement.sum(infrastructure_pm.measurements))} Ws")
    logger.info(f"Total carbon emitted: {power_domain.return_total_carbon_emissions()} gCo2")

    file_handler = FileHandler()
    filename = "Results.Json"
    file_handler.write_out_results(filename=filename, power_domain=power_domain)

    figure_plotter = FigurePlotter(power_domain, event_domain, show_event_lines=True)
    fig1 = figure_plotter.subplot_events(event_domain.event_history,
                                         title="(5.1) Time Series of Events.")
    fig2 = figure_plotter.subplot_time_series_entities("Power Used",
                                                       entities=entities,
                                                       axis_label="Energy Consumed (Wh)",
                                                       title="(5.2) Time Series of Energy Consumed for Infrastructure.")
    fig3 = figure_plotter.subplot_time_series_power_sources("Power Used",
                                                            power_sources=[solar_power, grid_power, battery_power],
                                                            axis_label="Energy Consumed (Wh)",
                                                            title="(5.2) Time Series of Energy Provided by Power Sources.")
    fig4 = figure_plotter.subplot_time_series_entities("Carbon Released",
                                                       entities=entities,
                                                       axis_label="Carbon Released (gC02eq)",
                                                       title="(5.3) Time Series of Carbon Released for Infrastructure.")
    fig5 = figure_plotter.subplot_time_series_power_sources("Carbon Released",
                                                            power_sources=[solar_power, grid_power, battery_power],
                                                            axis_label="Carbon Released (gC02eq)",
                                                            title="(5.4) Time Series of Carbon Released for Power Sources.")
    fig7 = figure_plotter.subplot_time_series_entities("Power Used",
                                                         entities=[solar_microprocessor],
                                                         axis_label="Energy Consumed (Wh)",
                                                         title_attribute="Energy Consumed",
                                                         title="(5.6) Time Series of Energy Consumed by the Solar Microprocessor.")
    fig8 = figure_plotter.subplot_time_series_entities("Power Used",
                                                         entities=[grid_microprocessor],
                                                         axis_label="Energy Consumed (Wh)",
                                                         title_attribute="Energy Consumed",
                                                         title="(5.7) Time Series of Energy Consumed by the Grid Microprocessor.")

    figs = [fig1, fig2, fig3, fig4, fig5]
    main_fig = FigurePlotter.aggregate_subplots(figs,title="Results for Example 5.")
    file_handler.write_figure_to_file(figure=main_fig, number_of_figs=len(figs))
    main_fig.show()
    for i, fig in enumerate(figs):
        main_fig = FigurePlotter.aggregate_subplots([fig], title="")
        file_handler.write_figure_to_file(main_fig, 1, filename=f"example_5-{i}")

    figs = [fig7, fig8]
    main_fig = FigurePlotter.aggregate_subplots(figs, title="Results for Example 5.")
    file_handler.write_figure_to_file(figure=main_fig, number_of_figs=len(figs), filename="Power provided")

    animation = Animation(power_domains=[power_domain], env=env, speed_sec=2.5)
    animation.run_animation()


class ExampleOrchestrator(Orchestrator):

    def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
        dest_node = self.infrastructure.node("Server")
        source_node = self.infrastructure.node("Sensor")
        paths = list(nx.all_simple_paths(self.infrastructure.graph, source=source_node.name, target=dest_node.name))
        # iterate through all the potential nodes
        current_best_carbon_intensity = np.inf
        return_node = None
        # check if a path
        for path in paths:
            for i, node in enumerate(path):
                node = self.infrastructure.node(node)
                remaining_path = path[i:]
                starting_path = path[:i]
                if len(application.get_application_paths(processing_task)[0]) == len(remaining_path):
                    if len(starting_path + remaining_path) == len(application.tasks()):
                        if node.paused is False:
                            power_source = node.power_model.power_source
                            if power_source in self.power_domain.power_sources:
                                carbon_intensity = power_source.get_current_carbon_intensity(0)
                                if carbon_intensity < current_best_carbon_intensity:
                                    return_node = node
                                    current_best_carbon_intensity = carbon_intensity
        return return_node

    def place_applications(self, applications):
        for application in applications:
            self.place(application)

    def deallocate_applications(self, applications):
        for application in applications:
            application.deallocate()


if __name__ == '__main__':
    main()
