import logging

import networkx as nx
import numpy as np
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
        INFO	- SinkTask(id=2, cu=12) on Node('node3', cu=0/20).
        INFO	- DataFlow(bit_rate=1000) on [Link('node1' -> 'node2', bandwidth=0/30000000.0, latency=10)].
        INFO	- DataFlow(bit_rate=300) on [Link('node2' -> 'node3', bandwidth=0/50000000.0, latency=12)].
        DEBUG	0: application_meter: PowerMeasurement(dynamic=34.38W, static=20.00W)
        DEBUG	0: infrastructure_meter: PowerMeasurement(dynamic=34.38W, static=20.00W)
        DEBUG	0: Source Task: PowerMeasurement(dynamic=1.08W, static=3.00W)
        DEBUG	0: Processing Task: PowerMeasurement(dynamic=7.50W, static=10.00W)
        DEBUG	0: Sink Task: PowerMeasurement(dynamic=25.80W, static=7.00W)
        DEBUG	1: application_meter: PowerMeasurement(dynamic=1.08W, static=3.00W)
        DEBUG	1: infrastructure_meter: PowerMeasurement(dynamic=26.88W, static=10.00W)
        DEBUG	1: Source Task: PowerMeasurement(dynamic=1.08W, static=3.00W)
        DEBUG	1: Processing Task: PowerMeasurement(dynamic=0.00W, static=0.00W)
        DEBUG	1: Sink Task: PowerMeasurement(dynamic=0.00W, static=0.00W)
        ...
        DEBUG	148: application_meter: PowerMeasurement(dynamic=1.08W, static=3.00W)
        DEBUG	148: infrastructure_meter: PowerMeasurement(dynamic=26.88W, static=10.00W)
        DEBUG	148: Source Task: PowerMeasurement(dynamic=1.08W, static=3.00W)
        DEBUG	148: Processing Task: PowerMeasurement(dynamic=0.00W, static=0.00W)
        DEBUG	148: Sink Task: PowerMeasurement(dynamic=0.00W, static=0.00W)
        DEBUG	149: application_meter: PowerMeasurement(dynamic=1.08W, static=3.00W)
        DEBUG	149: infrastructure_meter: PowerMeasurement(dynamic=26.88W, static=10.00W)
        DEBUG	149: Source Task: PowerMeasurement(dynamic=1.08W, static=3.00W)
        DEBUG	149: Processing Task: PowerMeasurement(dynamic=0.00W, static=0.00W)
        DEBUG	149: Sink Task: PowerMeasurement(dynamic=0.00W, static=0.00W)
        INFO	Total application power usage: 2825.244580000006 Ws
        INFO	Total infrastructure power usage: 6302.000000000013 Ws
        INFO	Total carbon emitted: 6.2369292893333075 gCo2

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

    events = [
        ("15:10:00", False, (orchestrator.place, [application1])),
        ("15:30:00", False, (battery_power.recharge_battery, [solar_power])),
        ("15:40:00", False, (orchestrator.place, [application2])),
        ("16:00:00", False, (battery_power.recharge_battery, [solar_power])),
        ("16:30:00", False, (application1.deallocate, [])),
        ("17:00:00", False, (battery_power.recharge_battery, [solar_power]))]
    power_domain.power_source_events = events

    # Early power meters when exploring isolated power measurements
    application1_pm = PowerMeter(application1, name="application_meter")
    application2_pm = PowerMeter(application2, name="application_meter")
    infrastructure_pm = PowerMeter(infrastructure.nodes(), name="infrastructure_meter", measurement_interval=1)

    # Run simulation
    env.process(power_domain.run(env))
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

    fig2 = file_handler.subplot_time_series_entities(power_domain, "Power Used", events=events, entities=all_entities)
    fig3 = file_handler.subplot_time_series_power_sources(power_domain, "Power Available", events=events, power_sources=[solar_power, battery_power])
    fig4 = file_handler.subplot_time_series_power_meter(power_domain, power_meters=[application1_pm,application2_pm,infrastructure_pm], events=events)
    figs = [fig2, fig3, fig4]
    main_fig = file_handler.aggregate_subplots(figs)
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
