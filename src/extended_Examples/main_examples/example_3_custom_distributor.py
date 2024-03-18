import logging

import numpy as np
import simpy

from src.extendedLeaf.animate import AllowCertainDebugFilter, Animation
from src.extendedLeaf.application import Application, SourceTask, ProcessingTask, SinkTask
from src.extendedLeaf.file_handler import FileHandler, FigurePlotter
from src.extendedLeaf.infrastructure import Node, Link, Infrastructure
from src.extendedLeaf.orchestrator import Orchestrator
from src.extendedLeaf.power import PowerModelNode, PowerMeasurement, PowerMeter, PowerModelLink, SolarPower, WindPower, \
    GridPower, PowerDomain, PowerSource, PoweredInfrastructureDistributor

handler = logging.StreamHandler()
handler.addFilter(AllowCertainDebugFilter())
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s',handlers=[handler])


def main():
    """
    Log Output:
        INFO	Placing Application(tasks=3):
        INFO	- SourceTask(id=0, cu=9) on Node('sensor', cu=0/10).
        INFO	- ProcessingTask(id=1, cu=5) on Node('server', cu=0/inf).
        INFO	- SinkTask(id=2, cu=10) on Node('server', cu=5/inf).
        INFO	- DataFlow(bit_rate=100) on [Link('sensor' -> 'microprocessor', bandwidth=0/50000000.0), Link('microprocessor' -> 'server', bandwidth=0/30000000.0, latency=10)].
        INFO	- DataFlow(bit_rate=500) on [].
        DEBUG	0: application_meter: PowerMeasurement(dynamic=0.43W, static=20.01W)
        DEBUG	0: infrastructure_meter: PowerMeasurement(dynamic=0.43W, static=24.81W)
        DEBUG	1: application_meter: PowerMeasurement(dynamic=0.43W, static=20.01W)
        DEBUG	1: infrastructure_meter: PowerMeasurement(dynamic=0.43W, static=24.81W)
        ...
        DEBUG	118: application_meter: PowerMeasurement(dynamic=0.43W, static=20.01W)
        DEBUG	118: infrastructure_meter: PowerMeasurement(dynamic=0.43W, static=24.81W)
        DEBUG	119: application_meter: PowerMeasurement(dynamic=0.43W, static=20.01W)
        DEBUG	119: infrastructure_meter: PowerMeasurement(dynamic=0.43W, static=24.81W)
        DEBUG	120: application_meter: PowerMeasurement(dynamic=0.43W, static=20.01W)
        DEBUG	120: infrastructure_meter: PowerMeasurement(dynamic=0.43W, static=24.81W)
        NFO	Total application power usage: 1226.1443999999992 Ws
        INFO	Total infrastructure power usage: 1514.1420000000007 Ws
        INFO	Total carbon emitted: 4.538085299999998 gCo2
        """
    env = simpy.Environment()
    infrastructure = Infrastructure()
    # Source task node
    sensor = Node("Sensor", cu=10, power_model=PowerModelNode(max_power=0.5, static_power=0.007))
    # Processing task node
    microprocessor = Node("Microprocessor", cu=400, power_model=PowerModelNode(max_power=6.25, static_power=4.8))
    # Sink task node
    server = Node("Server", power_model=PowerModelNode(power_per_cu=20e-3, static_power=20))

    # #two Wi-Fi links between (Wired WAN) Source -> Microprocessor and (Wireless WIFI) Microprocessor -> Server
    wired_link_from_source = Link(name="Link1", src=sensor, dst=microprocessor, latency=0, bandwidth=50e6,
                                  power_model=PowerModelLink(0))
    wifi_link_to_server = Link(name="Link2", src=microprocessor, dst=server, latency=10, bandwidth=30e6,
                               power_model=PowerModelLink(400e-9))
    infrastructure.add_link(wifi_link_to_server)
    infrastructure.add_link(wired_link_from_source)
    entities = infrastructure.nodes() + infrastructure.links()

    power_domain = PowerDomain(env, name="Power Domain 1", powered_infrastructure=entities,
                               start_time_str="19:00:00", update_interval=1, powered_infrastructure_distributor=
                               PoweredInfrastructureDistributor(custom_distribution_method))
    grid = GridPower(env, power_domain=power_domain, priority=5)
    solar_power = SolarPower(env, power_domain=power_domain, priority=0)
    wind_power = WindPower(env, power_domain=power_domain, priority=1)
    power_domain.add_power_source(solar_power)
    power_domain.add_power_source(wind_power)
    power_domain.add_power_source(grid)

    # Initialise three tasks
    source_task = SourceTask(cu=9, bound_node=sensor)
    processing_task = ProcessingTask(cu=50)
    sink_task = SinkTask(cu=150, bound_node=server)

    # Build Application
    application = Application()
    application.add_task(source_task)
    application.add_task(processing_task, incoming_data_flows=[(source_task, 100)])
    application.add_task(sink_task, incoming_data_flows=[(processing_task, 500)])

    # Place over Infrastructure
    orchestrator = SimpleOrchestrator(infrastructure, power_domain)
    orchestrator.place(application)

    # Early power meters when exploring isolated power measurements
    application_pm = PowerMeter(application, name="application_meter")
    infrastructure_pm = PowerMeter(infrastructure.nodes(), name="infrastructure_meter", measurement_interval=1)

    # Run simulation
    env.process(power_domain.run(env))
    env.process(application_pm.run(env))
    env.process(infrastructure_pm.run(env))
    env.run(until=61)  # run simulation until 20:00:00

    logger.info(f"Total application power usage: {float(PowerMeasurement.sum(application_pm.measurements))} Ws")
    logger.info(f"Total infrastructure power usage: {float(PowerMeasurement.sum(infrastructure_pm.measurements))} Ws")
    logger.info(f"Total carbon emitted: {power_domain.return_total_carbon_emissions()} gCo2")

    file_handler = FileHandler()
    filename = "Results.Json"
    file_handler.write_out_results(filename=filename, power_domain=power_domain)

    figure_plotter = FigurePlotter(power_domain)
    fig1 = figure_plotter.subplot_time_series_entities("Power Used",
                                                       entities=entities,
                                                       axis_label="Energy Consumed (Wh)",
                                                       title="(3.1) Time Series of Energy Consumed for Infrastructure.")
    fig2 = figure_plotter.subplot_time_series_power_sources("Power Used",
                                                            power_sources=[solar_power,grid, wind_power],
                                                            axis_label="Energy Consumed (Wh)",
                                                            title="(3.2) Time Series of Energy Provided by Power Sources.")
    fig3 = figure_plotter.subplot_time_series_entities("Carbon Released",
                                                       entities=entities,
                                                       axis_label="Carbon Released (gC02eq/kWh)",
                                                       title="(3.3) Time Series of Carbon Released for Infrastructure.")
    fig4 = figure_plotter.subplot_time_series_power_sources("Carbon Released",
                                                            power_sources=[solar_power, grid, wind_power],
                                                            axis_label="Carbon Released (gC02eq/kWh)",
                                                            title="(3.4) Time Series of Carbon Released for Power Sources.")
    fig5 = figure_plotter.subplot_time_series_power_sources("Power Available",
                                                            power_sources=[solar_power, wind_power],
                                                            axis_label="Energy Available (Wh)",
                                                            title="(3.5) Time Series of Energy Available for Power Sources.")

    figs = [fig1, fig2, fig3, fig4, fig5]
    main_fig = figure_plotter.aggregate_subplots(figs,title="Results for Example 3.")
    file_handler.write_figure_to_file(figure=main_fig, number_of_figs=len(figs))
    main_fig.show()
    for i, fig in enumerate(figs):
        main_fig = FigurePlotter.aggregate_subplots([fig], title="")
        file_handler.write_figure_to_file(main_fig, 1, filename=f"example_3-{i}")

    animation = Animation(power_domains=[power_domain], env=env, speed_sec=2.5)
    animation.run_animation()


