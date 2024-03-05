import logging

import networkx as nx
import numpy as np
import simpy

from src.extendedLeaf.animate import Animation, AllowCertainDebugFilter
from src.extendedLeaf.application import Application, SourceTask, ProcessingTask, SinkTask
from src.extendedLeaf.events import EventDomain, PowerDomainEvent
from src.extendedLeaf.file_handler import FileHandler, FigurePlotter
from src.extendedLeaf.infrastructure import Node, Link, Infrastructure
from src.extendedLeaf.orchestrator import Orchestrator
from src.extendedLeaf.power import PowerModelNode, PowerMeasurement, PowerMeter, PowerModelLink, SolarPower, \
    GridPower, PowerDomain, BatteryPower, PoweredInfrastructureDistributor
from src.extended_Examples.main_examples.example_5.settings import *

handler = logging.StreamHandler()
handler.addFilter(AllowCertainDebugFilter())
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s',handlers=[handler])


def create_application_type_1(sensor, server):
    applications = []
    for i in range(NO_TYPE1_APPLICATIONS):
        app1_source_task = SourceTask(cu=int(0.1*sensor.power_model.max_power), bound_node=sensor)
        app1_processing_task = ProcessingTask(cu=3)
        app1_sink_task = SinkTask(cu=12, bound_node=server)

        application = Application(name=f"{i}_Application_Type_1")

        application.add_task(app1_source_task)
        application.add_task(app1_processing_task, incoming_data_flows=[(app1_source_task, 1000)])
        application.add_task(app1_sink_task, incoming_data_flows=[(app1_processing_task, 300)])

        applications.append(application)
    return applications


