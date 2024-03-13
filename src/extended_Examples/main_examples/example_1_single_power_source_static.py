import logging
import simpy

from src.extendedLeaf.animate import Animation
from src.extendedLeaf.application import Task, Application, SourceTask, ProcessingTask, SinkTask
from src.extendedLeaf.file_handler import FileHandler, FigurePlotter
from src.extendedLeaf.infrastructure import Node, Link, Infrastructure
from src.extendedLeaf.orchestrator import Orchestrator
from src.extendedLeaf.power import PowerModelNode, PowerMeasurement, PowerMeter, PowerModelLink, SolarPower, \
    GridPower, PowerDomain, PoweredInfrastructureDistributor

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')


def main():
    """
    Log Output:
        INFO	Placing Application(tasks=3):
        INFO	- SourceTask(id=0, cu=9) on Node('sensor', cu=0/10).
        INFO	- ProcessingTask(id=1, cu=5) on Node('microprocessor', cu=0/40).
        INFO	- SinkTask(id=2, cu=10) on Node('node3', cu=0/inf).
        INFO	- DataFlow(bit_rate=100) on [Link('sensor' -> 'microprocessor', bandwidth=0/50000000.0)].
        INFO	- DataFlow(bit_rate=500) on [Link('microprocessor' -> 'node3', bandwidth=0/30000000.0, latency=10)].
        DEBUG	0: application_meter: PowerMeasurement(dynamic=0.51W, static=24.81W)
        DEBUG	0: infrastructure_meter: PowerMeasurement(dynamic=0.51W, static=24.81W)
        DEBUG	1: application_meter: PowerMeasurement(dynamic=0.51W, static=24.81W)
        DEBUG	1: infrastructure_meter: PowerMeasurement(dynamic=0.51W, static=24.81W)
        DEBUG	2: application_meter: PowerMeasurement(dynamic=0.51W, static=24.81W)
        DEBUG	2: infrastructure_meter: PowerMeasurement(dynamic=0.51W, static=24.81W)
        DEBUG	3: application_meter: PowerMeasurement(dynamic=0.51W, static=24.81W)
        DEBUG	3: infrastructure_meter: PowerMeasurement(dynamic=0.51W, static=24.81W)
        DEBUG	4: application_meter: PowerMeasurement(dynamic=0.51W, static=24.81W)
        DEBUG	4: infrastructure_meter: PowerMeasurement(dynamic=0.51W, static=24.81W)
        DEBUG	5: application_meter: PowerMeasurement(dynamic=0.51W, static=24.81W)
        DEBUG	5: infrastructure_meter: PowerMeasurement(dynamic=0.51W, static=24.81W)
        DEBUG	6: application_meter: PowerMeasurement(dynamic=0.51W, static=24.81W)
        DEBUG	6: infrastructure_meter: PowerMeasurement(dynamic=0.51W, static=24.81W)
        DEBUG	7: application_meter: PowerMeasurement(dynamic=0.51W, static=24.81W)
        DEBUG	7: infrastructure_meter: PowerMeasurement(dynamic=0.51W, static=24.81W)
        DEBUG	8: application_meter: PowerMeasurement(dynamic=0.51W, static=24.81W)
        DEBUG	8: infrastructure_meter: PowerMeasurement(dynamic=0.51W, static=24.81W)
        DEBUG	9: application_meter: PowerMeasurement(dynamic=0.51W, static=24.81W)
        DEBUG	9: infrastructure_meter: PowerMeasurement(dynamic=0.51W, static=24.81W)
        INFO	Total application power usage: 253.17149999999992 Ws
        INFO	Total infrastructure power usage: 253.16950000000006 Ws
        INFO	Total carbon emitted: 0.9071978749999999 gCo2
    """
    env = simpy.Environment()
    infrastructure = Infrastructure()
    # Source task node
    sensor = Node("sensor", cu=10, power_model=PowerModelNode(max_power=0.15, static_power=0.007))
    # Processing task node
    microprocessor = Node("microprocessor", cu=40, power_model=PowerModelNode(max_power=6.25, static_power=4.8))
    # Sink task node
    server = Node("node3", power_model=PowerModelNode(power_per_cu=20e-3, static_power=20))

    # #two Wi-Fi links between (Wired WAN) Source -> Microprocessor and (Wireless WIFI) Microprocessor -> Server
    wired_link_from_source = Link(name="Link1", src=sensor, dst=microprocessor, latency=0, bandwidth=50e6,
                                  power_model=PowerModelLink(0))
    wifi_link_to_server = Link(name="Link2", src=microprocessor, dst=server, latency=10, bandwidth=30e6,
                               power_model=PowerModelLink(400e-9))
    infrastructure.add_link(wifi_link_to_server)
    infrastructure.add_link(wired_link_from_source)
    entities = infrastructure.nodes()+infrastructure.links()

    power_domain = PowerDomain(env, name="Power Domain 1",
                               powered_infrastructure_distributor=PoweredInfrastructureDistributor(),
                               start_time_str="19:00:00", update_interval=1)
    grid = GridPower(env, power_domain=power_domain, priority=5, powered_infrastructure=entities, static=True)
    power_domain.add_power_source(grid)

    # Initialise three tasks
    source_task = SourceTask(cu=9, bound_node=sensor)
    processing_task = ProcessingTask(cu=5)
    sink_task = SinkTask(cu=10, bound_node=server)

    # Build Application
    application = Application()
    application.add_task(source_task)
    application.add_task(processing_task, incoming_data_flows=[(source_task, 100)])
    application.add_task(sink_task, incoming_data_flows=[(processing_task, 500)])

    # Place over Infrastructure
    orchestrator = ExampleOrchestrator(infrastructure, power_domain)
    orchestrator.place(application)

    # Early power meters when exploring isolated power measurements
    application_pm = PowerMeter(application, name="application_meter")
    infrastructure_pm = PowerMeter(infrastructure.nodes(), name="infrastructure_meter", measurement_interval=1)

    # Run simulation
    env.process(power_domain.run(env))
    env.process(application_pm.run(env))
    env.process(infrastructure_pm.run(env))
    env.run(until=12)  # run simulation for 10 minutes

    logger.info(f"Total application power usage: {float(PowerMeasurement.sum(application_pm.measurements))} Ws")
    logger.info(f"Total infrastructure power usage: {float(PowerMeasurement.sum(infrastructure_pm.measurements))} Ws")
    logger.info(f"Total carbon emitted: {power_domain.return_total_carbon_emissions()} gCo2")

    file_handler = FileHandler()
    filename = "Results.Json"
    file_handler.write_out_results(filename=filename, power_domain=power_domain)

    figure_plotter = FigurePlotter(power_domain)
    fig1 = figure_plotter.subplot_time_series_entities("Carbon Released",
                                                       entities=entities,
                                                       axis_label="Carbon Released (gC02eq/kWh)",
                                                       title_attribute="Carbon Released")
    fig2 = figure_plotter.subplot_time_series_entities("Power Used",
                                                       entities=entities,
                                                       axis_label="Energy Consumed (Wh)",
                                                       title_attribute="Energy Consumed")
    fig3 = figure_plotter.subplot_time_series_power_sources("Power Used",
                                                            power_sources=[grid],
                                                            axis_label="Energy Consumed (Wh)",
                                                            title_attribute="Energy Consumed")
    fig4 = figure_plotter.subplot_time_series_power_sources("Carbon Released",
                                                            power_sources=[grid],
                                                            axis_label="Carbon Released (gC02eq/kWh)",
                                                            title_attribute="Carbon Released")

    figs = [fig1, fig2, fig3, fig4]
    main_fig = figure_plotter.aggregate_subplots(figs,title="Results for Example 1.")
    file_handler.write_figure_to_file(figure=main_fig, number_of_figs=len(figs))
    for i, fig in enumerate(figs):
        main_fig = FigurePlotter.aggregate_subplots([fig], title="")
        file_handler.write_figure_to_file(main_fig, 1, filename=f"example_1-{i}")
    main_fig.show()


class ExampleOrchestrator(Orchestrator):
    def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
        return self.infrastructure.node("microprocessor")


if __name__ == '__main__':
    main()
