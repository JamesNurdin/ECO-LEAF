import logging
import simpy
from extendedLeaf.application import Task, Application, SourceTask, ProcessingTask, SinkTask
from extendedLeaf.infrastructure import Node, Link, Infrastructure
from extendedLeaf.orchestrator import Orchestrator
from extendedLeaf.power import PowerModelNode, PowerMeasurement, PowerMeter, PowerModelLink, SolarPower, WindPower, \
    GridPower, PowerDomain, PowerSource, NodeDistributor

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')

def main():
    env = simpy.Environment()  # creating SimPy simulation environment
    # Initializing infrastructure and workload
    node1 = Node("node1", cu=10, power_model=PowerModelNode(max_power=30, static_power=3))  # source
    node2 = Node("node2", cu=40, power_model=PowerModelNode(max_power=70, static_power=10))  # processing task
    node3 = Node("node3", cu=20, power_model=PowerModelNode(max_power=50, static_power=7))  # sink
    node4 = Node("node4", cu=100, power_model=PowerModelNode(max_power=130, static_power=20))

    infrastructure = Infrastructure()

    power_domain = PowerDomain(env, name="Power Domain 1", associated_nodes=[node1, node2, node3],
                               start_time_str="19:00:00", update_interval=1,
                               node_distributor=NodeDistributor(custom_distribution_method))
    solar_power = SolarPower(env, power_domain=power_domain, priority=0)
    grid1 = GridPower(env, power_domain=power_domain, priority=5)
    wind_power = WindPower(env, power_domain=power_domain, priority=0)
    power_domain.add_power_source(wind_power)
    power_domain.add_power_source(grid1)
    events = [
        ("19:20:00", False, (power_domain.remove_power_source, [wind_power])),
        ("19:40:00", False, (power_domain.add_power_source, [solar_power])),
        ("20:00:00", False, (power_domain.add_node, [node4]))]
    power_domain.power_source_events = events

    # three nodes 1,2,3
    # #two Wi-Fi links between 1 -> 2 and 2 -> 3
    wifi_link_from_source = Link(node1, node2, latency=10, bandwidth=30e6, power_model=PowerModelLink(300e-9))
    wifi_link_to_sink = Link(node2, node3, latency=12, bandwidth=50e6, power_model=PowerModelLink(400e-9))
    wifi_link_to_node4 = Link(node2, node4, latency=12, bandwidth=50e6, power_model=PowerModelLink(400e-9))
    infrastructure.add_link(wifi_link_to_sink)
    infrastructure.add_link(wifi_link_from_source)
    infrastructure.add_link(wifi_link_to_node4)

    # Initialise three tasks
    source_task = SourceTask(cu=0.4, bound_node=node1)
    processing_task = ProcessingTask(cu=5)
    sink_task = SinkTask(cu=1, bound_node=node3)

    # Initialise and allocate a separate task for Node 4
    task = Task(cu=100)
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
    env.run(until=50)  # run simulation for 10 seconds

    logger.info(f"Total application power usage: {float(PowerMeasurement.sum(application_pm.measurements))} Ws")
    logger.info(f"Total infrastructure power usage: {float(PowerMeasurement.sum(infrastructure_pm.measurements))} Ws")
    logger.info(f"Total carbon emitted: {power_domain.return_total_carbon_emissions()} gCo2")


def custom_distribution_method(current_power_source: PowerSource, associated_nodes,update_interval):
    """Update renewable sources"""
    total_current_power = current_power_source.get_current_power()

    for node in associated_nodes:
        current_node_power_requirement = float(node.power_model.update_sensitive_measure(update_interval))

        """Check if node is currently being powered by the desired power source"""
        if node.power_model.power_source == current_power_source:
            if total_current_power < current_node_power_requirement:
                node.power_model.power_source = None
                current_power_source.remove_node(node)
            else:
                total_current_power = total_current_power - current_node_power_requirement
            continue

        """Check if node is currently unpowered"""
        if node.power_model.power_source is None and current_node_power_requirement < total_current_power:
            current_power_source.add_node(node)
            node.power_model.power_source = current_power_source
            total_current_power = total_current_power - current_node_power_requirement
            continue

class SimpleOrchestrator(Orchestrator):
    def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
        return self.infrastructure.node("node2")

if __name__ == '__main__':
    main()
