import logging
import simpy
from src.extendedLeaf.application import Task, Application, SourceTask, ProcessingTask, SinkTask
from src.extendedLeaf.file_handler import FileHandler
from src.extendedLeaf.infrastructure import Node, Link, Infrastructure
from src.extendedLeaf.orchestrator import Orchestrator
from src.extendedLeaf.power import PowerModelNode, PowerMeasurement, PowerMeter, PowerModelLink, SolarPower, \
    GridPower, PowerDomain

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')


def main():
    """

DEBUG	119: application_meter: PowerMeasurement(dynamic=0.47W, static=20.50W)
DEBUG	119: infrastructure_meter: PowerMeasurement(dynamic=0.45W, static=20.50W)
INFO	Total application power usage: 2495.496640000002 Ws
INFO	Total infrastructure power usage: 2493.104740000002 Ws
INFO	Total carbon emitted: 1.895271535111113 gCo2
    """
    env = simpy.Environment()
    infrastructure = Infrastructure()

    # Initializing infrastructure and workload
    # Three nodes 1,2,3
    sensor = Node("node1", cu=10, power_model=PowerModelNode(max_power=0.5e-3, static_power=0.1e-3))  # source
    microprocessor = Node("node2", cu=40, power_model=PowerModelNode(max_power=2.5, static_power=0.5))  # processing task
    server = Node("node3", power_model=PowerModelNode(power_per_cu=20e-3,static_power=20))  # sink

    # #two Wi-Fi links between 1 -> 2 and 2 -> 3
    wired_link_from_source = Link(name="Link1", src=sensor, dst=microprocessor, latency=0, bandwidth=10e6, power_model=PowerModelLink(200e-6))
    wifi_link_to_server = Link(name="Link2", src=microprocessor, dst=server, latency=10, bandwidth=5e6, power_model=PowerModelLink(200e-9))
    infrastructure.add_link(wifi_link_to_server)
    infrastructure.add_link(wired_link_from_source)
    entities = infrastructure.nodes()+infrastructure.links()

    power_domain = PowerDomain(env, name="Power Domain 1", powered_infrastructure=entities,
                               start_time_str="17:00:00", update_interval=1)
    grid = GridPower(env, power_domain=power_domain, priority=5)
    solar_power = SolarPower(env, power_domain=power_domain, priority=0)
    power_domain.add_power_source(solar_power)
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
    orchestrator = SimpleOrchestrator(infrastructure, power_domain)
    orchestrator.place(application)

    # Early power meters when exploring isolated power measurements
    application_pm = PowerMeter(application, name="application_meter")
    infrastructure_pm = PowerMeter(infrastructure.nodes(), name="infrastructure_meter", measurement_interval=1)

    # Run simulation
    env.process(power_domain.run(env))
    env.process(application_pm.run(env))
    env.process(infrastructure_pm.run(env))
    env.run(until=120)  # run simulation for 10 seconds

    logger.info(f"Total application power usage: {float(PowerMeasurement.sum(application_pm.measurements))} Ws")
    logger.info(f"Total infrastructure power usage: {float(PowerMeasurement.sum(infrastructure_pm.measurements))} Ws")
    logger.info(f"Total carbon emitted: {power_domain.return_total_carbon_emissions()} gCo2")

    file_handler = FileHandler()
    filename = "Results.Json"
    file_handler.write_out_results(filename=filename, power_domain=power_domain)

    fig1 = file_handler.subplot_time_series_entities(power_domain, "Carbon Released", entities=entities)
    fig2 = file_handler.subplot_time_series_power_sources(power_domain, "Power Used",
                                                          power_sources=[solar_power, grid])
    fig3 = file_handler.subplot_time_series_power_sources(power_domain, "Power Available",
                                                          power_sources=[solar_power, grid])
    fig4 = file_handler.subplot_time_series_power_sources(power_domain, "Carbon Released",
                                                          power_sources=[solar_power, grid])

    figs = [fig1, fig2, fig3, fig4]
    main_fig = file_handler.aggregate_subplots(figs)
    file_handler.write_figure_to_file(main_fig, len(figs))
    main_fig.show()


class SimpleOrchestrator(Orchestrator):
    def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
        return self.infrastructure.node("node2")


if __name__ == '__main__':
    main()