def custom_distribution_method(current_power_source: PowerSource, power_domain):
    for entity in power_domain.powered_infrastructure:
        if entity.power_model.power_source == current_power_source:
            current_entity_power_requirement = float(entity.power_model.update_sensitive_measure(
                power_domain.update_interval))
            if current_power_source.get_current_power() < current_entity_power_requirement:
                current_power_source.remove_entity(entity)
            else:
                current_power_source.consume_power(current_entity_power_requirement)

    """Check if any unpowered infrastructure is able to be powered"""
    for entity in power_domain.powered_infrastructure:
        if entity.power_model.power_source is None:
            current_entity_power_requirement = float(entity.power_model.update_sensitive_measure(
                power_domain.update_interval))
            if current_entity_power_requirement < current_power_source.get_current_power():
                if isinstance(entity.power_model, PowerModelNode) and entity.power_model.max_power is None:
                    if current_power_source.remaining_power == np.inf:
                        current_power_source.add_entity(entity)
                        current_power_source.consume_power(current_entity_power_requirement)
                        continue  # Skip the rest of the loop for this entity
                    else:
                        continue  # Skip the rest of the loop for this entity

                # If not an infinite power source or not a node with unlimited power, continue here
                current_power_source.add_entity(entity)
                current_power_source.consume_power(current_entity_power_requirement)

    """Check if any entities in lower priority power sources can move up if excess energy is available"""
    for entity in power_domain.powered_infrastructure:
        if entity.power_model.power_source is not None \
                and entity.power_model.power_source.priority > current_power_source.priority:
            current_entity_power_requirement = float(entity.power_model.update_sensitive_measure(
                power_domain.update_interval))

            if current_entity_power_requirement < current_power_source.get_current_power():
                if isinstance(entity.power_model, PowerModelNode) and entity.power_model.max_power is None:
                    if current_power_source.remaining_power == np.inf:
                        entity.power_model.power_source.remove_entity(entity)
                        current_power_source.add_entity(entity)
                        current_power_source.consume_power(current_entity_power_requirement)
                        continue  # Skip the rest of the loop for this entity
                    else:
                        continue  # Skip the rest of the loop for this entity

                # If not an infinite power source or not a node with unlimited power, continue here
                entity.power_model.power_source.remove_entity(entity)
                current_power_source.add_entity(entity)
                current_power_source.consume_power(current_entity_power_requirement)


class SimpleOrchestrator(Orchestrator):
    def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
        return self.infrastructure.node("Server")

if __name__ == '__main__':
    main()
