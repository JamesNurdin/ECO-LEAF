import logging
import simpy
from src.extendedLeaf.application import Task, Application, SourceTask, ProcessingTask, SinkTask
from src.extendedLeaf.infrastructure import Node, Link, Infrastructure
from src.extendedLeaf.orchestrator import Orchestrator
from src.extendedLeaf.power import PowerModelNode, PowerMeasurement, PowerMeter, PowerModelLink, SolarPower, WindPower, \
    GridPower, PowerDomain, PowerSource, EntityDistributor

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s\t%(message)s')


def main():
    env = simpy.Environment()  # creating SimPy simulation environment
    infrastructure = Infrastructure()
    # Initializing infrastructure and workload
    node1 = Node("node1", cu=10, power_model=PowerModelNode(max_power=30, static_power=3))  # source
    node2 = Node("node2", cu=40, power_model=PowerModelNode(max_power=70, static_power=10))  # processing task
    node3 = Node("node3", cu=20, power_model=PowerModelNode(max_power=50, static_power=7))  # sink
    # three nodes 1,2,3
    # #two Wi-Fi links between 1 -> 2 and 2 -> 3
    wifi_link_from_source = Link("Link1", node1, node2, latency=10, bandwidth=30e6, power_model=PowerModelLink(300e-9))
    wifi_link_to_sink = Link("Link2", node2, node3, latency=12, bandwidth=50e6, power_model=PowerModelLink(400e-9))
    infrastructure.add_link(wifi_link_to_sink)
    infrastructure.add_link(wifi_link_from_source)

    power_domain = PowerDomain(env, name="Power Domain 1",
                               start_time_str="04:00:00", update_interval=1,
                               entity_distributor=EntityDistributor(static_entities=True))
    solar_power = SolarPower(env, power_domain=power_domain, priority=0, powered_entities=[node1, node2, node3])
    power_domain.add_power_source(solar_power)

    # Initialise three tasks
    source_task = SourceTask(cu=0.4, bound_node=node1)
    processing_task = ProcessingTask(cu=5)
    sink_task = SinkTask(cu=1, bound_node=node3)

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
    env.run(until=121)  # run simulation for 10 seconds

    logger.info(f"Total application power usage: {float(PowerMeasurement.sum(application_pm.measurements))} Ws")
    logger.info(f"Total infrastructure power usage: {float(PowerMeasurement.sum(infrastructure_pm.measurements))} Ws")
    logger.info(f"Total carbon emitted: {power_domain.return_total_carbon_emissions()} gCo2")


class SimpleOrchestrator(Orchestrator):
    def _processing_task_placement(self, processing_task: ProcessingTask, application: Application) -> Node:
        return self.infrastructure.node("node2")


if __name__ == '__main__':
    main()