def create_application_type_2(sensor, server):
    applications = []
    for i in range(NO_TYPE2_APPLICATIONS):
        app1_source_task = SourceTask(cu=int(0.1*sensor.power_model.max_power), bound_node=sensor)
        app1_processing_task_1 = ProcessingTask(cu=2)
        app1_processing_task_2 = ProcessingTask(cu=3)
        app1_sink_task = SinkTask(cu=12, bound_node=server)

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
        DEBUG	0: infrastructure_meter: PowerMeasurement(dynamic=0.00W, static=29.60W)
        DEBUG	0: application_1_meter: PowerMeasurement(dynamic=0.00W, static=0.00W)
        DEBUG	0: application_2_meter: PowerMeasurement(dynamic=0.00W, static=0.00W)
        DEBUG	1: infrastructure_meter: PowerMeasurement(dynamic=0.00W, static=34.41W)
        DEBUG	1: application_1_meter: PowerMeasurement(dynamic=0.00W, static=0.00W)
        DEBUG	1: application_2_meter: PowerMeasurement(dynamic=0.00W, static=0.00W)
        ...
        DEBUG	599: infrastructure_meter: PowerMeasurement(dynamic=0.00W, static=29.61W)
        DEBUG	599: application_1_meter: PowerMeasurement(dynamic=0.00W, static=0.00W)
        DEBUG	599: application_2_meter: PowerMeasurement(dynamic=0.00W, static=0.00W)
        INFO	Total infrastructure power usage: 19353.39299999997 Ws
        INFO	Total carbon emitted: 71.75519929999965 gCo2
         """
    env = simpy.Environment()  # creating SimPy simulation environment
    infrastructure = Infrastructure()

    # Initializing infrastructure and workload
    # Source task node
    sensor = Node("sensor", cu=10, power_model=PowerModelNode(max_power=0.15, static_power=0.007))

    # Processing task nodes
    solar_microprocessor = Node("solar_microprocessor", cu=40, power_model=PowerModelNode(max_power=6.25, static_power=4.8))
    battery_microprocessor = Node("bat_microprocessor", cu=40, power_model=PowerModelNode(max_power=6.25, static_power=4.8))
    grid_microprocessor = Node("grid_microprocessor", cu=40, power_model=PowerModelNode(max_power=6.25, static_power=4.8))

    # Sink task node
    server = Node("server", power_model=PowerModelNode(power_per_cu=20e-3, static_power=20))

    # Links

    # Path 1
    grid_wired_link_from_source = Link(name="grid_wired", src=sensor, dst=grid_microprocessor, latency=0,
                                       bandwidth=50e6, power_model=PowerModelLink(0))
    grid_wifi_link_to_server = Link(name="grid_wireless", src=grid_microprocessor, dst=server, latency=10,
                                    bandwidth=30e6, power_model=PowerModelLink(400e-9))
    # Path2
    bat_wired_link_from_source = Link(name="bat_wired", src=sensor, dst=battery_microprocessor, latency=0,
                                      bandwidth=50e6, power_model=PowerModelLink(0))
    bat_wifi_link_to_grid = Link(name="bat_wireless", src=battery_microprocessor, dst=grid_microprocessor, latency=10,
                                   bandwidth=30e6, power_model=PowerModelLink(400e-9))
    # Path 3
    solar_wired_link_from_source = Link(name="solar_wired", src=sensor, dst=solar_microprocessor, latency=0,
                                        bandwidth=50e6, power_model=PowerModelLink(0))
    solar_wifi_link_to_server = Link(name="solar_wireless", src=solar_microprocessor, dst=server, latency=10,
                                     bandwidth=30e6, power_model=PowerModelLink(400e-9))
    infrastructure.add_link(grid_wired_link_from_source)
    infrastructure.add_link(grid_wifi_link_to_server)
    infrastructure.add_link(bat_wired_link_from_source)
    infrastructure.add_link(bat_wifi_link_to_grid)
    infrastructure.add_link(solar_wired_link_from_source)
    infrastructure.add_link(solar_wifi_link_to_server)

    entities = infrastructure.nodes() + infrastructure.links()

    power_domain = PowerDomain(env, name="Power Domain 1", start_time_str="15:00:00", update_interval=1)
    solar_power = SolarPower(env, power_domain=power_domain, priority=1,
                             powered_infrastructure=[solar_microprocessor, solar_wired_link_from_source,
                                                     solar_wifi_link_to_server], static=True)
    grid_power = GridPower(env, power_domain=power_domain, priority=5,
                           powered_infrastructure=[grid_microprocessor, grid_wired_link_from_source,
                                                   grid_wifi_link_to_server,server], static=True)
    battery_power = BatteryPower(env, power_domain=power_domain, priority=0, total_power_available=500,
                                 powered_infrastructure=[sensor, battery_microprocessor, bat_wired_link_from_source,
                                                         bat_wifi_link_to_grid], static=True)
    power_domain.add_power_source(battery_power)
    power_domain.add_power_source(grid_power)

    type_1_applications = create_application_type_1(sensor, server)
    type_2_applications = create_application_type_2(sensor, server)

    # Place over Infrastructure
    orchestrator = ExampleOrchestrator(infrastructure, power_domain)
    # orchestrator.place(application2)

    event_domain = EventDomain(env, update_interval=1, start_time_str="15:00:00")

    event_domain.add_event(
        PowerDomainEvent(event=battery_power.recharge_battery, args=[grid_power], time_str="15:00:00", repeat=False))
    event_domain.add_event(
        PowerDomainEvent(event=orchestrator.place_applications, args=[type_1_applications], time_str="15:10:00", repeat=True))
    event_domain.add_event(
        PowerDomainEvent(event=orchestrator.place_applications, args=[type_2_applications], time_str="15:10:00", repeat=True))
    event_domain.add_event(
        PowerDomainEvent(event=orchestrator.deallocate_applications, args=[type_1_applications], time_str="15:20:00", repeat=True))
    event_domain.add_event(
        PowerDomainEvent(event=orchestrator.deallocate_applications, args=[type_2_applications], time_str="15:20:00", repeat=True))
    event_domain.add_event(
        PowerDomainEvent(event=power_domain.add_power_source, args=[solar_power], time_str="17:00:00", repeat=False))
    infrastructure_pm = PowerMeter(infrastructure.nodes(), name="infrastructure_meter", measurement_interval=1)
    application1_pm = PowerMeter(type_1_applications[0], name="application_1_meter")
    application2_pm = PowerMeter(type_2_applications[0], name="application_2_meter")


    # Run simulation
    env.process(power_domain.run(env))
    env.process(event_domain.run())

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
    event_figure = figure_plotter.subplot_events(event_domain.event_history)
    fig1 = figure_plotter.subplot_time_series_entities("Power Used", entities=entities)
    fig2 = figure_plotter.subplot_time_series_power_sources("Carbon Released", power_sources=[solar_power, battery_power, grid_power])
    fig3 = figure_plotter.subplot_time_series_power_sources("Power Available", power_sources=[battery_power])
    fig4 = figure_plotter.subplot_time_series_power_meter([application2_pm,application1_pm])
    figs = [event_figure, fig1, fig2, fig3, fig4]
    main_fig = figure_plotter.aggregate_subplots(figs)
    file_handler.write_figure_to_file(figure=main_fig, number_of_figs=len(figs))
    main_fig.show()

    animation = Animation(power_domains=[power_domain], env=env, speed_sec=2.5)
    animation.run_animation()


class ExampleOrchestrator(Orchestrator):

    def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
        dest_node = self.infrastructure.node("server")
        source_node = self.infrastructure.node("sensor")
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
                    if len(starting_path+remaining_path) == len(application.tasks()):
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
