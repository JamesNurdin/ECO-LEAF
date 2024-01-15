import logging
import simpy
from src.extendedLeaf.application import Task, Application, SourceTask, ProcessingTask, SinkTask
from src.extendedLeaf.file_handler import FileHandler
from src.extendedLeaf.infrastructure import Node, Link, Infrastructure
from src.extendedLeaf.orchestrator import Orchestrator
from src.extendedLeaf.power import PowerModelNode, PowerMeasurement, PowerMeter, PowerModelLink, SolarPower, WindPower, \
    GridPower, PowerDomain, BatteryPower, PoweredInfrastructureDistributor

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')


def main():
    """
    Log Output:
        INFO	Placing Application(tasks=3):
        INFO	- SourceTask(id=0, cu=0.4) on Node('node1', cu=0/10).
        INFO	- ProcessingTask(id=1, cu=5) on Node('node2', cu=0/40).
        INFO	- SinkTask(id=2, cu=1) on Node('node3', cu=0/20).
        INFO	- DataFlow(bit_rate=1000) on [Link('node1' -> 'node2', bandwidth=0/30000000.0, latency=10)].
        INFO	- DataFlow(bit_rate=300) on [Link('node2' -> 'node3', bandwidth=0/50000000.0, latency=12)].
        DEBUG	0: application_meter: PowerMeasurement(dynamic=10.73W, static=20.00W)
        DEBUG	0: infrastructure_meter: PowerMeasurement(dynamic=65.73W, static=40.00W)
        DEBUG	1: application_meter: PowerMeasurement(dynamic=10.73W, static=20.00W)
        DEBUG	1: infrastructure_meter: PowerMeasurement(dynamic=65.73W, static=40.00W)
        DEBUG	2: application_meter: PowerMeasurement(dynamic=10.73W, static=20.00W)
        DEBUG	2: infrastructure_meter: PowerMeasurement(dynamic=65.73W, static=40.00W)
        ...
        DEBUG	147: application_meter: PowerMeasurement(dynamic=10.73W, static=20.00W)
        DEBUG	147: infrastructure_meter: PowerMeasurement(dynamic=65.73W, static=40.00W)
        DEBUG	148: application_meter: PowerMeasurement(dynamic=10.73W, static=20.00W)
        DEBUG	148: infrastructure_meter: PowerMeasurement(dynamic=65.73W, static=40.00W)
        DEBUG	149: application_meter: PowerMeasurement(dynamic=10.73W, static=20.00W)
        DEBUG	149: infrastructure_meter: PowerMeasurement(dynamic=65.73W, static=40.00W)
        INFO	Total application power usage: 4609.563000000004 Ws
        INFO	Total infrastructure power usage: 15859.499999999964 Ws
        INFO	Total carbon emitted: 24.922497796000034 gCo2
    """
    env = simpy.Environment()  # creating SimPy simulation environment
    infrastructure = Infrastructure()

    # Initializing infrastructure and workload
    node1 = Node("node1", cu=10, power_model=PowerModelNode(max_power=30, static_power=3))  # source
    node2 = Node("node2", cu=40, power_model=PowerModelNode(max_power=70, static_power=10))  # processing task
    node3 = Node("node3", cu=20, power_model=PowerModelNode(max_power=50, static_power=7))  # sink
    wifi_link_from_source = Link(name="Link 1", src=node1, dst=node2, latency=10, bandwidth=30e6, power_model=PowerModelLink(300e-9))
    wifi_link_to_sink = Link(name="Link 2", src=node2, dst=node3, latency=12, bandwidth=50e6, power_model=PowerModelLink(400e-9))
    all_entities = [node1,node2,node3,wifi_link_from_source,wifi_link_to_sink]

    infrastructure.add_link(wifi_link_to_sink)
    infrastructure.add_link(wifi_link_from_source)

    power_domain = PowerDomain(env, name="Power Domain 1",
                               start_time_str="15:00:00", update_interval=1, powered_infrastructure_distributor=
                               PoweredInfrastructureDistributor(static_powered_infrastructure=True))
    solar_power = SolarPower(env, power_domain=power_domain, priority=1, powered_infrastructure=[node1, node3, wifi_link_to_sink])
    battery_power = BatteryPower(env, power_domain=power_domain, priority=0, total_power_available=30,
                                 powered_infrastructure=[wifi_link_from_source,node2])
    power_domain.add_power_source(battery_power)
    power_domain.add_power_source(solar_power)

    events = [
        ("15:20:00", False, (battery_power.recharge_battery, [solar_power]))]
    power_domain.power_source_events = events

    # three nodes 1,2,3
    # #two Wi-Fi links between 1 -> 2 and 2 -> 3

    # Initialise three tasks
    source_task = SourceTask(cu=0.4, bound_node=node1)
    processing_task = ProcessingTask(cu=5)
    sink_task = SinkTask(cu=12, bound_node=node3)

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

    source_task_pm = PowerMeter(source_task, name="Source Task")
    processing_task_pm = PowerMeter(processing_task, name="Processing Task")
    sink_task_pm = PowerMeter(sink_task, name="Sink Task")

    # Run simulation
    env.process(power_domain.run(env))  # registering power metering process 2

    env.process(application_pm.run(env))  # registering power metering process 2
    env.process(infrastructure_pm.run(env))  # registering power metering process 2

    env.process(source_task_pm.run(env))  # registering power metering process 2
    env.process(processing_task_pm.run(env))  # registering power metering process 2
    env.process(sink_task_pm.run(env))  # registering power metering process 2

    env.run(until=150)

    logger.info(f"Total application power usage: {float(PowerMeasurement.sum(application_pm.measurements))} Ws")
    logger.info(f"Total infrastructure power usage: {float(PowerMeasurement.sum(infrastructure_pm.measurements))} Ws")
    logger.info(f"Total carbon emitted: {power_domain.return_total_carbon_emissions()} gCo2")

    file_handler = FileHandler()
    filename = "Results.Json"
    file_handler.write_out_results(filename=filename, power_domain=power_domain)

    fig1 = file_handler.subplot_time_series_entities(power_domain, "Carbon Released", events=events, entities=all_entities)
    fig2 = file_handler.subplot_time_series_entities(power_domain, "Power Used", events=events, entities=all_entities)
    fig3 = file_handler.subplot_time_series_power_sources(power_domain, "Power Used", events=events, power_sources=[solar_power, battery_power])
    fig4 = file_handler.subplot_time_series_power_meter(power_domain, power_meters=[source_task_pm, processing_task_pm, sink_task_pm], events=events)
    figs = [fig1, fig2, fig3,fig4]
    main_fig = file_handler.aggregate_subplots(figs)
    file_handler.write_figure_to_file(main_fig, len(figs))
    main_fig.show()


class SimpleOrchestrator(Orchestrator):
    def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
        return self.infrastructure.node("node2")


if __name__ == '__main__':
    main()
