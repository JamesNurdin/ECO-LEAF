import logging
import simpy
from src.extendedLeaf.application import Task, Application, SourceTask, ProcessingTask, SinkTask
from src.extendedLeaf.file_handler import FileHandler
from src.extendedLeaf.infrastructure import Node, Link, Infrastructure
from src.extendedLeaf.orchestrator import Orchestrator
from src.extendedLeaf.power import PowerModelNode, PowerMeasurement, PowerMeter, PowerModelLink, SolarPower, WindPower, \
    GridPower, PowerDomain

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')


def main():
    env = simpy.Environment()  # creating SimPy simulation environment
    infrastructure = Infrastructure()

    # Initializing infrastructure and workload
    node1 = Node("node1", cu=10, power_model=PowerModelNode(max_power=30, static_power=3))  # source
    node2 = Node("node2", cu=40, power_model=PowerModelNode(max_power=70, static_power=10))  # processing task
    node3 = Node("node3", cu=20, power_model=PowerModelNode(max_power=50, static_power=7))  # sink
    node4 = Node("node4", cu=100, power_model=PowerModelNode(max_power=130, static_power=20))
    wifi_link_from_source = Link(name="Link 1", src=node1, dst=node2, latency=10, bandwidth=30e6, power_model=PowerModelLink(300e-9))
    wifi_link_to_sink = Link(name="Link 2", src=node2, dst=node3, latency=12, bandwidth=50e6, power_model=PowerModelLink(400e-9))
    wifi_link_to_node4 = Link(name="Link 3", src=node2, dst=node4, latency=12, bandwidth=50e6, power_model=PowerModelLink(400e-9))
    all_entities = [node1,node2,node3,node4,wifi_link_from_source,wifi_link_to_sink,wifi_link_to_node4]

    infrastructure.add_link(wifi_link_to_sink)
    infrastructure.add_link(wifi_link_from_source)
    infrastructure.add_link(wifi_link_to_node4)

    entities = infrastructure.nodes()+infrastructure.links()
    entities.remove(node4)

    power_domain = PowerDomain(env, name="Power Domain 1", powered_entities=entities,
                               start_time_str="19:00:00", update_interval=1)
    solar_power = SolarPower(env, power_domain=power_domain, priority=0)
    grid1 = GridPower(env, power_domain=power_domain, priority=5)
    wind_power = WindPower(env, power_domain=power_domain, priority=0)
    power_domain.add_power_source(wind_power)
    power_domain.add_power_source(grid1)
    events = [
        ("19:20:00", False, (power_domain.remove_power_source, [wind_power])),
        ("19:40:00", False, (power_domain.add_power_source, [solar_power])),
        ("20:30:00", False, (power_domain.add_entity, [node4])),
        ("21:15:00", False, (power_domain.remove_entity, [node4]))]
    power_domain.power_source_events = events

    # three nodes 1,2,3
    # #two Wi-Fi links between 1 -> 2 and 2 -> 3

    # Initialise three tasks
    source_task = SourceTask(cu=0.4, bound_node=node1)
    processing_task = ProcessingTask(cu=5)
    sink_task = SinkTask(cu=1, bound_node=node3)

    # Initialise and allocate a separate task for Node 4
    task = Task(cu=50)
    task.allocate(node4)

    # Build Application
    application = Application()
    application.add_task(source_task)
    application.add_task(processing_task, incoming_data_flows=[(source_task, 1000)])
    application.add_task(sink_task, incoming_data_flows=[(processing_task, 300)])

    # Place over Infrastructure
    orchestrator = SimpleOrchestrator(infrastructure)
    orchestrator.place(application)

    # Early power meters when exploring isolated power measurements
    application_pm = PowerMeter(application, name="application_meter")
    infrastructure_pm = PowerMeter(infrastructure.nodes(), name="infrastructure_meter", measurement_interval=1)

    env.process(power_domain.run(env))  # registering power metering process 2

    # Run simulation
    env.process(application_pm.run(env))  # registering power metering process 2
    env.process(infrastructure_pm.run(env))  # registering power metering process 2
    env.run(until=150)  # run simulation for 10 seconds

    logger.info(f"Total application power usage: {float(PowerMeasurement.sum(application_pm.measurements))} Ws")
    logger.info(f"Total infrastructure power usage: {float(PowerMeasurement.sum(infrastructure_pm.measurements))} Ws")
    logger.info(f"Total carbon emitted: {power_domain.return_total_carbon_emissions()} gCo2")

    #print(power_domain.captured_data)

    file_handler = FileHandler()
    filename = "Results.Json"
    file_handler.write_out_results(filename=filename, power_domain=power_domain)

    fig1 = file_handler.subplot_time_series_entities(power_domain, "Carbon Released", events=events, entities=all_entities)
    fig2 = file_handler.subplot_time_series_power_sources(power_domain, "Power Used", events=events, power_sources=[solar_power, grid1, wind_power])
    fig3 = file_handler.subplot_time_series_power_sources(power_domain, "Power Available", events=events, power_sources=[solar_power, grid1, wind_power])
    fig4 = file_handler.subplot_time_series_power_sources(power_domain, "Carbon Released", events=events, power_sources=[solar_power, grid1, wind_power])

    figs = [fig1, fig2, fig3, fig4]
    main_fig = file_handler.aggregate_subplots(figs)
    file_handler.write_figure_to_file(main_fig, len(figs))
    main_fig.show()


class SimpleOrchestrator(Orchestrator):
    def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
        return self.infrastructure.node("node2")


if __name__ == '__main__':
    main()
